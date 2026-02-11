"""
Common types and utilities for all ingestion modules.
Every ingestion module outputs entities in this standard format.
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
import json
from pathlib import Path

from pipeline.config import CACHE_DIR


@dataclass
class EntityConnection:
    """A single piece of evidence connecting a person to the Epstein network."""
    description: str
    source_db: str
    document_ids: List[str] = field(default_factory=list)
    raw_text: str = ""
    evidence_type: str = ""  # e.g., "flight_log", "email", "co-occurrence", "testimony"


@dataclass
class Entity:
    """A person extracted from Epstein documents."""
    name: str
    sources: List[str] = field(default_factory=list)
    connections: List[EntityConnection] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)
    total_document_mentions: int = 0

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "sources": self.sources,
            "connections": [asdict(c) for c in self.connections],
            "categories": self.categories,
            "aliases": self.aliases,
            "total_document_mentions": self.total_document_mentions,
        }


def merge_entity_databases(*databases: Dict[str, Entity]) -> Dict[str, Entity]:
    """
    Merge multiple entity databases into a unified one.
    Entities with matching normalized names are combined.
    """
    from pipeline.crossref.normalize import normalize_name

    merged: Dict[str, Entity] = {}

    for db in databases:
        for name, entity in db.items():
            norm = normalize_name(name)
            if not norm:
                continue

            if norm not in merged:
                merged[norm] = Entity(
                    name=entity.name,
                    sources=list(entity.sources),
                    connections=list(entity.connections),
                    categories=list(entity.categories),
                    aliases=list(entity.aliases),
                    total_document_mentions=entity.total_document_mentions,
                )
            else:
                existing = merged[norm]
                # Add new sources
                for src in entity.sources:
                    if src not in existing.sources:
                        existing.sources.append(src)
                # Add connections
                existing.connections.extend(entity.connections)
                # Add categories
                for cat in entity.categories:
                    if cat not in existing.categories:
                        existing.categories.append(cat)
                # Add aliases
                if entity.name != existing.name and entity.name not in existing.aliases:
                    existing.aliases.append(entity.name)
                for alias in entity.aliases:
                    if alias not in existing.aliases:
                        existing.aliases.append(alias)
                # Sum mentions
                existing.total_document_mentions += entity.total_document_mentions

    return merged


def save_entity_db(entities: Dict[str, Entity], filename: str = "unified_entities.json") -> Path:
    """Save entity database to JSON."""
    path = CACHE_DIR / filename
    data = {name: entity.to_dict() for name, entity in entities.items()}
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


def load_entity_db(filename: str = "unified_entities.json") -> Dict[str, Dict]:
    """Load entity database from JSON (returns raw dicts, not Entity objects)."""
    path = CACHE_DIR / filename
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def download_file(url: str, dest: Path, chunk_size: int = 8192) -> Path:
    """Download a file with progress, skipping if already cached."""
    import requests

    if dest.exists():
        print(f"  Cached: {dest.name}")
        return dest

    print(f"  Downloading: {url}")
    dest.parent.mkdir(parents=True, exist_ok=True)

    resp = requests.get(url, stream=True, timeout=300)
    resp.raise_for_status()

    total = int(resp.headers.get("content-length", 0))
    downloaded = 0

    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=chunk_size):
            f.write(chunk)
            downloaded += len(chunk)
            if total:
                pct = (downloaded / total) * 100
                print(f"  {downloaded / 1_000_000:.1f} MB / {total / 1_000_000:.1f} MB ({pct:.0f}%)", end="\r")

    print(f"  Downloaded: {dest.name} ({downloaded / 1_000_000:.1f} MB)")
    return dest
