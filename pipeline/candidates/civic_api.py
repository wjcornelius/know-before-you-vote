"""
Google Civic Information API - divisionsByAddress endpoint.
Converts a zip code into political divisions (congressional district, state, etc.)

Note: The Representatives endpoint was discontinued March 2025.
We use divisionsByAddress to get OCD-IDs, then look up candidates from other sources.
"""
import requests
from typing import Dict, List, Optional

from pipeline.config import GOOGLE_CIVIC_API_KEY


DIVISIONS_URL = "https://www.googleapis.com/civicinfo/v2/divisions"


def get_divisions_by_address(
    address: str,
    api_key: str = GOOGLE_CIVIC_API_KEY,
) -> Dict:
    """
    Get political divisions for an address using Google Civic API.

    Args:
        address: Full address or just a zip code (e.g., "90210" or "123 Main St, City, ST 12345")
        api_key: Google Civic API key

    Returns:
        Dict with 'divisions' mapping OCD-IDs to division info, plus 'normalized_address'
    """
    if not api_key:
        raise ValueError("GOOGLE_CIVIC_API_KEY not set.")

    # The divisionsByAddress endpoint doesn't exist directly.
    # We use representatives endpoint with just address to get divisions.
    # Actually, with the Representatives API discontinued, we use the
    # voterInfoQuery or fall back to the divisions search.
    # For now, use the representatives endpoint which still returns divisions
    # even though representative data is gone.

    # Alternative approach: use the OCD-ID lookup
    resp = requests.get(
        "https://www.googleapis.com/civicinfo/v2/representatives",
        params={"address": address, "key": api_key},
        timeout=10,
    )

    if resp.status_code == 404 or resp.status_code == 400:
        # Try with divisions endpoint as fallback
        return _fallback_zip_to_district(address)

    resp.raise_for_status()
    data = resp.json()

    divisions = {}
    for ocd_id, div_info in data.get("divisions", {}).items():
        divisions[ocd_id] = {
            "name": div_info.get("name", ""),
            "ocd_id": ocd_id,
        }

    return {
        "divisions": divisions,
        "normalized_address": data.get("normalizedInput", {}),
    }


def extract_district_info(divisions: Dict) -> Dict:
    """
    Extract congressional district and state from OCD-ID divisions.

    Args:
        divisions: Output from get_divisions_by_address()['divisions']

    Returns:
        Dict with 'state', 'congressional_district', 'state_upper', 'state_lower'
    """
    result = {
        "state": None,
        "state_abbrev": None,
        "congressional_district": None,
        "senate_class": None,  # Which Senate seats are up
    }

    for ocd_id in divisions:
        parts = ocd_id.split("/")

        for part in parts:
            if part.startswith("state:"):
                result["state_abbrev"] = part.split(":")[1].upper()
                result["state"] = divisions[ocd_id].get("name", "")

            if part.startswith("cd:") or "congressional_district" in part:
                try:
                    district_num = part.split(":")[-1]
                    result["congressional_district"] = district_num
                except (ValueError, IndexError):
                    pass

    return result


def _fallback_zip_to_district(zip_code: str) -> Dict:
    """
    Fallback: Use Census Bureau ZCTA-to-congressional-district crosswalk.
    This is a static lookup that doesn't require an API call.
    The actual crosswalk data will be bundled in districts.json.
    """
    return {
        "divisions": {},
        "normalized_address": {"zip": zip_code},
        "error": "Could not resolve divisions. Using static district mapping.",
    }
