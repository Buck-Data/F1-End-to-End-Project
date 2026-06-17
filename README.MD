# F1 Analytics – End-to-End Data Pipeline

> A production-grade ELT pipeline for Formula 1 telemetry and race data — from REST API ingestion to an interactive Power BI dashboard — built entirely with open-source tooling.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![dbt](https://img.shields.io/badge/dbt-1.11-orange)
![DuckDB](https://img.shields.io/badge/DuckDB-1.10-yellow)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-gold)
![CI/CD](https://img.shields.io/badge/GitHub%20Actions-weekly-green)

---

## What This Project Does

Every Monday after a race weekend, a GitHub Actions pipeline automatically:

1. Fetches new F1 session data from the OpenF1 REST API
2. Loads it incrementally into a local DuckDB warehouse
3. Transforms it through a dbt star schema (staging → dims → facts)
4. Validates data quality with 60+ automated tests
5. Exports Parquet files ready for Power BI

The result is an always-up-to-date dashboard covering lap times, sector analysis, tyre strategies, championship standings, and weather correlations across the entire 2026 season.

---

## Architecture

```
OpenF1 REST API  (10 endpoints)
        │
        ▼
Python ETL                    incremental loading · parallel fetching (4 workers)
  openf1_etl.py               retry logic · state tracking · backfill support
        │
        ▼  Parquet → data/raw/
DuckDB Warehouse              mtime-based change detection
  load_to_duckdb.py           skips unchanged files on reload
        │
        ▼  raw schema
dbt Core                      staging → dims → facts
  transform/f1_analytics/     69 data tests · referential integrity · accepted_values
        │
        ▼  main schema
Parquet Export                one file per mart/dim
  export_parquet.py
        │
        ▼  data/processed/
Power BI Dashboard            star schema · live refresh from local Parquet
```

**Stack:** Python · DuckDB · dbt Core · Power BI · GitHub Actions

---

## Key Engineering Decisions

### Incremental Loading
The ETL tracks processed `session_keys` in a local state file (`.etl_state.json`). On each run, only new sessions are fetched — avoiding redundant API calls across 10 endpoints. A `--backfill` flag allows selective re-ingestion of specific endpoints without a full reload.

### Parallel API Fetching
Session-level endpoints are fetched concurrently using `ThreadPoolExecutor` with 4 workers and per-worker retry/backoff logic. This reduces ingestion time by ~4x while staying within API rate limits.

### mtime-Based Change Detection
`load_to_duckdb.py` compares file modification timestamps before reloading. Unchanged Parquet files are skipped entirely, keeping DuckDB loads fast even with a growing number of tables.

### Star Schema Data Model
Rather than denormalizing everything into flat fact tables, the dbt mart layer follows a proper star schema. Power BI relationships replace redundant joins, reducing data volume and keeping dimension data (driver images, team logos) in one place.

### Data Quality as Code
Every staging model has dbt tests for `not_null`, `unique`, `relationships` (referential integrity), and `accepted_values`. Custom SQL tests catch business-logic violations like negative lap times or out-of-range humidity values.

---

## Data Model

```
dim_drivers ────────────────────────────────────┐
  driver_number (PK)                            │
  full_name · name_acronym                      │
  team_name · team_colour                       ├──► fact_lap_times
  image_url · teamshot_url                      │    fact_sector_times
  country_code                                  │    fact_stints
                                                │    fact_positions
dim_sessions ───────────────────────────────────┤    fact_championship_drivers
  session_key (PK)                              │
  session_name · session_type                   │
  meeting_key (FK)                              │
                                                │
dim_meetings ───────────────────────────────────┘
  meeting_key (PK)
  meeting_name · circuit_short_name
  country_name · date_start
```

---

## Data Sources

| Endpoint | Raw Table | Rows (2026) | Description |
|---|---|---|---|
| `/sessions` | `raw.sessions` | 126 | Practice, Qualifying, Race sessions |
| `/meetings` | `raw.meetings` | 26 | Grand Prix weekends |
| `/drivers` | `raw.drivers` | ~2000 | Driver info per session |
| `/laps` | `raw.laps` | ~49000 | Lap times per driver |
| `/weather` | `raw.weather` | ~12000 | Track conditions |
| `/position` | `raw.positions` | ~46000 | Car positions during sessions |
| `/stints` | `raw.stints` | — | Tyre compound & stint data |
| `/championship_drivers` | `raw.championship_drivers` | 154 | WDC standings per race |
| `/championship_teams` | `raw.championship_teams` | 66 | WCC standings per race |
| `/session_results` (derived) | `raw.session_results` | 789 | Final classifications |

---

## Project Structure

```
f1-analytics/
├── ingestion/
│   └── openf1_etl.py              # ETL: incremental loading, parallel fetch, backfill
├── warehouse/
│   ├── load_to_duckdb.py          # Load: mtime-based change detection
│   └── export_parquet.py          # Export: marts → Parquet for Power BI
├── transform/f1_analytics/        # dbt project
│   ├── models/
│   │   ├── staging/               # stg_* — clean & type-cast raw data
│   │   └── marts/                 # dim_* + fact_* — star schema
│   ├── seeds/
│   │   └── driver_images.csv      # Custom driver & team image URLs
│   └── tests/                     # Custom SQL tests (business logic)
├── data/
│   ├── raw/                       # Parquet from API (gitignored)
│   └── processed/                 # dbt exports for Power BI (gitignored)
└── .github/workflows/
    └── f1_pipeline.yml            # Weekly CI/CD (Monday 06:00 UTC)
```

---

## Dashboard

The Power BI dashboard covers:

- Lap time comparison per driver and event
- Sector times (S1 / S2 / S3) breakdown
- Tyre strategy — compound usage and stint lengths
- Championship standings (drivers & constructors) after each race
- Starting grid vs. final race result
- Weather conditions and correlation with lap times
- Driver portraits and team logos via custom image URLs

---

## How to Run Locally

### Prerequisites

```bash
pip install duckdb pandas pyarrow requests dbt-core dbt-duckdb
```

### Full Pipeline

```bash
# 1. Fetch data from OpenF1 API (incremental)
python ingestion/openf1_etl.py

# 2. Load into DuckDB
python warehouse/load_to_duckdb.py

# 3. Transform with dbt
cd transform/f1_analytics
dbt run
dbt test

# 4. Export to Parquet
python warehouse/export_parquet.py
```

### Backfill a Specific Endpoint

```bash
python ingestion/openf1_etl.py --backfill stints championship_drivers
```

### Explore the Data

```bash
duckdb warehouse/f1.duckdb
# then: SELECT * FROM raw.laps LIMIT 10;
```

### dbt Lineage & Docs

```bash
cd transform/f1_analytics
dbt docs generate
dbt docs serve
```

---

## Automated Pipeline (CI/CD)

GitHub Actions triggers every **Monday at 06:00 UTC** after race weekends:

```
Schedule trigger
      ↓
openf1_etl.py       # fetch new sessions only
      ↓
load_to_duckdb.py   # reload changed files only
      ↓
dbt run             # rebuild affected models
      ↓
dbt test            # validate 69 data tests
      ↓
export_parquet.py   # refresh Power BI source files
```

Manual trigger available via `workflow_dispatch` for on-demand runs.

---

## License

MIT
