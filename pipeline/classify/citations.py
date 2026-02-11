"""
Generate structured citations with links to primary source documents.
Every displayed connection must trace back to a verifiable public record.
"""
from typing import Dict, List, Optional


# Known DOJ Epstein Library base URLs by dataset
DOJ_BASE_URLS = {
    "DS01": "https://www.justice.gov/epstein/dataset-01",
    "DS02": "https://www.justice.gov/epstein/dataset-02",
    "DS03": "https://www.justice.gov/epstein/dataset-03",
    "DS04": "https://www.justice.gov/epstein/dataset-04",
    "DS05": "https://www.justice.gov/epstein/dataset-05",
    "DS06": "https://www.justice.gov/epstein/dataset-06",
    "DS07": "https://www.justice.gov/epstein/dataset-07",
    "DS08": "https://www.justice.gov/epstein/dataset-08",
    "DS09": "https://www.justice.gov/epstein/dataset-09",
    "DS10": "https://www.justice.gov/epstein/dataset-10",
    "DS11": "https://www.justice.gov/epstein/dataset-11",
    "DS12": "https://www.justice.gov/epstein/dataset-12",
}


def build_document_url(document_id: str, source_db: str) -> Optional[str]:
    """
    Attempt to construct a URL to the primary source document.

    Args:
        document_id: The document identifier from the source database
        source_db: Which source database this came from

    Returns:
        URL string or None if we can't construct one
    """
    if not document_id:
        return None

    # Try to match DOJ dataset pattern (e.g., "DOJ-DS10-00234")
    doc_upper = document_id.upper()
    for ds_key, base_url in DOJ_BASE_URLS.items():
        if ds_key in doc_upper:
            return f"{base_url}#{document_id}"

    # For LMSBAND source, documents come from DOJ datasets 8-12
    if source_db == "lmsband":
        return f"https://www.justice.gov/epstein#{document_id}"

    # For maxandrews source, documents are from House Oversight releases
    if source_db == "maxandrews":
        return f"https://oversight.house.gov/release/epstein-records#{document_id}"

    # Generic DOJ library link as fallback
    return f"https://www.justice.gov/epstein#{document_id}"


def generate_citation(
    person_name: str,
    connection_level: str,
    confidence: str,
    num_sources: int,
    evidence: List[Dict],
    caveat: Optional[str] = None,
) -> Dict:
    """
    Generate a complete, structured citation for a verified connection.

    Args:
        person_name: The connected person's name
        connection_level: Direct, Contact, Financial, or Institutional
        confidence: HIGH or MEDIUM
        num_sources: Number of independent corroborating sources
        evidence: List of evidence dicts from all sources
        caveat: Optional caveat text for MEDIUM confidence

    Returns:
        Structured citation dict ready for frontend display
    """
    # Build evidence items with source links
    evidence_items = []
    for ev in evidence:
        doc_id = ev.get("document_id", "")
        source_db = ev.get("source_db", "")
        doc_url = build_document_url(doc_id, source_db)

        evidence_items.append({
            "source_db": source_db,
            "document_id": doc_id,
            "document_url": doc_url,
            "relevant_text": ev.get("raw_text", ev.get("description", ""))[:500],
            "what_it_shows": ev.get("description", "Document mentions this individual"),
        })

    # Generate summary sentence
    source_types = set()
    for ev in evidence:
        desc = ev.get("description", "").lower()
        if "flight" in desc:
            source_types.add("flight logs")
        elif "email" in desc:
            source_types.add("email correspondence")
        elif "donation" in desc or "fec" in desc or "campaign" in desc:
            source_types.add("campaign finance records")
        elif "testimony" in desc or "victim" in desc:
            source_types.add("testimony")
        elif "phone" in desc:
            source_types.add("phone records")
        elif "photo" in desc:
            source_types.add("photographs")
        else:
            source_types.add("documents")

    source_list = ", ".join(sorted(source_types))
    summary = f"Documented in {source_list} across {num_sources} independent databases"

    return {
        "person_name": person_name,
        "summary": summary,
        "level": connection_level,
        "confidence": confidence,
        "num_sources": num_sources,
        "evidence": evidence_items,
        "caveat": caveat,
    }


def generate_clean_citation(candidate_name: str) -> Dict:
    """
    Generate a citation for a candidate with NO documented connections.
    Clean candidates deserve explicit recognition.

    Args:
        candidate_name: The candidate's name

    Returns:
        Structured "no connections" citation
    """
    return {
        "person_name": candidate_name,
        "summary": "No documented connections found in available records",
        "level": "None found",
        "confidence": None,
        "num_sources": 0,
        "evidence": [],
        "caveat": None,
        "databases_searched": [
            "DOJ Epstein Library",
            "Epstein Doc Explorer (email corpus)",
            "LMSBAND (DOJ Datasets 8-12)",
            "SvetimFM Entity Analysis",
            "phelix001 Epstein Network",
        ],
    }
