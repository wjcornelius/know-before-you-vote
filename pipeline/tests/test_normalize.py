"""
Tests for name normalization - the foundation of accurate cross-referencing.
Getting this wrong means either false accusations (matching wrong person)
or missed connections (failing to match a known connection).
"""
import pytest

from pipeline.crossref.normalize import (
    generate_name_variants,
    names_match,
    normalize_name,
)


class TestNormalizeName:
    """Test basic name normalization."""

    def test_lowercase(self):
        assert normalize_name("John Smith") == "john smith"

    def test_strip_whitespace(self):
        assert normalize_name("  John  Smith  ") == "john smith"

    def test_strip_senator_title(self):
        assert normalize_name("Sen. John Smith") == "john smith"

    def test_strip_representative_title(self):
        assert normalize_name("Rep. Jane Doe") == "jane doe"

    def test_strip_honorable(self):
        assert normalize_name("Hon. John Smith") == "john smith"

    def test_strip_dr(self):
        assert normalize_name("Dr. Jane Smith") == "jane smith"

    def test_strip_suffix_jr(self):
        assert normalize_name("John Smith Jr.") == "john smith"

    def test_strip_suffix_iii(self):
        assert normalize_name("John Smith III") == "john smith"

    def test_strip_party_designation(self):
        assert normalize_name("John Smith (D-CA)") == "john smith"

    def test_expand_nickname_bill(self):
        assert normalize_name("Bill Clinton") == "william clinton"

    def test_expand_nickname_bob(self):
        assert normalize_name("Bob Menendez") == "robert menendez"

    def test_expand_nickname_ted(self):
        assert normalize_name("Ted Cruz") == "edward cruz"

    def test_expand_nickname_dick(self):
        assert normalize_name("Dick Cheney") == "richard cheney"

    def test_expand_nickname_mike(self):
        assert normalize_name("Mike Johnson") == "michael johnson"

    def test_expand_nickname_jim(self):
        assert normalize_name("Jim Jordan") == "james jordan"

    def test_expand_nickname_chuck(self):
        assert normalize_name("Chuck Schumer") == "charles schumer"

    def test_no_nickname_for_formal(self):
        """Formal names should not be changed."""
        assert normalize_name("William Clinton") == "william clinton"

    def test_empty_string(self):
        assert normalize_name("") == ""

    def test_none(self):
        assert normalize_name(None) == ""

    def test_remove_periods_from_initials(self):
        assert normalize_name("J.F. Kennedy") == "j f kennedy"


class TestGenerateNameVariants:
    """Test variant generation for fuzzy matching."""

    def test_basic_variants(self):
        variants = generate_name_variants("Bill Clinton")
        assert "william clinton" in variants

    def test_first_last_from_three_parts(self):
        variants = generate_name_variants("William Jefferson Clinton")
        assert "william clinton" in variants

    def test_includes_normalized_form(self):
        variants = generate_name_variants("Sen. Robert Smith Jr.")
        assert "robert smith" in variants

    def test_reverse_nickname(self):
        """Should generate common nicknames from formal names."""
        variants = generate_name_variants("William Clinton")
        assert "bill clinton" in variants

    def test_empty_returns_empty(self):
        assert generate_name_variants("") == []


class TestNamesMatch:
    """Test name matching - critical for preventing false positives/negatives."""

    def test_exact_match(self):
        assert names_match("John Smith", "John Smith") is True

    def test_case_insensitive(self):
        assert names_match("john smith", "JOHN SMITH") is True

    def test_nickname_match(self):
        assert names_match("Bill Clinton", "William Clinton") is True

    def test_title_stripped(self):
        assert names_match("Sen. John Smith", "John Smith") is True

    def test_suffix_stripped(self):
        assert names_match("John Smith Jr.", "John Smith") is True

    def test_different_people(self):
        assert names_match("John Smith", "Jane Doe") is False

    def test_similar_but_different(self):
        """Different last names should not match even with same first name."""
        assert names_match("John Smith", "John Jones") is False

    def test_empty_strings(self):
        assert names_match("", "") is False

    def test_partial_name_no_match(self):
        """First name only should not match a full name."""
        assert names_match("John", "John Smith") is False


class TestRealWorldCases:
    """Test with real politician names that might appear in both databases."""

    def test_bill_clinton(self):
        assert names_match("Bill Clinton", "William Jefferson Clinton") is True

    def test_bob_menendez(self):
        assert names_match("Bob Menendez", "Robert Menendez") is True

    def test_different_john_kennedys(self):
        """Two different people named John Kennedy should match on name alone.
        AI disambiguation (Phase B) handles telling them apart."""
        assert names_match("John Kennedy", "John F. Kennedy") is True

    def test_chuck_grassley(self):
        assert names_match("Chuck Grassley", "Charles Grassley") is True
