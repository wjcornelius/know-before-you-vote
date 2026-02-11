"""
FEC API - Federal Election Commission candidate data.
Returns all filed candidates for federal races, including challengers.
https://api.open.fec.gov/developers/
"""
import requests
from typing import Dict, List

from pipeline.config import FEC_API_KEY


BASE_URL = "https://api.open.fec.gov/v1"


def get_candidates_by_state_and_office(
    state: str,
    office: str = "H",
    district: str = None,
    election_year: int = 2026,
    api_key: str = FEC_API_KEY,
) -> List[Dict]:
    """
    Get all filed candidates for a given state and office.

    Args:
        state: Two-letter state abbreviation
        office: "H" for House, "S" for Senate, "P" for President
        district: District number for House races (optional)
        election_year: Election year to search
        api_key: FEC API key

    Returns:
        List of candidate dicts
    """
    if not api_key:
        raise ValueError("FEC_API_KEY not set.")

    params = {
        "api_key": api_key,
        "state": state,
        "office": office,
        "election_year": election_year,
        "is_active_candidate": True,
        "sort": "name",
        "per_page": 100,
    }

    if district and office == "H":
        params["district"] = district.zfill(2)  # FEC uses 2-digit district codes

    candidates = []
    page = 1

    while True:
        params["page"] = page
        resp = requests.get(
            f"{BASE_URL}/candidates/",
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", [])
        if not results:
            break

        for c in results:
            candidates.append({
                "name": c.get("name", ""),
                "party": _normalize_party(c.get("party", "")),
                "state": state,
                "district": c.get("district", ""),
                "office": "U.S. Senate" if office == "S" else "U.S. House",
                "incumbent": c.get("incumbent_challenge", "") == "I",
                "fec_id": c.get("candidate_id", ""),
                "other_names": [],
            })

        # Check for more pages
        pagination = data.get("pagination", {})
        if page >= pagination.get("pages", 1):
            break
        page += 1

    return candidates


def _normalize_party(party_code: str) -> str:
    """Normalize FEC party codes to common abbreviations."""
    mapping = {
        "DEM": "D",
        "REP": "R",
        "LIB": "L",
        "GRE": "G",
        "IND": "I",
        "CON": "C",
    }
    return mapping.get(party_code.upper(), party_code)


def get_all_candidates_for_location(
    state: str,
    district: str = None,
    election_year: int = 2026,
    api_key: str = FEC_API_KEY,
) -> List[Dict]:
    """
    Get all filed federal candidates relevant to a location.

    Args:
        state: Two-letter state abbreviation
        district: Congressional district number (for House)
        election_year: Election year

    Returns:
        Combined list of Senate + House candidates
    """
    candidates = []

    # Senate candidates for the state
    try:
        senate = get_candidates_by_state_and_office(
            state, "S", election_year=election_year, api_key=api_key
        )
        candidates.extend(senate)
    except Exception:
        pass

    # House candidates for the district
    if district:
        try:
            house = get_candidates_by_state_and_office(
                state, "H", district=district, election_year=election_year, api_key=api_key
            )
            candidates.extend(house)
        except Exception:
            pass

    return candidates
