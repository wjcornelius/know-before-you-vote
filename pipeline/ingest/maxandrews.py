"""
Ingest entity data from maxandrews/Epstein-doc-explorer.
Source: document_analysis.db (91 MB SQLite via Git LFS)

Tables used:
  - rdf_triples: actor, action, target, doc_id, timestamp, location
  - entity_aliases: original_name -> canonical_name
  - documents: doc_id, file_path, one_sentence_summary
"""
import sqlite3
import subprocess
import shutil
from typing import Dict
from pathlib import Path

from pipeline.config import CACHE_DIR
from pipeline.ingest.common import Entity, EntityConnection

SOURCE_NAME = "maxandrews"

REPO_URL = "https://github.com/maxandrews/Epstein-doc-explorer.git"
DB_FILENAME = "document_analysis.db"


def _clone_and_get_db() -> Path:
    """
    Clone the repo (shallow) and pull the LFS database file.
    Returns path to the SQLite database.
    """
    db_path = CACHE_DIR / DB_FILENAME
    if db_path.exists():
        print(f"  Cached: {db_path.name}")
        return db_path

    clone_dir = CACHE_DIR / "epstein-doc-explorer"

    if not clone_dir.exists():
        print(f"  Cloning {REPO_URL} (shallow)...")
        subprocess.run(
            ["git", "clone", "--depth", "1", REPO_URL, str(clone_dir)],
            check=True,
            capture_output=True,
        )

    # Pull LFS files
    print("  Pulling Git LFS files...")
    subprocess.run(
        ["git", "lfs", "pull"],
        cwd=str(clone_dir),
        check=True,
        capture_output=True,
    )

    # Find the database file
    source_db = clone_dir / DB_FILENAME
    if not source_db.exists():
        # Try alternative locations
        for candidate in clone_dir.rglob("*.db"):
            if "document_analysis" in candidate.name:
                source_db = candidate
                break

    if not source_db.exists():
        raise FileNotFoundError(f"Could not find {DB_FILENAME} in cloned repo")

    # Copy to cache
    shutil.copy2(source_db, db_path)

    # Clean up clone to save space
    shutil.rmtree(clone_dir, ignore_errors=True)

    print(f"  Database ready: {db_path.name} ({db_path.stat().st_size / 1_000_000:.1f} MB)")
    return db_path


def ingest() -> Dict[str, Entity]:
    """
    Ingest entities from the maxandrews database.
    Extracts all actors and targets from RDF triples, resolves aliases,
    and builds entity records with connection details.
    """
    db_path = _clone_and_get_db()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    # Load entity aliases for name resolution
    aliases = {}
    try:
        for row in conn.execute("SELECT original_name, canonical_name FROM entity_aliases"):
            aliases[row["original_name"]] = row["canonical_name"]
    except sqlite3.OperationalError:
        print("  [maxandrews] No entity_aliases table found, proceeding without alias resolution")

    def resolve(name: str) -> str:
        return aliases.get(name, name)

    # Extract all RDF triples
    entities: Dict[str, Entity] = {}

    query = """
        SELECT rt.actor, rt.action, rt.target, rt.doc_id, rt.timestamp, rt.location
        FROM rdf_triples rt
        ORDER BY rt.actor
    """

    triple_count = 0
    for row in conn.execute(query):
        triple_count += 1
        actor = resolve(row["actor"]).strip()
        target = resolve(row["target"]).strip()
        action = row["action"]
        doc_id = row["doc_id"]
        timestamp = row["timestamp"] or ""
        location = row["location"] or ""

        # Build description
        desc_parts = [f"{actor} {action} {target}"]
        if timestamp:
            desc_parts.append(f"({timestamp})")
        if location:
            desc_parts.append(f"at {location}")
        description = " ".join(desc_parts)

        connection = EntityConnection(
            description=description,
            source_db=SOURCE_NAME,
            document_ids=[doc_id] if doc_id else [],
            evidence_type="rdf_triple",
        )

        # Add to actor's record
        if actor not in entities:
            entities[actor] = Entity(
                name=actor,
                sources=[SOURCE_NAME],
                connections=[],
                categories=[],
                total_document_mentions=0,
            )
        entities[actor].connections.append(connection)
        entities[actor].total_document_mentions += 1

        # Add to target's record
        if target not in entities:
            entities[target] = Entity(
                name=target,
                sources=[SOURCE_NAME],
                connections=[],
                categories=[],
                total_document_mentions=0,
            )
        entities[target].connections.append(EntityConnection(
            description=description,
            source_db=SOURCE_NAME,
            document_ids=[doc_id] if doc_id else [],
            evidence_type="rdf_triple",
        ))
        entities[target].total_document_mentions += 1

    conn.close()

    # Populate aliases
    for original, canonical in aliases.items():
        if canonical in entities and original != canonical:
            entities[canonical].aliases.append(original)

    print(f"[maxandrews] Ingested {len(entities)} entities from {triple_count} RDF triples")
    return entities
