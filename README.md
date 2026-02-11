# Know Before You Vote

**A fully designed, partially built open-source tool that lets voters enter their zip code and see which candidates on their ballot have documented connections to the Epstein network — with links to primary source documents.**

No editorializing. No accusations. No partisan framing. Just public records, organized by your ballot, with links to primary sources.

---

## Looking for a Developer to Take This On

This project has a complete architecture, working scaffolding, and a detailed development plan — but **the original author is unable to continue development**. Everything is here for someone to pick up and finish.

### What's Already Built
- **Full 9-phase development plan** with architecture, data flow, and test strategy (see [PLAN.md](PLAN.md))
- **Entity ingestion pipeline** — Python modules to download and parse all 4 community Epstein databases into a unified entity format (tested, working)
- **Entity merge & deduplication** — Combines entities across databases with name normalization (55 tests passing)
- **Name normalization** — 90+ nickname mappings, title/suffix stripping, variant generation
- **Multi-source corroboration logic** — The core safety mechanism: 2+ independent databases must agree before any connection is displayed
- **Cross-referencing modules** — Fuzzy matching + AI disambiguation (Claude Haiku) to prevent false name matches
- **Connection classifier** — AI categorization into Direct/Contact/Financial/Institutional levels
- **Citation generator** — Structured evidence citations linking to primary source documents
- **Candidate pipeline modules** — Google Civic, ProPublica Congress, and FEC API integrations
- **Next.js frontend scaffold** — Landing page, results page, candidate detail page, methodology page
- **GitHub Actions CI** — Test workflow running on every push
- **Component library** — CandidateCard, ConnectionBadge components with Tailwind styling

### What Still Needs to Be Done
- **Phase 3**: Wire up candidate pipeline against live APIs (modules written, need API keys + testing)
- **Phase 4**: End-to-end cross-referencing against real data
- **Phase 5**: Test classification with real evidence
- **Phase 6**: Connect frontend to pipeline-generated JSON
- **Phase 7**: Set up automated GitHub Actions workflows (weekly updates, daily candidate refresh, news monitoring)
- **Phase 8**: Pre-launch audit (human review of all displayed connections)
- **Phase 9**: Domain registration and launch

### Estimated Ongoing Costs
| Service | Cost |
|---------|------|
| Perplexity API (news monitoring) | ~$5-8/mo |
| Claude Haiku (disambiguation) | ~$1-2/mo |
| GitHub Actions | ~$2-4/mo |
| Vercel hosting | Free tier |
| Google Civic, ProPublica, FEC APIs | Free |
| **Total** | **~$9-15/month** |

---

## How It Works

1. **Data Ingestion** — Downloads and parses pre-extracted entity data from 4 citizen-built Epstein document analysis projects
2. **Candidate Pipeline** — Builds current candidate lists using Google Civic, ProPublica Congress, and FEC APIs
3. **Cross-Referencing** — Matches entities to candidates using fuzzy name matching + AI disambiguation
4. **Multi-Source Corroboration** — Only displays connections verified by 2+ independent source databases
5. **Classification** — Categorizes each connection as Direct, Contact, Financial, or Institutional
6. **Publication** — Generates a static website deployable to Vercel

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
- AI disambiguation prevents false name matches ("John Kennedy" from Louisiana ≠ "John F. Kennedy" from the 1960s)
- Equal standards regardless of party affiliation
- "None found" explicitly displayed for candidates without connections
- Conservative threshold: better to miss a real connection than show a false one

## Data Sources (All Public, All Free)

| Source | Data |
|--------|------|
| [Epstein Doc Explorer](https://github.com/maxandrews/Epstein-doc-explorer) | 15,000+ relationships from email corpus (91 MB SQLite) |
| [LMSBAND Epstein Files DB](https://github.com/LMSBAND/epstein-files-db) | Named entities from DOJ Datasets 8-12 (835 MB SQLite) |
| [SvetimFM Analysis](https://github.com/SvetimFM/epstein-files-visualizations) | 68,798 documents with entity networks |
| [phelix001 Network](https://github.com/phelix001/epstein-network) | 19,154 FOIA documents with categorized entities |
| Google Civic Information API | Zip code → congressional district mapping |
| ProPublica Congress API | Current federal incumbents |
| FEC API | All filed federal candidates |

## Running What's Here

```bash
# Pipeline tests (55 tests, all passing)
pip install -r pipeline/requirements.txt
python -m pytest pipeline/tests/ -v

# Frontend (builds cleanly)
cd web && npm install && npm run dev
```

## Project Structure

```
know-before-you-vote/
├── pipeline/                    # Python data pipeline
│   ├── ingest/                  # Source database parsers (4 sources)
│   ├── candidates/              # Candidate API integrations
│   ├── crossref/                # Name matching & corroboration
│   ├── classify/                # Connection classification & citations
│   ├── publish/                 # Static JSON generator
│   └── tests/                   # 55 tests
├── web/                         # Next.js frontend
│   ├── src/app/                 # Pages (landing, results, methodology)
│   └── src/components/          # UI components
└── .github/workflows/           # CI/CD
```

## License

Public domain. Use it, fork it, build from it.

Original concept and architecture by W.J. Cornelius. Code scaffolding built with Claude.

---

**If you're interested in taking this on**, fork the repo and go. The [PLAN.md](PLAN.md) file has everything you need. If you have questions, open an issue.
