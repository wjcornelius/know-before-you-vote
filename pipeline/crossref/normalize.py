"""
Name normalization for cross-referencing Epstein entities with political candidates.
Handles titles, nicknames, suffixes, and common variations.
"""
import re
from typing import List

# Common political/professional titles to strip
TITLES = [
    "president", "vice president", "senator", "sen.", "representative", "rep.",
    "congressman", "congresswoman", "governor", "gov.", "mayor", "judge",
    "justice", "secretary", "ambassador", "hon.", "honorable", "dr.", "mr.",
    "mrs.", "ms.", "prof.", "professor", "general", "gen.", "colonel", "col.",
    "captain", "capt.", "lieutenant", "lt.", "sergeant", "sgt.",
]

# Common nickname -> formal name mappings
NICKNAMES = {
    "bill": "william",
    "billy": "william",
    "will": "william",
    "willy": "william",
    "bob": "robert",
    "bobby": "robert",
    "rob": "robert",
    "dick": "richard",
    "rick": "richard",
    "rich": "richard",
    "ted": "edward",
    "teddy": "edward",
    "ed": "edward",
    "eddie": "edward",
    "mike": "michael",
    "mikey": "michael",
    "jim": "james",
    "jimmy": "james",
    "jamie": "james",
    "joe": "joseph",
    "joey": "joseph",
    "tom": "thomas",
    "tommy": "thomas",
    "dave": "david",
    "dan": "daniel",
    "danny": "daniel",
    "chris": "christopher",
    "matt": "matthew",
    "pat": "patrick",
    "tony": "anthony",
    "steve": "steven",
    "stevie": "steven",
    "al": "albert",
    "alex": "alexander",
    "andy": "andrew",
    "drew": "andrew",
    "ben": "benjamin",
    "benny": "benjamin",
    "bernie": "bernard",
    "bert": "albert",
    "beth": "elizabeth",
    "betsy": "elizabeth",
    "liz": "elizabeth",
    "lizzy": "elizabeth",
    "beth": "elizabeth",
    "betty": "elizabeth",
    "cathy": "catherine",
    "kate": "catherine",
    "katie": "catherine",
    "chuck": "charles",
    "charlie": "charles",
    "connie": "constance",
    "deb": "deborah",
    "debbie": "deborah",
    "don": "donald",
    "donny": "donald",
    "doug": "douglas",
    "frank": "francis",
    "fred": "frederick",
    "gerry": "gerald",
    "jerry": "gerald",
    "greg": "gregory",
    "hank": "henry",
    "harry": "henry",
    "jack": "john",
    "jake": "jacob",
    "jeff": "jeffrey",
    "jenny": "jennifer",
    "jenn": "jennifer",
    "larry": "lawrence",
    "len": "leonard",
    "lenny": "leonard",
    "marty": "martin",
    "mel": "melvin",
    "mitch": "mitchell",
    "nate": "nathaniel",
    "nat": "nathaniel",
    "ned": "edward",
    "nick": "nicholas",
    "norm": "norman",
    "pam": "pamela",
    "pete": "peter",
    "phil": "philip",
    "ralph": "ralph",
    "ray": "raymond",
    "ron": "ronald",
    "ronnie": "ronald",
    "russ": "russell",
    "sam": "samuel",
    "sammy": "samuel",
    "sandy": "sandra",
    "sue": "susan",
    "suzy": "susan",
    "terry": "terrence",
    "tim": "timothy",
    "vince": "vincent",
    "walt": "walter",
    "wes": "wesley",
}

# Suffixes to strip for matching but preserve for display
SUFFIXES = ["jr.", "jr", "junior", "sr.", "sr", "senior", "ii", "iii", "iv", "v",
            "2nd", "3rd", "4th", "esq.", "esq", "m.d.", "md", "ph.d.", "phd"]


def normalize_name(name: str) -> str:
    """
    Normalize a name for comparison. Returns lowercase, stripped of titles/suffixes,
    with nicknames expanded to formal names.
    """
    if not name:
        return ""

    result = name.lower().strip()

    # Remove parenthetical content like "(D-CA)" or "(Republican)"
    result = re.sub(r'\([^)]*\)', '', result).strip()

    # Remove all periods first (Sen. -> Sen, J.F. -> JF, Jr. -> Jr)
    result = result.replace('.', ' ')
    result = re.sub(r'\s+', ' ', result).strip()

    # Remove titles (now without periods: "sen", "rep", "hon", "dr", etc.)
    for title in TITLES:
        title_clean = title.replace('.', '').strip()
        # Match as whole word
        result = re.sub(r'\b' + re.escape(title_clean) + r'\b', '', result)

    # Remove suffixes
    for suffix in SUFFIXES:
        suffix_clean = suffix.replace('.', '').strip()
        result = re.sub(r',?\s*\b' + re.escape(suffix_clean) + r'\b$', '', result)

    # Clean up whitespace
    result = re.sub(r'\s+', ' ', result).strip()

    # Expand first-name nicknames
    parts = result.split()
    if parts:
        first = parts[0]
        if first in NICKNAMES:
            parts[0] = NICKNAMES[first]
        result = ' '.join(parts)

    return result.strip()


def generate_name_variants(name: str) -> List[str]:
    """
    Generate multiple plausible variants of a name for fuzzy matching.
    Returns a list of normalized name variants.
    """
    variants = set()

    normalized = normalize_name(name)
    if normalized:
        variants.add(normalized)

    parts = normalized.split()
    if not parts:
        return list(variants)

    # Full name as-is
    variants.add(normalized)

    # If there are 3+ parts, try first + last (skipping middle)
    if len(parts) >= 3:
        variants.add(f"{parts[0]} {parts[-1]}")

    # If first name has a nickname mapping, try both directions
    first = parts[0]
    rest = ' '.join(parts[1:]) if len(parts) > 1 else ''

    # Try the original first name (before nickname expansion)
    original_lower = name.lower().strip().split()
    if original_lower:
        original_first = original_lower[0]
        if original_first != first and rest:
            variants.add(f"{original_first} {rest}")

    # Try reverse nickname lookup (formal -> common nicknames)
    reverse_nicknames = {}
    for nick, formal in NICKNAMES.items():
        if formal not in reverse_nicknames:
            reverse_nicknames[formal] = []
        reverse_nicknames[formal].append(nick)

    if first in reverse_nicknames and rest:
        for nick in reverse_nicknames[first]:
            variants.add(f"{nick} {rest}")

    return list(variants)


def names_match(name_a: str, name_b: str) -> bool:
    """
    Check if two names likely refer to the same person after normalization.
    Uses exact match on normalized forms. For fuzzy matching, use thefuzz library
    in the match.py module.
    """
    norm_a = normalize_name(name_a)
    norm_b = normalize_name(name_b)

    if not norm_a or not norm_b:
        return False

    # Exact normalized match
    if norm_a == norm_b:
        return True

    # Check all variants
    variants_a = set(generate_name_variants(name_a))
    variants_b = set(generate_name_variants(name_b))

    return bool(variants_a & variants_b)
