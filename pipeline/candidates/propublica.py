"""
ProPublica Congress API - free API for current federal legislators.
Returns members of Congress by state/district.
https://www.propublica.org/datastore/api/propublica-congress-api
"""
import requests
from typing import Dict, List

from pipeline.config import PROPUBLICA_API_KEY


BASE_URL = "https://api.propublica.org/congress/v1"


def get_members_by_state(
    state: str,
    chamber: str = "senate",
    api_key: str = PROPUBLICA_API_KEY,
) -> List[Dict]:
    """
    Get current members of Congress for a state.

    Args:
        state: Two-letter state abbreviation (e.g., "CA")
        chamber: "senate" or "house"
        api_key: ProPublica API key

    Returns:
        List of member dicts with name, party, district, etc.
    """
    if not api_key:
        raise ValueError("PROPUBLICA_API_KEY not set.")

    url = f"{BASE_URL}/members/{chamber}/{state}/current.json"
    resp = requests.get(
        url,
        headers={"X-API-Key": api_key},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    members = []
    for member in data.get("results", []):
        members.append({
            "name": f"{member.get('first_name', '')} {member.get('last_name', '')}".strip(),
            "party": member.get("party", ""),
            "state": state,
            "district": member.get("district", ""),
            "office": "U.S. Senate" if chamber == "senate" else "U.S. House",
            "incumbent": True,
            "propublica_id": member.get("id", ""),
            "other_names": [],
        })

    return members


def get_house_member_by_district(
    state: str,
    district: str,
    api_key: str = PROPUBLICA_API_KEY,
) -> List[Dict]:
    """
    Get current House member for a specific district.

    Args:
        state: Two-letter state abbreviation
        district: District number as string (e.g., "22")
        api_key: ProPublica API key

    Returns:
        List of member dicts (usually 1, but could be 0 if vacant)
    """
    all_house = get_members_by_state(state, "house", api_key)
    return [m for m in all_house if str(m.get("district", "")) == str(district)]


def get_all_federal_candidates(
    state: str,
    district: str = None,
    api_key: str = PROPUBLICA_API_KEY,
) -> List[Dict]:
    """
    Get all current federal incumbents relevant to a location.

    Args:
        state: Two-letter state abbreviation
        district: Congressional district number (optional, for House)
        api_key: ProPublica API key

    Returns:
        List of candidate dicts (both senators + relevant house member)
    """
    candidates = []

    # Get senators
    try:
        senators = get_members_by_state(state, "senate", api_key)
        candidates.extend(senators)
    except Exception:
        pass  # API may be down; we'll fill from FEC

    # Get house member for district
    if district:
        try:
            house = get_house_member_by_district(state, district, api_key)
            candidates.extend(house)
        except Exception:
            pass

    return candidates
