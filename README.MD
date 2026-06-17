# F1 Analytics – End-to-End Datenpipeline

> Eine produktionsreife ELT-Pipeline für Formel-1-Telemetrie und Renndaten — von der REST-API-Anbindung bis zum interaktiven Power-BI-Dashboard — vollständig mit Open-Source-Technologien gebaut.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![dbt](https://img.shields.io/badge/dbt-1.11-orange)
![DuckDB](https://img.shields.io/badge/DuckDB-1.10-yellow)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-gold)
![CI/CD](https://img.shields.io/badge/GitHub%20Actions-wöchentlich-green)

---

## Was dieses Projekt macht

Jeden Montag nach einem Rennwochenende führt eine GitHub-Actions-Pipeline automatisch folgende Schritte aus:

1. Neue F1-Sessiondaten von der OpenF1-REST-API abrufen
2. Inkrementell in ein lokales DuckDB-Warehouse laden
3. Über ein dbt-Sternschema transformieren (Staging → Dims → Facts)
4. Datenqualität mit 69 automatisierten Tests validieren
5. Parquet-Dateien für Power BI exportieren

Das Ergebnis ist ein stets aktuelles Dashboard mit Rundenzeiten, Sektoranalysen, Reifenstrategien, WM-Standings und Wetterkorrelationen für die gesamte Saison 2026.

---

## Architektur

```
OpenF1 REST API  (10 Endpunkte)
        │
        ▼
Python ETL                    Inkrementelles Laden · Parallele Abfragen (4 Worker)
  openf1_etl.py               Retry-Logik · State-Tracking · Backfill-Unterstützung
        │
        ▼  Parquet → data/raw/
DuckDB Warehouse              mtime-basierte Änderungserkennung
  load_to_duckdb.py           Unveränderte Dateien werden übersprungen
        │
        ▼  raw schema
dbt Core                      Staging → Dims → Facts
  transform/f1_analytics/     69 Datentests · Referentielle Integrität · accepted_values
        │
        ▼  main schema
Parquet Export                Eine Datei pro Mart/Dim
  export_parquet.py
        │
        ▼  data/processed/
Power BI Dashboard            Sternschema · Live-Aktualisierung aus lokalem Parquet
```

**Stack:** Python · DuckDB · dbt Core · Power BI · GitHub Actions

---

## Technische Entscheidungen

### Inkrementelles Laden
Der ETL verfolgt verarbeitete `session_keys` in einer lokalen State-Datei (`.etl_state.json`). Bei jedem Lauf werden nur neue Sessions abgerufen — redundante API-Aufrufe über 10 Endpunkte werden vermieden. Ein `--backfill`-Flag ermöglicht die gezielte Nachladung einzelner Endpunkte ohne vollständigen Reload.

### Parallele API-Abfragen
Session-basierte Endpunkte werden gleichzeitig mit `ThreadPoolExecutor` und 4 Workern abgerufen, mit eigenem Retry/Backoff-Mechanismus pro Worker. Das reduziert die Ladezeit um ~4x bei gleichzeitiger Einhaltung der API-Rate-Limits.

### mtime-basierte Änderungserkennung
`load_to_duckdb.py` vergleicht Datei-Änderungszeitstempel vor dem Neuladen. Unveränderte Parquet-Dateien werden komplett übersprungen — die DuckDB-Ladevorgänge bleiben auch bei wachsender Tabellenanzahl schnell.

### Sternschema-Datenmodell
Statt alles in flache Fact-Tabellen zu denormalisieren, folgt die dbt-Mart-Schicht einem sauberen Sternschema. Power-BI-Beziehungen ersetzen redundante Joins, reduzieren das Datenvolumen und halten Dimensionsdaten (Fahrerbilder, Teamlogos) zentral an einem Ort.

### Datenqualität als Code
Jedes Staging-Modell hat dbt-Tests für `not_null`, `unique`, `relationships` (referentielle Integrität) und `accepted_values`. Eigene SQL-Tests prüfen Geschäftslogik wie negative Rundenzeiten oder ungültige Luftfeuchtewerte.

---

## Datenmodell

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

## Datenquellen

| Endpunkt | Raw-Tabelle | Zeilen (2026) | Beschreibung |
|---|---|---|---|
| `/sessions` | `raw.sessions` | 126 | Training, Qualifying, Rennen |
| `/meetings` | `raw.meetings` | 26 | Grand-Prix-Wochenenden |
| `/drivers` | `raw.drivers` | ~2.000 | Fahrerinfos pro Session |
| `/laps` | `raw.laps` | ~49.000 | Rundenzeiten pro Fahrer |
| `/weather` | `raw.weather` | ~12.000 | Streckenbedingungen |
| `/position` | `raw.positions` | ~46.000 | Fahrzeugpositionen während Sessions |
| `/stints` | `raw.stints` | — | Reifencompound & Stint-Daten |
| `/championship_drivers` | `raw.championship_drivers` | 154 | WM-Stand Fahrer nach jedem Rennen |
| `/championship_teams` | `raw.championship_teams` | 66 | WM-Stand Konstrukteure nach jedem Rennen |
| `/session_results` (abgeleitet) | `raw.session_results` | 789 | Endklassifikationen |

---

## Projektstruktur

```
f1-analytics/
├── ingestion/
│   └── openf1_etl.py              # ETL: inkrementelles Laden, parallele Abfragen, Backfill
├── warehouse/
│   ├── load_to_duckdb.py          # Laden: mtime-basierte Änderungserkennung
│   └── export_parquet.py          # Export: Marts → Parquet für Power BI
├── transform/f1_analytics/        # dbt-Projekt
│   ├── models/
│   │   ├── staging/               # stg_* — Rohdaten bereinigen & typisieren
│   │   └── marts/                 # dim_* + fact_* — Sternschema
│   ├── seeds/
│   │   └── driver_images.csv      # Eigene Fahrer- & Teambild-URLs
│   └── tests/                     # Eigene SQL-Tests (Geschäftslogik)
├── data/
│   ├── raw/                       # Parquet von API (gitignored)
│   └── processed/                 # dbt-Exporte für Power BI (gitignored)
└── .github/workflows/
    └── f1_pipeline.yml            # Wöchentliche CI/CD (Montag 06:00 UTC)
```

---

## Dashboard

Das Power-BI-Dashboard umfasst:

- Rundenzeitenvergleich pro Fahrer und Event
- Sektorzeiten (S1 / S2 / S3) im Detail
- Reifenstrategie — Compound-Nutzung und Stint-Längen
- WM-Stand (Fahrer & Konstrukteure) nach jedem Rennen
- Startaufstellung vs. Rennendergebnis
- Wetterbedingungen und Korrelation mit Rundenzeiten
- Fahrerportraits und Teamlogos über eigene Bild-URLs

---

## Lokale Ausführung

### Voraussetzungen

```bash
pip install duckdb pandas pyarrow requests dbt-core dbt-duckdb
```

### Komplette Pipeline

```bash
# 1. Daten von OpenF1 API abrufen (inkrementell)
python ingestion/openf1_etl.py

# 2. In DuckDB laden
python warehouse/load_to_duckdb.py

# 3. Mit dbt transformieren
cd transform/f1_analytics
dbt run
dbt test

# 4. Nach Parquet exportieren
python warehouse/export_parquet.py
```

### Einzelne Endpunkte nachladen

```bash
python ingestion/openf1_etl.py --backfill stints championship_drivers
```

### Daten erkunden

```bash
duckdb warehouse/f1.duckdb
# dann: SELECT * FROM raw.laps LIMIT 10;
```

### dbt Lineage & Dokumentation

```bash
cd transform/f1_analytics
dbt docs generate
dbt docs serve
```

---

## Automatisierte Pipeline (CI/CD)

GitHub Actions startet jeden **Montag um 06:00 UTC** nach Rennwochenenden:

```
Zeitgesteuerte Ausführung
        ↓
openf1_etl.py           # Nur neue Sessions abrufen
        ↓
load_to_duckdb.py       # Nur geänderte Dateien neu laden
        ↓
dbt run                 # Betroffene Modelle neu bauen
        ↓
dbt test                # 69 Datentests validieren
        ↓
export_parquet.py       # Power-BI-Quelldateien aktualisieren
```

Manueller Start jederzeit über `workflow_dispatch` möglich.

---

## Lizenz

MIT
