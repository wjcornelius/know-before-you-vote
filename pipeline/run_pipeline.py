"""
Main pipeline orchestrator.
Runs all phases in sequence: ingest -> candidates -> crossref -> classify -> publish.

Usage:
  python -m pipeline.run_pipeline              # Full run
  python -m pipeline.run_pipeline --ingest     # Only ingestion
  python -m pipeline.run_pipeline --candidates # Only candidate refresh
"""
import argparse
import json
import sys
from datetime import datetime, timezone

from pipeline.config import CACHE_DIR, DATA_DIR
from pipeline.ingest.common import merge_entity_databases, save_entity_db, load_entity_db


def run_ingest():
    """Phase 2: Download and parse all Epstein entity databases."""
    print("=" * 60)
    print("PHASE 2: Entity Ingestion")
    print("=" * 60)

    databases = []

    # Import and run each ingestion module
    from pipeline.ingest import phelix, maxandrews, lmsband, svetimfm

    modules = [
        ("phelix", phelix),
        ("maxandrews", maxandrews),
        ("lmsband", lmsband),
        ("svetimfm", svetimfm),
    ]

    for name, module in modules:
        try:
            print(f"\n--- Ingesting from {name} ---")
            db = module.ingest()
            databases.append(db)
            print(f"  -> {len(db)} entities")
        except Exception as e:
            print(f"  -> FAILED: {e}")
            # Continue with other sources - partial data is better than none

    if not databases:
        print("\nERROR: No databases could be ingested. Aborting.")
        sys.exit(1)

    # Merge all databases
    print(f"\n--- Merging {len(databases)} databases ---")
    unified = merge_entity_databases(*databases)
    print(f"  -> {len(unified)} unique entities after merge")

    # Count multi-source entities (these are the ones we can display)
    multi_source = sum(1 for e in unified.values() if len(e.sources) >= 2)
    print(f"  -> {multi_source} entities with 2+ source databases (displayable)")

    # Save unified database
    path = save_entity_db(unified)
    print(f"  -> Saved to {path}")

    return unified


def run_candidates():
    """Phase 3: Build candidate database from API sources."""
    print("\n" + "=" * 60)
    print("PHASE 3: Candidate Pipeline")
    print("=" * 60)
    print("  (Not yet implemented - requires API keys)")
    # TODO: Implement when API keys are available
    return []


def run_crossref(unified_entities, candidates):
    """Phase 4: Cross-reference entities with candidates."""
    print("\n" + "=" * 60)
    print("PHASE 4: Cross-Referencing")
    print("=" * 60)
    print("  (Not yet implemented - requires candidates)")
    return {}


def run_classify(matched_results):
    """Phase 5: Classify connection levels."""
    print("\n" + "=" * 60)
    print("PHASE 5: Classification")
    print("=" * 60)
    print("  (Not yet implemented - requires matched results)")
    return {}


def run_publish(candidates, filtered_connections, classifications):
    """Phase 6: Generate static JSON for frontend."""
    print("\n" + "=" * 60)
    print("PHASE 6: Publish")
    print("=" * 60)

    from pipeline.publish.generate_json import publish_metadata
    path = publish_metadata()
    print(f"  -> Published metadata to {path}")


def main():
    parser = argparse.ArgumentParser(description="Know Before You Vote data pipeline")
    parser.add_argument("--ingest", action="store_true", help="Only run ingestion")
    parser.add_argument("--candidates", action="store_true", help="Only refresh candidates")
    parser.add_argument("--full", action="store_true", help="Full pipeline run (default)")
    args = parser.parse_args()

    start = datetime.now(timezone.utc)
    print(f"Pipeline started at {start.isoformat()}")
    print(f"Cache directory: {CACHE_DIR}")
    print(f"Output directory: {DATA_DIR}")

    if args.ingest:
        run_ingest()
    elif args.candidates:
        run_candidates()
    else:
        # Full run
        unified = run_ingest()
        candidates = run_candidates()
        matched = run_crossref(unified, candidates)
        classifications = run_classify(matched)
        run_publish(candidates, matched, classifications)

    elapsed = (datetime.now(timezone.utc) - start).total_seconds()
    print(f"\nPipeline completed in {elapsed:.1f} seconds")


if __name__ == "__main__":
    main()
