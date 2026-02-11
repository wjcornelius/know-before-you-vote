"""
Generate static JSON files for the frontend.
These files are committed to the repo and served as static data by Vercel.
No runtime API calls needed from the frontend.
"""
import json
from pathlib import Path
from typing import Dict, List

from pipeline.config import DATA_DIR
from pipeline.candidates.merge import build_candidate_id
from pipeline.classify.citations import generate_citation, generate_clean_citation


def publish_candidates(candidates: List[Dict]) -> Path:
    """
    Write candidates.json with all candidates and their district assignments.

    Args:
        candidates: List of merged candidate dicts

    Returns:
        Path to written file
    """
    output = []
    for c in candidates:
        output.append({
            "id": build_candidate_id(c),
            "name": c.get("name", ""),
            "party": c.get("party", ""),
            "state": c.get("state", ""),
            "district": c.get("district", ""),
            "office": c.get("office", ""),
            "incumbent": c.get("incumbent", False),
        })

    path = DATA_DIR / "candidates.json"
    path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    return path


def publish_connections(
    candidates: List[Dict],
    filtered_connections: Dict[str, Dict],
    classifications: Dict[str, Dict],
) -> Path:
    """
    Write connections.json with all verified connections and clean candidate records.

    Args:
        candidates: List of merged candidate dicts
        filtered_connections: Output from corroborate.filter_connections()
        classifications: Dict mapping candidate_key -> {"level": str, "reasoning": str}

    Returns:
        Path to written file
    """
    output = {}

    for candidate in candidates:
        cid = build_candidate_id(candidate)
        candidate_key = f"{candidate['name']}|{candidate.get('state', '')}|{candidate.get('office', '')}"

        conn_data = filtered_connections.get(candidate_key, {"has_connections": False, "connections": []})

        if conn_data["has_connections"]:
            # Build citations for each connection
            citations = []
            for conn in conn_data["connections"]:
                classification = classifications.get(candidate_key, {"level": "Contact", "reasoning": ""})

                citation = generate_citation(
                    person_name=candidate["name"],
                    connection_level=classification["level"],
                    confidence=conn["confidence"],
                    num_sources=conn["num_sources"],
                    evidence=conn["entity_data"].get("connections", []),
                    caveat=conn.get("caveat"),
                )
                citations.append(citation)

            output[cid] = {
                "has_connections": True,
                "citations": citations,
            }
        else:
            output[cid] = {
                "has_connections": False,
                "citations": [generate_clean_citation(candidate["name"])],
            }

    path = DATA_DIR / "connections.json"
    path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    return path


def publish_districts(district_mapping: Dict[str, Dict]) -> Path:
    """
    Write districts.json mapping zip codes to district info.

    Args:
        district_mapping: {zip_code: {"state": str, "district": str, ...}}

    Returns:
        Path to written file
    """
    path = DATA_DIR / "districts.json"
    path.write_text(json.dumps(district_mapping, indent=2), encoding="utf-8")
    return path


def publish_metadata() -> Path:
    """
    Write metadata.json with data freshness info and source URLs.
    """
    from datetime import datetime, timezone

    metadata = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "data_sources": [
            {
                "name": "DOJ Epstein Library",
                "url": "https://www.justice.gov/epstein",
                "description": "3.5 million pages released January 30, 2026",
            },
            {
                "name": "Epstein Doc Explorer",
                "url": "https://github.com/maxandrews/Epstein-doc-explorer",
                "description": "15,000+ relationships extracted from email corpus",
            },
            {
                "name": "LMSBAND Epstein Files DB",
                "url": "https://github.com/LMSBAND/epstein-files-db",
                "description": "NER entities from DOJ Datasets 8-12",
            },
            {
                "name": "SvetimFM Entity Analysis",
                "url": "https://github.com/SvetimFM/epstein-files-visualizations",
                "description": "68,798 documents with entity networks",
            },
            {
                "name": "phelix001 Epstein Network",
                "url": "https://github.com/phelix001/epstein-network",
                "description": "19,154 FOIA documents with categorized entities",
            },
            {
                "name": "ProPublica Congress API",
                "url": "https://www.propublica.org/datastore/api/propublica-congress-api",
                "description": "Current federal legislators",
            },
            {
                "name": "FEC API",
                "url": "https://api.open.fec.gov/developers/",
                "description": "Filed federal candidates",
            },
        ],
        "methodology": {
            "min_sources_to_display": 2,
            "fuzzy_match_threshold": 92,
            "ai_disambiguation": True,
            "connection_levels": ["Direct", "Contact", "Financial", "Institutional"],
        },
    }

    path = DATA_DIR / "metadata.json"
    path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return path
