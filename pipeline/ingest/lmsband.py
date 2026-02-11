"""
Ingest entity data from LMSBAND/epstein-files-db.
Source: epstein.db (835 MB SQLite, split into 4 gzipped parts)

Tables used:
  - entities: file_id, entity_text, entity_label, normalized, count
  - entity_cooccurrence: entity_a, entity_b, file_count
  - files: id, filename, dataset, rel_path
"""
import gzip
import sqlite3
import subprocess
from typing import Dict
from pathlib import Path

from pipeline.config import CACHE_DIR
from pipeline.ingest.common import Entity, EntityConnection, download_file

SOURCE_NAME = "lmsband"

# 4-part download from GitHub releases
RELEASE_BASE = "https://github.com/LMSBAND/epstein-files-db/releases/download/v1.0"
PARTS = [
    f"{RELEASE_BASE}/epstein.db.gz.part-aa",
    f"{RELEASE_BASE}/epstein.db.gz.part-ab",
    f"{RELEASE_BASE}/epstein.db.gz.part-ac",
    f"{RELEASE_BASE}/epstein.db.gz.part-ad",
]

DB_FILENAME = "lmsband_epstein.db"


def _download_and_assemble_db() -> Path:
    """
    Download 4-part gzipped database and reassemble.
    Returns path to the SQLite database.
    """
    db_path = CACHE_DIR / DB_FILENAME
    if db_path.exists():
        print(f"  Cached: {db_path.name}")
        return db_path

    # Download parts
    part_paths = []
    for url in PARTS:
        part_name = url.split("/")[-1]
        part_path = CACHE_DIR / part_name
        download_file(url, part_path)
        part_paths.append(part_path)

    # Concatenate parts into single gzip file
    gz_path = CACHE_DIR / "epstein.db.gz"
    print("  Assembling parts...")
    with open(gz_path, "wb") as outfile:
        for part in part_paths:
            with open(part, "rb") as infile:
                outfile.write(infile.read())

    # Decompress
    print("  Decompressing...")
    with gzip.open(gz_path, "rb") as gz_file:
        with open(db_path, "wb") as db_file:
            while True:
                chunk = gz_file.read(1024 * 1024)  # 1 MB chunks
                if not chunk:
                    break
                db_file.write(chunk)

    # Clean up parts and gz to save space
    for part in part_paths:
        part.unlink(missing_ok=True)
    gz_path.unlink(missing_ok=True)

    print(f"  Database ready: {db_path.name} ({db_path.stat().st_size / 1_000_000:.1f} MB)")
    return db_path


def ingest() -> Dict[str, Entity]:
    """
    Ingest entities from the LMSBAND database.
    Focuses on PERSON entities and their co-occurrence relationships.
    """
    db_path = _download_and_assemble_db()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    entities: Dict[str, Entity] = {}

    # Step 1: Get all PERSON entities with their document counts
    print("  Loading PERSON entities...")
    person_query = """
        SELECT normalized AS name,
               SUM(count) AS total_mentions,
               COUNT(DISTINCT file_id) AS file_count,
               GROUP_CONCAT(DISTINCT file_id) AS file_ids
        FROM entities
        WHERE entity_label = 'PERSON'
          AND length(normalized) > 2
        GROUP BY normalized
        HAVING file_count >= 2
        ORDER BY total_mentions DESC
    """

    for row in conn.execute(person_query):
        name = row["name"].strip()
        if not name:
            continue

        file_ids = (row["file_ids"] or "").split(",")

        entity = Entity(
            name=name,
            sources=[SOURCE_NAME],
            connections=[
                EntityConnection(
                    description=f"Named in {row['file_count']} DOJ documents "
                    f"({row['total_mentions']} total mentions)",
                    source_db=SOURCE_NAME,
                    document_ids=file_ids[:20],
                    evidence_type="ner_extraction",
                )
            ],
            categories=[],
            total_document_mentions=row["total_mentions"],
        )
        entities[name] = entity

    # Step 2: Add co-occurrence relationships
    print("  Loading co-occurrence relationships...")
    cooccur_query = """
        SELECT entity_a, entity_b, file_count
        FROM entity_cooccurrence
        WHERE file_count >= 3
        ORDER BY file_count DESC
    """

    cooccur_count = 0
    for row in conn.execute(cooccur_query):
        entity_a = row["entity_a"].strip()
        entity_b = row["entity_b"].strip()
        file_count = row["file_count"]

        # Add co-occurrence to both entities if they exist
        for name_a, name_b in [(entity_a, entity_b), (entity_b, entity_a)]:
            if name_a in entities:
                entities[name_a].connections.append(EntityConnection(
                    description=f"Co-occurs with {name_b} in {file_count} documents",
                    source_db=SOURCE_NAME,
                    evidence_type="co_occurrence",
                ))
                cooccur_count += 1

    conn.close()

    print(f"[lmsband] Ingested {len(entities)} entities with {cooccur_count} co-occurrence links")
    return entities
