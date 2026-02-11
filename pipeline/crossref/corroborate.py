"""
Multi-source corroboration: only connections verified by 2+ independent sources are displayed.
This is the quality gate that replaces human curation.
"""
from typing import Dict, List, Optional

from pipeline.config import HIGH_CONFIDENCE_SOURCES, MIN_SOURCES_TO_DISPLAY


def corroborate_connection(
    entity_data: Dict,
) -> Dict:
    """
    Evaluate a matched entity's evidence across independent sources.

    Args:
        entity_data: Entity dict with 'sources' list and 'connections' list

    Returns:
        Dict with:
          - display: bool (whether to show this connection)
          - confidence: "HIGH", "MEDIUM", or None
          - num_sources: int
          - evidence_types: set of distinct evidence types across sources
          - caveat: optional string caveat for MEDIUM confidence
    """
    sources = set(entity_data.get("sources", []))
    num_sources = len(sources)

    # Count distinct evidence types across sources
    evidence_types = set()
    for conn in entity_data.get("connections", []):
        etype = conn.get("evidence_type", conn.get("description", ""))
        if etype:
            evidence_types.add(etype.lower()[:50])  # Normalize and truncate

    # Apply thresholds
    if num_sources >= HIGH_CONFIDENCE_SOURCES:
        return {
            "display": True,
            "confidence": "HIGH",
            "num_sources": num_sources,
            "evidence_types": evidence_types,
            "caveat": None,
        }
    elif num_sources >= MIN_SOURCES_TO_DISPLAY:
        return {
            "display": True,
            "confidence": "MEDIUM",
            "num_sources": num_sources,
            "evidence_types": evidence_types,
            "caveat": "Based on limited documentation from {n} independent sources.".format(
                n=num_sources
            ),
        }
    else:
        return {
            "display": False,
            "confidence": None,
            "num_sources": num_sources,
            "evidence_types": evidence_types,
            "caveat": None,
        }


def filter_connections(
    matched_results: Dict[str, List[Dict]],
) -> Dict[str, Dict]:
    """
    Apply corroboration filter to all matched results.

    Args:
        matched_results: Output from match.match_candidates_to_entities()
            {candidate_key: [list of confirmed entity matches]}

    Returns:
        Dict of displayable connections:
        {candidate_key: {
            "has_connections": bool,
            "connections": [{entity_name, confidence, num_sources, evidence_types, caveat, entity_data}],
        }}
    """
    filtered = {}

    for candidate_key, matches in matched_results.items():
        displayable = []

        for match in matches:
            entity_data = match.get("entity_data", {})
            result = corroborate_connection(entity_data)

            if result["display"]:
                displayable.append({
                    "entity_name": match["entity_name"],
                    "confidence": result["confidence"],
                    "num_sources": result["num_sources"],
                    "evidence_types": list(result["evidence_types"]),
                    "caveat": result["caveat"],
                    "entity_data": entity_data,
                })

        filtered[candidate_key] = {
            "has_connections": len(displayable) > 0,
            "connections": displayable,
        }

    return filtered
