# Know Before You Vote: Development Plan

## Context

The DOJ released 3.5 million pages of Epstein documents and announced no further prosecutions. Citizen developers have built tools to explore this data (JMail, Epstein Doc Explorer, etc.), but none connect the data to a voter's actual ballot. This project bridges that gap: enter your zip code, see your candidates, see which ones have documented Epstein connections with links to primary source documents.

The system must be fully automated (no manual curation), self-updating, and correct from day one. Real careers are at stake — a false positive is an unjust accusation, and a false negative lets complicity hide. The multi-source corroboration requirement (2+ independent databases must agree) replaces human curation as the quality gate.

**Design constraints:**
- Ongoing costs must stay under ~$15/month (all free-tier APIs where possible)
- Heavy processing should happen in GitHub Actions, not locally
- Google Civic Representatives API was discontinued March 2025 — must use `divisionsByAddress` + other sources for candidate data
- Ballotpedia has no free API — must use free alternatives for candidate lists

---

## Current Status

**Phases 1-2 are complete. Phases 3-9 need a developer.**

| Phase | Status | Description |
|-------|--------|-------------|
| 1. Scaffolding | DONE | Repo, CI/CD, project structure, Next.js app |
| 2. Entity Ingestion | DONE | All 4 source database parsers, merge logic, 55 tests passing |
| 3. Candidate Pipeline | CODE WRITTEN, NEEDS TESTING | API modules built, need API keys + live testing |
| 4. Cross-Referencing | CODE WRITTEN, NEEDS TESTING | Fuzzy match + AI disambiguation modules built |
| 5. Classification | CODE WRITTEN, NEEDS TESTING | Classifier + citation generator built |
| 6. Frontend | SCAFFOLDED | Pages + components exist, need real data wiring |
| 7. Automation | NOT STARTED | GitHub Actions workflows for weekly/daily updates |
| 8. Pre-Launch Audit | NOT STARTED | Human review of all displayed connections |
| 9. Launch | NOT STARTED | Domain, deployment, soft launch |

---

## Prerequisites

