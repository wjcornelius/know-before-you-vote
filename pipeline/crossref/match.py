"""
Two-phase candidate-to-entity matching:
  Phase A: Fuzzy string matching with high threshold
  Phase B: AI disambiguation to confirm identity
"""
import json
import os
from typing import Dict, List, Optional

from thefuzz import fuzz

from pipeline.config import (
    ANTHROPIC_API_KEY,
    FUZZY_MATCH_THRESHOLD,
)
from pipeline.crossref.normalize import generate_name_variants, normalize_name


def fuzzy_match_candidate(
    candidate: Dict,
    entity_db: Dict[str, Dict],
    threshold: int = FUZZY_MATCH_THRESHOLD,
) -> List[Dict]:
    """
    Phase A: Find potential entity matches for a candidate using fuzzy string matching.

    Args:
        candidate: Dict with at least 'name', 'state', 'office' keys
        entity_db: Unified entity database {normalized_name: {sources, connections, ...}}
        threshold: Minimum fuzzywuzzy score (default 92)

    Returns:
        List of potential matches: [{entity_name, score, entity_data}]
    """
    candidate_variants = generate_name_variants(candidate["name"])
    matches = []
    seen_entities = set()

    for entity_name, entity_data in entity_db.items():
        if entity_name in seen_entities:
            continue

        entity_norm = normalize_name(entity_name)
        if not entity_norm:
            continue

        best_score = 0
        for variant in candidate_variants:
            # Try token_sort_ratio (handles word order differences)
            score = fuzz.token_sort_ratio(variant, entity_norm)
            best_score = max(best_score, score)

            # Also try against entity's own variants if available
            entity_aliases = entity_data.get("aliases", [])
            for alias in entity_aliases:
                alias_norm = normalize_name(alias)
                score = fuzz.token_sort_ratio(variant, alias_norm)
                best_score = max(best_score, score)

        if best_score >= threshold:
            seen_entities.add(entity_name)
            matches.append({
                "entity_name": entity_name,
                "score": best_score,
                "entity_data": entity_data,
            })

    # Sort by score descending
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches


def ai_disambiguate(
    candidate: Dict,
    entity_name: str,
    entity_data: Dict,
    api_key: str = ANTHROPIC_API_KEY,
) -> str:
    """
    Phase B: Use Claude Haiku to determine if a candidate and entity are the same person.

    Args:
        candidate: Dict with 'name', 'state', 'district', 'office', 'party', etc.
        entity_name: Name as it appears in Epstein documents
        entity_data: Dict with connections, source documents, categories

    Returns:
        "YES", "NO", or "UNCERTAIN"
    """
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set. Cannot perform AI disambiguation.")

    import anthropic

    client = anthropic.Anthropic(api_key=api_key)

    # Build context about the entity from documents
    entity_context_parts = []
    for conn in entity_data.get("connections", [])[:10]:  # Limit to 10 for token efficiency
        desc = conn.get("description", "")
        raw = conn.get("raw_text", "")[:500]  # Truncate long text
        source = conn.get("source_db", "unknown")
        if desc:
            entity_context_parts.append(f"[{source}] {desc}")
        elif raw:
            entity_context_parts.append(f"[{source}] {raw}")

    entity_context = "\n".join(entity_context_parts) if entity_context_parts else "No detailed context available."
    categories = ", ".join(entity_data.get("categories", ["unknown"]))

    prompt = f"""You are verifying whether a political candidate and a person named in Epstein-related documents are the same individual.

CANDIDATE:
- Name: {candidate.get('name', 'Unknown')}
- Office: {candidate.get('office', 'Unknown')}
- State: {candidate.get('state', 'Unknown')}
- District: {candidate.get('district', 'N/A')}
- Party: {candidate.get('party', 'Unknown')}
- Incumbent: {candidate.get('incumbent', 'Unknown')}
- FEC ID: {candidate.get('fec_id', 'N/A')}

PERSON IN EPSTEIN DOCUMENTS:
- Name as it appears: {entity_name}
- Categories: {categories}
- Document context:
{entity_context}

QUESTION: Based on the information above, is the candidate the SAME PERSON as the individual named in the Epstein documents?

Consider:
- Do the names match (accounting for nicknames, middle names, suffixes)?
- Does the geographic/professional context match (state, career, time period)?
- Could this be a different person who happens to share the same name?

Respond with exactly one word: YES, NO, or UNCERTAIN.
- YES: You are confident they are the same person.
- NO: You are confident they are different people (name collision, wrong state/era, etc.)
- UNCERTAIN: Not enough information to determine. (Treated as NO for safety.)"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=10,
        messages=[{"role": "user", "content": prompt}],
    )

    answer = response.content[0].text.strip().upper()

    # Only accept exact YES
    if answer == "YES":
        return "YES"
    elif answer == "NO":
        return "NO"
    else:
        return "UNCERTAIN"


def match_candidates_to_entities(
    candidates: List[Dict],
    entity_db: Dict[str, Dict],
    use_ai: bool = True,
) -> Dict[str, List[Dict]]:
    """
    Run the full two-phase matching pipeline.

    Args:
        candidates: List of candidate dicts
        entity_db: Unified entity database
        use_ai: Whether to run Phase B (AI disambiguation). Set False for testing.

    Returns:
        Dict mapping candidate name -> list of confirmed entity matches
    """
    results = {}

    for candidate in candidates:
        candidate_key = f"{candidate['name']}|{candidate.get('state', '')}|{candidate.get('office', '')}"

        # Phase A: Fuzzy matching
        fuzzy_matches = fuzzy_match_candidate(candidate, entity_db)

        if not fuzzy_matches:
            results[candidate_key] = []
            continue

        confirmed = []
        for match in fuzzy_matches:
            if use_ai:
                # Phase B: AI disambiguation
                verdict = ai_disambiguate(candidate, match["entity_name"], match["entity_data"])
                if verdict == "YES":
                    confirmed.append(match)
            else:
                # Without AI, only accept very high fuzzy scores (98+)
                if match["score"] >= 98:
                    confirmed.append(match)

        results[candidate_key] = confirmed

    return results
