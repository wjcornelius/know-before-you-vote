# Know Before You Vote

**Enter your zip code. See your ballot. See which candidates have documented connections to the Epstein network. Click any connection to see the source document.**

No editorializing. No accusations. No partisan framing. Just public records, organized by your ballot, with links to primary sources.

## How It Works

1. **Data Ingestion** - Downloads and parses pre-extracted entity data from citizen-built Epstein document analysis projects
2. **Candidate Pipeline** - Builds current candidate lists using Google Civic, ProPublica Congress, and FEC APIs
3. **Cross-Referencing** - Matches entities to candidates using fuzzy name matching + AI disambiguation
4. **Multi-Source Corroboration** - Only displays connections verified by 2+ independent source databases
5. **Classification** - Categorizes each connection as Direct, Contact, Financial, or Institutional
6. **Publication** - Generates a static website deployable to Vercel

## Connection Levels

| Level | Meaning |
|-------|---------|
| **Direct** | Named in documents as participant in Epstein's activities |
| **Contact** | Documented communication or social contact |
| **Financial** | Campaign donations from Epstein or documented associates |
| **Institutional** | Held position with authority over Epstein investigations |
| **None found** | No documented connection in available records |

## Trust Architecture

- Every claim links to a specific primary source document
- Connections require 2+ independent source databases to agree
- AI disambiguation prevents false name matches
- Equal standards regardless of party affiliation
- "None found" displayed for candidates without connections

## Data Sources (All Public)

- DOJ Epstein Library (justice.gov/epstein)
- Epstein Doc Explorer (maxandrews/Epstein-doc-explorer)
- LMSBAND Epstein Files DB (LMSBAND/epstein-files-db)
- SvetimFM Entity Analysis (SvetimFM/epstein-files-visualizations)
- phelix001 Epstein Network (phelix001/epstein-network)
- Google Civic Information API
- ProPublica Congress API
- FEC Campaign Finance API

## Running Locally

```bash
# Pipeline
pip install -r pipeline/requirements.txt
python -m pytest pipeline/tests/ -v

# Frontend
cd web && npm install && npm run dev
```

## License

Public domain. Use it, share it, build from it.

Built by W.J. Cornelius and Claude.
