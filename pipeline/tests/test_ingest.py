"""
Tests for entity ingestion and merging.
These tests use synthetic data - they don't download real databases.
"""
import pytest

from pipeline.ingest.common import (
    Entity,
    EntityConnection,
    merge_entity_databases,
)


class TestEntityMerge:
    """Test the critical merge logic that combines entities across databases."""

    def test_merge_two_databases(self):
        """Entities from different sources should combine."""
        db1 = {
            "John Smith": Entity(
                name="John Smith",
                sources=["source_a"],
                connections=[EntityConnection("test", "source_a", ["doc1"])],
                categories=["political"],
                total_document_mentions=5,
            )
        }
        db2 = {
            "John Smith": Entity(
                name="John Smith",
                sources=["source_b"],
                connections=[EntityConnection("test2", "source_b", ["doc2"])],
                categories=["business"],
                total_document_mentions=3,
            )
        }

        merged = merge_entity_databases(db1, db2)

        # Should have one entry (merged)
        assert len(merged) == 1
        entity = list(merged.values())[0]
        assert set(entity.sources) == {"source_a", "source_b"}
        assert len(entity.connections) == 2
        assert set(entity.categories) == {"political", "business"}
        assert entity.total_document_mentions == 8

    def test_merge_normalizes_names(self):
        """'Bill Smith' and 'William Smith' should merge."""
        db1 = {
            "Bill Smith": Entity(
                name="Bill Smith",
                sources=["source_a"],
                connections=[],
                total_document_mentions=3,
            )
        }
        db2 = {
            "William Smith": Entity(
                name="William Smith",
                sources=["source_b"],
                connections=[],
                total_document_mentions=5,
            )
        }

        merged = merge_entity_databases(db1, db2)
        assert len(merged) == 1
        entity = list(merged.values())[0]
        assert len(entity.sources) == 2
        # One of the names should be an alias
        assert "William Smith" in entity.aliases or "Bill Smith" in entity.aliases

    def test_merge_preserves_separate_people(self):
        """Different people should NOT merge."""
        db1 = {
            "John Smith": Entity(
                name="John Smith",
                sources=["source_a"],
                connections=[],
                total_document_mentions=3,
            )
        }
        db2 = {
            "Jane Doe": Entity(
                name="Jane Doe",
                sources=["source_b"],
                connections=[],
                total_document_mentions=5,
            )
        }

        merged = merge_entity_databases(db1, db2)
        assert len(merged) == 2

    def test_merge_three_databases(self):
        """Entity appearing in 3 databases should have 3 sources."""
        db1 = {"Test Person": Entity(name="Test Person", sources=["a"], connections=[], total_document_mentions=1)}
        db2 = {"Test Person": Entity(name="Test Person", sources=["b"], connections=[], total_document_mentions=2)}
        db3 = {"Test Person": Entity(name="Test Person", sources=["c"], connections=[], total_document_mentions=3)}

        merged = merge_entity_databases(db1, db2, db3)
        entity = list(merged.values())[0]
        assert len(entity.sources) == 3
        assert entity.total_document_mentions == 6

    def test_merge_empty_databases(self):
        """Merging empty databases should return empty."""
        merged = merge_entity_databases({}, {})
        assert len(merged) == 0

    def test_merge_single_database(self):
        """Single database should pass through unchanged."""
        db = {
            "Test": Entity(name="Test", sources=["a"], connections=[], total_document_mentions=1)
        }
        merged = merge_entity_databases(db)
        assert len(merged) == 1

    def test_duplicate_source_not_added(self):
        """Same source appearing twice should only be listed once."""
        db1 = {"Test": Entity(name="Test", sources=["source_a"], connections=[], total_document_mentions=1)}
        db2 = {"Test": Entity(name="Test", sources=["source_a"], connections=[], total_document_mentions=2)}

        merged = merge_entity_databases(db1, db2)
        entity = list(merged.values())[0]
        assert entity.sources == ["source_a"]  # Not ["source_a", "source_a"]

    def test_merge_with_titles(self):
        """'Sen. John Smith' and 'John Smith' should merge."""
        db1 = {
            "Sen. John Smith": Entity(
                name="Sen. John Smith",
                sources=["a"],
                connections=[],
                total_document_mentions=1,
            )
        }
        db2 = {
            "John Smith": Entity(
                name="John Smith",
                sources=["b"],
                connections=[],
                total_document_mentions=1,
            )
        }

        merged = merge_entity_databases(db1, db2)
        assert len(merged) == 1
        entity = list(merged.values())[0]
        assert len(entity.sources) == 2


class TestEntityToDict:
    """Test serialization."""

    def test_entity_to_dict(self):
        entity = Entity(
            name="Test Person",
            sources=["source_a", "source_b"],
            connections=[
                EntityConnection("desc1", "source_a", ["doc1"], "raw text", "email"),
            ],
            categories=["political"],
            aliases=["T. Person"],
            total_document_mentions=10,
        )

        d = entity.to_dict()
        assert d["name"] == "Test Person"
        assert len(d["sources"]) == 2
        assert len(d["connections"]) == 1
        assert d["connections"][0]["description"] == "desc1"
        assert d["connections"][0]["source_db"] == "source_a"
        assert d["total_document_mentions"] == 10
