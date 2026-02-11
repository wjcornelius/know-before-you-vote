"""
Merge candidate data from multiple sources (ProPublica + FEC) into a unified list.
Deduplicates incumbents that appear in both sources.
"""
from typing import Dict, List

from pipeline.crossref.normalize import normalize_name


def merge_candidate_lists(*candidate_lists: List[Dict]) -> List[Dict]:
    """
    Merge multiple candidate lists, deduplicating by normalized name + office.

    Args:
        *candidate_lists: Variable number of candidate lists to merge

    Returns:
        Deduplicated list of candidates
    """
    seen = {}  # key: (normalized_name, state, office) -> candidate dict

    for clist in candidate_lists:
        for candidate in clist:
            name_norm = normalize_name(candidate.get("name", ""))
            state = candidate.get("state", "").upper()
            office = candidate.get("office", "")

            key = (name_norm, state, office)

            if key not in seen:
                seen[key] = candidate.copy()
            else:
                # Merge: prefer data from the source that has more fields
                existing = seen[key]

                # Fill in missing fields from new source
                if not existing.get("fec_id") and candidate.get("fec_id"):
                    existing["fec_id"] = candidate["fec_id"]
                if not existing.get("propublica_id") and candidate.get("propublica_id"):
                    existing["propublica_id"] = candidate["propublica_id"]
                if not existing.get("district") and candidate.get("district"):
                    existing["district"] = candidate["district"]

                # Collect alternate names
                other_names = set(existing.get("other_names", []))
                if candidate.get("name") != existing.get("name"):
                    other_names.add(candidate["name"])
                existing["other_names"] = list(other_names)

    return list(seen.values())


def build_candidate_id(candidate: Dict) -> str:
    """
    Generate a stable, unique ID for a candidate (used in URLs).

    Args:
        candidate: Candidate dict

    Returns:
        URL-safe string ID like "ca-22-jane-smith"
    """
    state = candidate.get("state", "xx").lower()
    district = candidate.get("district", "")
    name = normalize_name(candidate.get("name", "unknown"))

    # Replace spaces with hyphens
    name_slug = name.replace(" ", "-")

    if candidate.get("office", "").lower() == "u.s. senate":
        return f"{state}-senate-{name_slug}"
    elif district:
        return f"{state}-{district}-{name_slug}"
    else:
        return f"{state}-{name_slug}"