1. **Get API keys** (all free):
   - Google Cloud Console: Civic Information API key
   - ProPublica Congress API key (https://www.propublica.org/datastore/api/propublica-congress-api)
   - FEC API key (https://api.data.gov/signup/)
   - Perplexity API key (https://docs.perplexity.ai/) — $5/month Pro or pay-per-query
   - Anthropic API key for Claude Haiku (disambiguation + classification)

---

## Architecture Overview

```
know-before-you-vote/
├── pipeline/                    # Python data pipeline (runs in GitHub Actions)
│   ├── ingest/                  # Download & parse source databases
│   │   ├── maxandrews.py        # Parse Epstein Doc Explorer SQLite (91 MB)
│   │   ├── lmsband.py           # Parse LMSBAND SQLite (835 MB)
│   │   ├── svetimfm.py          # Parse SvetimFM entity analysis JSON
│   │   └── phelix.py            # Parse phelix001 JSON data
│   ├── candidates/              # Build current candidate database
│   │   ├── civic_api.py         # Google Civic divisionsByAddress
│   │   ├── propublica.py        # ProPublica Congress API (federal incumbents)
│   │   ├── fec.py               # FEC API (all filed candidates)
│   │   └── merge.py             # Merge into unified candidate list
│   ├── crossref/                # Match entities to candidates
│   │   ├── normalize.py         # Name normalization (Bill/William, Jr/Sr, etc.)
│   │   ├── match.py             # Fuzzy matching + AI disambiguation
│   │   └── corroborate.py       # Multi-source verification (2+ sources required)
│   ├── classify/                # Connection level classification
│   │   ├── classifier.py        # AI categorization (Direct/Financial/Contact/Institutional)
│   │   └── citations.py         # Generate source citations with document links
│   ├── publish/                 # Generate frontend data
│   │   └── generate_json.py     # Output static JSON for the website
│   └── tests/                   # 55 tests and growing
├── web/                         # Next.js frontend (deployed to Vercel)
│   ├── src/app/                 # Pages (landing, results, candidate detail, methodology)
│   └── src/components/          # UI components (CandidateCard, ConnectionBadge, etc.)
├── .github/workflows/           # CI/CD (test.yml working, others to be built)
└── README.md
```

---

## Development Phases (Detailed)

### Phase 3: Candidate Data Pipeline
**Goal: For any US zip code, return the list of candidates on that ballot**

The code modules are already written. They need API keys and live testing.

1. **`candidates/civic_api.py`** — Call Google Civic `divisionsByAddress` to get OCD-IDs for congressional district
2. **`candidates/propublica.py`** — Query ProPublica for current federal incumbents by state/district
3. **`candidates/fec.py`** — Query FEC for all filed candidates (captures challengers)
4. **`candidates/merge.py`** — Deduplicate and merge into unified candidate list
5. **`publish/districts.json`** — Pre-compute zip code → district mapping using Census ZCTA-to-congressional-district crosswalk

**Test checkpoint:**
- Test with 10 diverse zip codes (urban, rural, split-district, territories)
- Verify candidate lists match Ballotpedia (manual spot-check)
- Test edge cases: territories (PR, GU), zip codes spanning multiple districts

---

### Phase 4: Cross-Referencing & Verification (The Critical Step)
**Goal: Match candidates to Epstein entity database with multi-source corroboration**

1. **Name normalization** — Lowercase, strip titles (Sen., Rep., Hon.), expand nicknames (Bill→William), handle suffixes (Jr., Sr., III). 90+ nickname mappings already built.

2. **Two-phase matching:**
   - **Phase A**: Fuzzy string matching (thefuzz, threshold ≥92)
   - **Phase B**: AI disambiguation via Claude Haiku with biographical context. "Is this the same person? YES/NO/UNCERTAIN." Only YES advances.

3. **Multi-source corroboration:**
   - ≥3 sources = HIGH confidence (displayed fully)
   - 2 sources = MEDIUM confidence (displayed with caveat)
   - 1 source = NOT DISPLAYED (too high risk of noise)
   - 0 sources = "No documented connections found"

**Test checkpoint — MOST IMPORTANT:**
- Known positive test (well-documented connections)
- Known negative test (common names, no connections)
- Name collision test (AI disambiguation must reject false matches)
- Threshold test (single-source matches never appear)
- Cross-party balance test
- Null test (candidates with zero mentions)

---

### Phase 5: Connection Classification & Citation
**Goal: Categorize connection level and generate source citations**

| Level | Criteria |
|-------|----------|
| **Direct** | Named as participant: flight logs, victim testimony, criminal proceedings |
| **Contact** | Documented communication: emails, event attendance, phone records |
| **Financial** | Campaign donations from Epstein or documented associates |
| **Institutional** | Authority over investigations, took no action |

The AI classifies based ONLY on documentary evidence, never inference. Every citation includes a `document_url` that must resolve to an actual public record.

---

### Phase 6: Frontend
**Goal: Clean, mobile-first website any voter can use**

Scaffold is built. Needs wiring to pipeline-generated JSON:
- Landing page: zip code input
- Results page: candidates with connection badges
- Candidate detail: full evidence display with source links
- Methodology: data sources, thresholds, legal disclaimers

---

### Phase 7: GitHub Actions Automation
**Goal: Self-updating, no human intervention**

- `weekly-update.yml` — Full pipeline run every Sunday
- `daily-candidates.yml` — Candidate list refresh during election season
- `news-monitor.yml` — Perplexity API for new Epstein revelations
- `test.yml` — Tests on every push (already working)
- `deploy.yml` — Vercel deployment on data changes

---

### Phase 8: Pre-Launch Audit
- Human review of every displayed connection
- Link verification (all document URLs resolve)
- Cross-party balance check
- Legal disclaimer review
- Red team testing (common names, edge cases)

---

### Phase 9: Launch
- Domain registration (~$12/year)
- Soft launch to civic tech and transparency communities
- GitHub Issues for public error reporting

---

## Estimated Monthly Costs

| Service | Cost |
|---------|------|
| Perplexity API (news monitoring) | ~$5-8/mo |
| Claude Haiku (disambiguation + classification) | ~$1-2/mo |
| GitHub Actions | ~$2-4/mo |
| Vercel hosting | Free tier |
| Google Civic, ProPublica, FEC APIs | Free |
| **Total** | **~$9-15/month** |

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| False positive | 2+ source corroboration; AI disambiguation; conservative classification; pre-launch audit |
| False negative | Acceptable — better to miss one than flag one falsely; improves as sources grow |
| Source database offline | Cache in GitHub Actions artifacts; log availability |
| API pricing changes | Abstract behind wrappers; swap providers |
| Legal threat (SLAPP) | All public records; no accusations; primary source links; First Amendment; anti-SLAPP |
| NER noise | Multi-source corroboration filters single-source noise by design |
