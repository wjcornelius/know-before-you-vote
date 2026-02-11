"""
Connection level classification using Claude Haiku.
Categorizes verified connections as Direct, Contact, Financial, or Institutional.

CRITICAL: Classification is based ONLY on what documents show, never on inference.
Flying on the plane without documented illegal activity = "Contact", not "Direct".
"""
import json
from typing import Dict, List

from pipeline.config import ANTHROPIC_API_KEY, CONNECTION_LEVELS


CLASSIFICATION_PROMPT = """You are classifying the nature of a connection between a political figure and the Epstein network based ONLY on documentary evidence.

PERSON: {person_name}
OFFICE: {office}

DOCUMENTARY EVIDENCE:
{evidence_text}

Classify this connection into exactly ONE of these levels:

DIRECT - Named as participant in illegal activities: victim testimony naming them, evidence of sexual abuse, evidence of participation in trafficking. This is the highest level and requires the strongest evidence.

CONTACT - Documented communication or social contact: flight logs, emails, event attendance, phone records, photographs together. This does NOT imply participation in illegal activity.

FINANCIAL - Campaign donations from Epstein, Maxwell, or documented close associates. Based on FEC filings or financial records.

INSTITUTIONAL - Held a position with authority over Epstein investigations and failed to act, or had oversight responsibility. Prosecutors, AG offices, judges who gave lenient sentences, oversight committee members.

RULES:
- Classify based ONLY on what the documents explicitly show
- If someone flew on the plane but no illegal activity is documented during that flight, classify as CONTACT not DIRECT
- Being in Epstein's contact book alone = CONTACT
- Receiving donations from Epstein = FINANCIAL
- If evidence spans multiple levels, classify at the HIGHEST supported level
- When in doubt, classify LOWER (Contact rather than Direct)

Respond with a JSON object:
{{"level": "DIRECT|CONTACT|FINANCIAL|INSTITUTIONAL", "reasoning": "One sentence explaining why this level"}}"""


def classify_connection(
    person_name: str,
    office: str,
    evidence: List[Dict],
    api_key: str = ANTHROPIC_API_KEY,
) -> Dict:
    """
    Classify a verified connection's level using AI.

    Args:
        person_name: The person's name
        office: Their political office
        evidence: List of evidence dicts from corroborated sources

    Returns:
        {"level": str, "reasoning": str}
    """
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set.")

    import anthropic

    # Build evidence text from all corroborating sources
    evidence_parts = []
    for i, ev in enumerate(evidence[:15], 1):  # Cap at 15 for token efficiency
        source = ev.get("source_db", "unknown")
        desc = ev.get("description", "")
        raw = ev.get("raw_text", "")[:400]
        doc_id = ev.get("document_id", "unknown")

        text = desc or raw
        if text:
            evidence_parts.append(f"{i}. [{source}] (Doc: {doc_id}) {text}")

    if not evidence_parts:
        return {"level": "Contact", "reasoning": "No detailed evidence available; defaulting to lowest level."}

    evidence_text = "\n".join(evidence_parts)

    prompt = CLASSIFICATION_PROMPT.format(
        person_name=person_name,
        office=office,
        evidence_text=evidence_text,
    )

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )

    answer = response.content[0].text.strip()

    # Parse JSON response
    try:
        result = json.loads(answer)
        level = result.get("level", "Contact")
        reasoning = result.get("reasoning", "")

        # Validate level is one we recognize
        if level not in CONNECTION_LEVELS:
            level = "Contact"  # Default to safest level

        return {"level": level, "reasoning": reasoning}
    except json.JSONDecodeError:
        # If AI didn't return valid JSON, default to Contact (safest)
        return {"level": "Contact", "reasoning": f"Classification unclear; defaulting to Contact. Raw: {answer[:100]}"}
