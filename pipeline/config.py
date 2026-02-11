"""
Central configuration for the Know Before You Vote pipeline.
API keys are loaded from environment variables (set as GitHub Actions secrets in production).
"""
import os
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
PIPELINE_DIR = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "web" / "public" / "data"
CACHE_DIR = PIPELINE_DIR / ".cache"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# API Keys (from environment variables)
GOOGLE_CIVIC_API_KEY = os.environ.get("GOOGLE_CIVIC_API_KEY", "")
PROPUBLICA_API_KEY = os.environ.get("PROPUBLICA_API_KEY", "")
FEC_API_KEY = os.environ.get("FEC_API_KEY", "")
PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Cross-referencing thresholds
FUZZY_MATCH_THRESHOLD = 92  # Minimum fuzzywuzzy score to consider a name match
MIN_SOURCES_TO_DISPLAY = 2  # Minimum independent sources required to show a connection
HIGH_CONFIDENCE_SOURCES = 3  # Sources needed for HIGH confidence rating

# Connection levels (ordered by severity)
CONNECTION_LEVELS = ["Direct", "Contact", "Financial", "Institutional"]

# Source database URLs
SOURCES = {
    "maxandrews": {
        "repo": "https://github.com/maxandrews/Epstein-doc-explorer",
        "description": "Epstein Doc Explorer - 15,000+ RDF relationship triples from email corpus",
    },
    "lmsband": {
        "repo": "https://github.com/LMSBAND/epstein-files-db",
        "release": "https://github.com/LMSBAND/epstein-files-db/releases/tag/v1.0",
        "description": "DOJ Datasets 8-12 with NER entities and co-occurrence graph",
    },
    "svetimfm": {
        "repo": "https://github.com/SvetimFM/epstein-files-visualizations",
        "description": "68,798 documents with entity networks and financial transactions",
    },
    "phelix": {
        "repo": "https://github.com/phelix001/epstein-network",
        "description": "19,154 FOIA documents with categorized entities",
    },
}
