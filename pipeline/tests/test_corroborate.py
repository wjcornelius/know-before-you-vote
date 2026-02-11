"""
Tests for multi-source corroboration - the quality gate that prevents false positives.
This is the most important safety mechanism in the system.
"""
import pytest

from pipeline.crossref.corroborate import corroborate_connection, filter_connections


class TestCorroborateConnection:
    """Test the corroboration logic that decides what gets displayed."""

    def test_three_sources_high_confidence(self):
        """3+ sources = HIGH confidence, displayed."""
        entity = {
            "sources": ["maxandrews", "lmsband", "phelix"],
            "connections": [
                {"description": "flight log", "source_db": "maxandrews"},
                {"description": "email mention", "source_db": "lmsband"},
                {"description": "network connection", "source_db": "phelix"},
            ],
        }
        result = corroborate_connection(entity)
        assert result["display"] is True
        assert result["confidence"] == "HIGH"
        assert result["num_sources"] == 3
        assert result["caveat"] is None

    def test_two_sources_medium_confidence(self):
        """2 sources = MEDIUM confidence, displayed with caveat."""
        entity = {
            "sources": ["maxandrews", "lmsband"],
            "connections": [
                {"description": "flight log", "source_db": "maxandrews"},
                {"description": "email mention", "source_db": "lmsband"},
            ],
        }
        result = corroborate_connection(entity)
        assert result["display"] is True
        assert result["confidence"] == "MEDIUM"
        assert result["num_sources"] == 2
        assert result["caveat"] is not None
        assert "limited documentation" in result["caveat"]

    def test_one_source_not_displayed(self):
        """1 source = NOT displayed. This is critical for preventing false positives."""
        entity = {
            "sources": ["maxandrews"],
            "connections": [
                {"description": "email mention", "source_db": "maxandrews"},
            ],
        }
        result = corroborate_connection(entity)
        assert result["display"] is False
        assert result["confidence"] is None

    def test_zero_sources_not_displayed(self):
        """0 sources = NOT displayed."""
        entity = {
            "sources": [],
            "connections": [],
        }
        result = corroborate_connection(entity)
        assert result["display"] is False

    def test_duplicate_source_counts_once(self):
        """Same source appearing twice should only count once."""
        entity = {
            "sources": ["maxandrews", "maxandrews"],
            "connections": [
                {"description": "email 1", "source_db": "maxandrews"},
                {"description": "email 2", "source_db": "maxandrews"},
            ],
        }
        result = corroborate_connection(entity)
        assert result["display"] is False  # Only 1 unique source
        assert result["num_sources"] == 1

    def test_evidence_types_tracked(self):
        """Different evidence types across sources strengthen corroboration."""
        entity = {
            "sources": ["maxandrews", "lmsband", "phelix"],
            "connections": [
                {"description": "flight log entry", "source_db": "maxandrews"},
                {"description": "email correspondence", "source_db": "lmsband"},
                {"description": "phone record", "source_db": "phelix"},
            ],
        }
        result = corroborate_connection(entity)
        assert len(result["evidence_types"]) == 3


class TestFilterConnections:
    """Test the full filter pipeline."""

    def test_mixed_results(self):
        """Some candidates have displayable connections, some don't."""
        matched = {
            "Jane Doe|CA|House": [
                {
                    "entity_name": "Jane Doe",
                    "entity_data": {
                        "sources": ["maxandrews", "lmsband", "phelix"],
                        "connections": [{"description": "test"}],
                    },
                }
            ],
            "John Smith|TX|Senate": [
                {
                    "entity_name": "John Smith",
                    "entity_data": {
                        "sources": ["maxandrews"],  # Only 1 source - should be filtered
                        "connections": [{"description": "test"}],
                    },
                }
            ],
            "Bob Jones|FL|House": [],  # No matches at all
        }

        filtered = filter_connections(matched)

        # Jane Doe: 3 sources, should display
        assert filtered["Jane Doe|CA|House"]["has_connections"] is True
        assert len(filtered["Jane Doe|CA|House"]["connections"]) == 1

        # John Smith: 1 source, should NOT display
        assert filtered["John Smith|TX|Senate"]["has_connections"] is False
        assert len(filtered["John Smith|TX|Senate"]["connections"]) == 0

        # Bob Jones: no matches, no connections
        assert filtered["Bob Jones|FL|House"]["has_connections"] is False

    def test_clean_candidate(self):
        """A candidate with no entity matches should show as clean."""
        matched = {"Clean Candidate|NY|House": []}
        filtered = filter_connections(matched)
        assert filtered["Clean Candidate|NY|House"]["has_connections"] is False
        assert filtered["Clean Candidate|NY|House"]["connections"] == []
