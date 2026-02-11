"""
Ingest entity data from SvetimFM/epstein-files-visualizations.
Source: JSON data files from the GitHub repo.

This project has 68,798 documents with NER-extracted entities,
16,169 financial transactions, and timeline events.
"""
import json
from typing import Dict

from pipeline.config import CACHE_DIR
from pipeline.ingest.common import Entity, EntityConnection, download_file

SOURCE_NAME = "svetimfm"

# Try multiple possible data file locations from the repo
ENTITY_DATA_URLS = [
    "https://raw.githubusercontent.com/SvetimFM/epstein-files-visualizations/main/data/entities.json",
    "https://raw.githubusercontent.com/SvetimFM/epstein-files-visualizations/main/entities.json",
    "https://raw.githubusercontent.com/SvetimFM/epstein-files-visualizations/main/data/network_data.json",
]

FINANCIAL_DATA_URLS = [
    "https://raw.githubusercontent.com/SvetimFM/epstein-files-visualizations/main/data/financial_transactions.json",
    "https://raw.githubusercontent.com/SvetimFM/epstein-files-visualizations/main/financial_transactions.json",
]


def _try_download(urls: list, dest_name: str) -> dict | list | None:
    """Try downloading from multiple possible URLs."""
    for url in urls:
        dest = CACHE_DIR / dest_name
        try:
            download_file(url, dest)
            data = json.loads(dest.read_text(encoding="utf-8"))
            return data
        except Exception:
            dest.unlink(missing_ok=True)
            continue
    return None


def ingest() -> Dict[str, Entity]:
    """
    Ingest entities from SvetimFM project.
    Tries entity JSON files, falls back gracefully if structure differs from expected.
    """
    entities: Dict[str, Entity] = {}

    # Try to load entity data
    entity_data = _try_download(ENTITY_DATA_URLS, "svetimfm_entities.json")

    if entity_data:
        if isinstance(entity_data, dict):
            # Could be {name: {count, type, ...}} or {nodes: [...], links: [...]}
            if "nodes" in entity_data:
                # Network graph format
                for node in entity_data["nodes"]:
                    name = node.get("name", node.get("id", "")).strip()
                    if not name or len(name) < 3:
                        continue

                    entity = Entity(
                        name=name,
                        sources=[SOURCE_NAME],
                        connections=[EntityConnection(
                            description=f"Entity in network graph. "
                            f"Type: {node.get('type', 'unknown')}. "
                            f"Documents: {node.get('doc_count', 'unknown')}",
                            source_db=SOURCE_NAME,
                            document_ids=node.get("docs", [])[:20],
                            evidence_type="network_node",
                        )],
                        categories=[node.get("type", "unknown")],
                        total_document_mentions=node.get("doc_count", node.get("count", 0)),
                    )
                    entities[name] = entity

            else:
                # Direct name -> info mapping
                for name, info in entity_data.items():
                    if isinstance(info, dict):
                        name = name.strip()
                        if not name or len(name) < 3:
                            continue

                        count = info.get("count", info.get("doc_count", 0))
                        entity = Entity(
                            name=name,
                            sources=[SOURCE_NAME],
                            connections=[EntityConnection(
                                description=f"Named entity in {count} documents",
                                source_db=SOURCE_NAME,
                                document_ids=info.get("docs", info.get("document_ids", []))[:20],
                                evidence_type="ner_extraction",
                            )],
                            categories=[info.get("type", info.get("category", "unknown"))],
                            total_document_mentions=count,
                        )
                        entities[name] = entity

        elif isinstance(entity_data, list):
            # Array of entity objects
            for item in entity_data:
                if isinstance(item, dict):
                    name = item.get("name", item.get("entity", "")).strip()
                    if not name or len(name) < 3:
                        continue

                    count = item.get("count", item.get("mentions", 0))
                    entity = Entity(
                        name=name,
                        sources=[SOURCE_NAME],
                        connections=[EntityConnection(
                            description=f"Named entity. Mentions: {count}",
                            source_db=SOURCE_NAME,
                            document_ids=item.get("docs", item.get("document_ids", []))[:20],
                            evidence_type="ner_extraction",
                        )],
                        categories=[item.get("type", item.get("category", "unknown"))],
                        total_document_mentions=count,
                    )
                    entities[name] = entity

    # Try to load financial transaction data
    financial_data = _try_download(FINANCIAL_DATA_URLS, "svetimfm_financial.json")

    if financial_data and isinstance(financial_data, list):
        for txn in financial_data:
            for party_key in ["from", "to", "sender", "recipient", "party"]:
                party = txn.get(party_key, "").strip()
                if party and len(party) >= 3:
                    amount = txn.get("amount", txn.get("value", ""))
                    purpose = txn.get("purpose", txn.get("description", ""))
                    doc_id = txn.get("document_id", txn.get("doc_id", ""))

                    conn = EntityConnection(
                        description=f"Financial transaction: {purpose}. Amount: {amount}",
                        source_db=SOURCE_NAME,
                        document_ids=[doc_id] if doc_id else [],
                        evidence_type="financial_transaction",
                    )

                    if party in entities:
                        entities[party].connections.append(conn)
                    else:
                        entities[party] = Entity(
                            name=party,
                            sources=[SOURCE_NAME],
                            connections=[conn],
                            categories=["financial"],
                            total_document_mentions=1,
                        )

    if not entities:
        print(f"[svetimfm] WARNING: Could not load data from any known URL. "
              f"Repository structure may have changed.")
    else:
        print(f"[svetimfm] Ingested {len(entities)} entities")

    return entities
