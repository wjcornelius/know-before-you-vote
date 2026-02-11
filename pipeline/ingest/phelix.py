"""
Ingest entity data from phelix001/epstein-network.
Primary source: focused_entities.json (richest data with connections, locations, years).
Fallback: dataset8_all_names.csv (simpler, but noisier).

Categories: core, accomplice, victim, political, business, legal/attorney,
            academic, entertainment, staff, journalist, unknown
"""
import csv
import json
import io
from typing import Dict

from pipeline.config import CACHE_DIR
from pipeline.ingest.common import Entity, EntityConnection, download_file

SOURCE_NAME = "phelix"

# URLs for raw files from the repo
FOCUSED_ENTITIES_URL = (
    "https://raw.githubusercontent.com/phelix001/epstein-network/main/focused_entities.json"
)
CSV_URL = (
    "https://raw.githubusercontent.com/phelix001/epstein-network/main/dataset8_all_names.csv"
)

# Categories to skip (noise, not people)
SKIP_CATEGORIES = {"unknown"}

# Known noise entries to filter out
NOISE_NAMES = {
    "new york", "palm beach", "florida", "normal attachments", "end date",
    "date created", "united states", "virgin islands", "little st. james",
}


def ingest_focused_entities() -> Dict[str, Entity]:
    """
    Ingest from focused_entities.json - the richest data source from phelix.
    Contains connections, locations, years, document IDs, and categories.
    """
    dest = CACHE_DIR / "phelix_focused_entities.json"
    download_file(FOCUSED_ENTITIES_URL, dest)

    data = json.loads(dest.read_text(encoding="utf-8"))
    people = data.get("people", {})

    entities: Dict[str, Entity] = {}

    for name, info in people.items():
        name_lower = name.strip().lower()

        # Skip noise entries
        if name_lower in NOISE_NAMES:
            continue

        category = info.get("category", "unknown")
        if category in SKIP_CATEGORIES:
            continue

        count = info.get("count", 0)
        doc_ids = info.get("docs", [])
        connections_raw = info.get("connections", {})
        role = info.get("role", "")

        # Build connection descriptions
        connections = []

        # The entity's own document presence
        if doc_ids:
            connections.append(EntityConnection(
                description=f"Named in {len(doc_ids)} FOIA documents. Category: {category}."
                + (f" Role: {role}" if role else ""),
                source_db=SOURCE_NAME,
                document_ids=doc_ids[:20],  # Cap at 20 for efficiency
                evidence_type="document_mention",
            ))

        # Co-occurrence connections with other entities
        for connected_name, co_count in connections_raw.items():
            if co_count >= 3:  # Only meaningful co-occurrences
                connections.append(EntityConnection(
                    description=f"Co-occurs with {connected_name} in {co_count} documents",
                    source_db=SOURCE_NAME,
                    evidence_type="co_occurrence",
                ))

        entity = Entity(
            name=name.strip(),
            sources=[SOURCE_NAME],
            connections=connections,
            categories=[category],
            total_document_mentions=count,
        )

        entities[name.strip()] = entity

    print(f"[phelix] Ingested {len(entities)} entities from focused_entities.json")
    return entities


def ingest_csv_fallback() -> Dict[str, Entity]:
    """
    Fallback: ingest from dataset8_all_names.csv.
    Less rich data but broader coverage.
    """
    dest = CACHE_DIR / "phelix_dataset8_all_names.csv"
    download_file(CSV_URL, dest)

    text = dest.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text))

    entities: Dict[str, Entity] = {}

    for row in reader:
        name = row.get("Name", "").strip()
        category = row.get("Category", "unknown").lower()
        mention_count = int(row.get("Mention Count", 0))
        sample_files = row.get("Sample Files", "")

        name_lower = name.lower()
        if name_lower in NOISE_NAMES or category in SKIP_CATEGORIES:
            continue

        if not name or mention_count < 2:
            continue

        doc_ids = [d.strip() for d in sample_files.split(";") if d.strip()]

        entity = Entity(
            name=name,
            sources=[SOURCE_NAME],
            connections=[
                EntityConnection(
                    description=f"Named in {mention_count} FOIA documents. Category: {category}.",
                    source_db=SOURCE_NAME,
                    document_ids=doc_ids,
                    evidence_type="document_mention",
                )
            ],
            categories=[category],
            total_document_mentions=mention_count,
        )

        # Deduplicate (CSV has some duplicate names)
        if name not in entities or mention_count > entities[name].total_document_mentions:
            entities[name] = entity

    print(f"[phelix] Ingested {len(entities)} entities from CSV fallback")
    return entities


def ingest() -> Dict[str, Entity]:
    """Main entry point. Tries focused_entities.json first, falls back to CSV."""
    try:
        return ingest_focused_entities()
    except Exception as e:
        print(f"[phelix] focused_entities.json failed ({e}), falling back to CSV")
        return ingest_csv_fallback()
