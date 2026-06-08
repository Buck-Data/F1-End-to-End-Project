# 🏎️ F1 Analytics – End-to-End Data Pipeline

> An end-to-end ELT pipeline for Formula 1 data using the OpenF1 API – from raw API ingestion to an interactive Power BI dashboard, built with modern data stack tooling.

![Pipeline](docs/architecture.png)
<!-- Screenshot des Architekturdiagramms hier einfügen -->

---

## 🏗️ Architecture

```
OpenF1 API (REST)
      │
      ▼
Python Extract           → requests, rate-limit handling, session filtering
      │
      ▼
DuckDB (local warehouse) → raw schema: drivers, sessions, meetings, laps, weather, positions
      │
      ▼
dbt Core (transform)     → staging → marts (fct_race_results, fct_lap_times, fct_weather)
      │
      ▼
Parquet Export           → data/processed/
      │
      ▼
Power BI Dashboard       → interactive race analysis, lap times, weather correlation
```

**Stack:** Python · DuckDB · dbt Core · Power BI · GitHub Actions

---

## 📁 Project Structure

```
f1-analytics/
├── ingestion/
│   └── openf1_etl.py          # Extract: API calls, rate limiting, parquet output
├── warehouse/
│   └── load_to_duckdb.py      # Load: raw parquet → DuckDB raw schema + mart export
├── transform/
│   └── f1_analytics/          # dbt project
│       └── models/
│           ├── staging/        # stg_drivers, stg_sessions, stg_laps, stg_meetings, stg_weather
│           └── marts/          # fct_race_results, fct_lap_times, fct_weather
├── data/
│   ├── raw/                   # Parquet files from API (gitignored)
│   └── processed/             # dbt mart exports for Power BI (gitignored)
├── docs/                      # Architecture diagram, screenshots
└── .github/workflows/
    └── f1_pipeline.yml        # CI/CD: automated pipeline every Monday
```

---

## ⚙️ Pipeline

### Data Flow

| Phase | Tool | Description |
|-------|------|-------------|
| Extract | Python | Fetches data from OpenF1 API per session, handles rate limits (429) and retries |
| Load | DuckDB | Stores raw parquet files into `raw` schema without transformation |
| Transform | dbt Core | Staging layer cleans and standardizes; Mart layer joins and enriches |
| Export | DuckDB | Marts exported as Parquet for Power BI consumption |
| Visualize | Power BI | Interactive dashboard reading from processed Parquet files |

### dbt Lineage

![dbt Lineage Graph](docs/lineage_graph.png)
<!-- Screenshot des dbt docs Lineage Graphs hier einfügen -->

---

## 🤖 Automated Pipeline (CI/CD)

GitHub Actions runs the full pipeline every **Monday at 06:00 UTC** (after race weekends):

```
Push / Schedule trigger
        │
        ▼
python ingestion/openf1_etl.py     # Extract new race data
        │
        ▼
python warehouse/load_to_duckdb.py # Load into DuckDB
        │
        ▼
dbt run                             # Transform: staging + marts
        │
        ▼
dbt test                            # Validate: not_null, unique tests
```

---

## 🚀 How to Run Locally

### Prerequisites

```bash
pip install duckdb pandas pyarrow requests dbt-core dbt-duckdb
```

### 1. Extract data from OpenF1 API

```bash
python ingestion/openf1_etl.py
```

### 2. Load into DuckDB & export marts

```bash
python warehouse/load_to_duckdb.py
```

### 3. Run dbt transformations

```bash
cd transform/f1_analytics
dbt run
dbt test
```

### 4. View dbt documentation & lineage

```bash
dbt docs generate
dbt docs serve
```

### 5. Open Power BI

Open `F1.pbix` and refresh data – reads from `data/processed/`.

---

## 📊 Data Sources

| Table | Source | Description |
|-------|--------|-------------|
| `drivers` | OpenF1 `/drivers` | Driver info per session |
| `meetings` | OpenF1 `/meetings` | Grand Prix events (e.g. Monaco GP) |
| `sessions` | OpenF1 `/sessions` | FP1, FP2, FP3, Qualifying, Race |
| `laps` | OpenF1 `/laps` | Lap times per driver per session |
| `weather` | OpenF1 `/weather` | Track conditions per session |
| `positions` | OpenF1 `/position` | Driver positions → starting grid & results |

---

## 📈 Dashboard

The Power BI dashboard covers:

- Lap time comparison per driver and event
- Sector analysis (S1, S2, S3)
- Starting grid vs. race result
- Weather conditions on race day
- Team performance overview

---

## 🗂️ Status

> **Season:** 2026 (live – updates every Monday via GitHub Actions)

---

## 📝 License

MIT
