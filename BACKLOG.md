# 📋 F1 Analytics – Project Backlog

## 🔴 High Priority (Pipeline & Daten)

- [ ] **GitHub Actions fixen & validieren**
  - dbt profiles.yml Pfad auf CI-Umgebung abstimmen via DUCKDB_PATH Umgebungsvariable
  - Erfolgreichen End-to-End Run auf GitHub bestätigen

- [ ] **Incremental Loading im Extract**
  - Bereits geladene `session_keys` aus DuckDB lesen
  - Nur neue Sessions abfragen die seit letztem Run dazugekommen sind
  - Reduziert Pipeline-Laufzeit von ~45min auf ~5min nach Rennwochenende

- [ ] **Incremental dbt Models**
  - `materialized='incremental'` für `fct_lap_times` und `fct_race_results`
  - Nur neue Zeilen einfügen statt alles neu bauen

- [ ] **Fehlende Tabellen in dbt integrieren**
  - `f1_starting_grid_2026` → `stg_starting_grid` + in Mart einbauen
  - `f1_session_results_2026` → `stg_session_results` + in Mart einbauen
  - `fct_race_results` mit echten Positionen/Ergebnissen anreichern

- [ ] **Headshot URLs ersetzen**
  - dbt Seed anlegen (`seeds/driver_headshots.csv`) mit `driver_number` + GitHub-hosted URL
  - In `stg_drivers` joinen und API-URLs überschreiben
  - Saubere, qualitativ hochwertige Fahrerbilder im Dashboard

- [ ] **API Felder prüfen**
  - Nur notwendige Spalten aus OpenF1 API ziehen
  - Unnötige Felder bereits im Extract oder Staging Model rauswerfen

- [ ] **dbt Sources definieren**
  - `sources.yml` anlegen statt direkt `raw.table` zu referenzieren
  - Macht Lineage Graph vollständiger (raw layer sichtbar)

- [ ] **YEAR nicht hardcoded**
  - Dynamisch aus aktuellem Jahr ableiten oder via Config-Datei steuern
  - Verhindert manuelle Anpassung bei Saisonwechsel

---

## 🟡 Medium Priority (Qualität & Robustheit)

- [ ] **Parallelisierung im Extract**
  - Mehrere Sessions gleichzeitig abfragen via `threading` oder `asyncio`
  - Laufzeit drastisch reduzieren bei vollem Season-Load

- [ ] **Logging statt print-Statements**
  - Python `logging` Modul einführen
  - Logfile schreiben statt nur Konsolenausgabe
  - Bei API-Ausfall: sauberer Exit Code 1

- [ ] **Retry-Logik verbessern**
  - Aktuell nur bei 429 – sollte auch bei Netzwerkfehlern und Timeouts greifen
  - Exponential Backoff ausbauen

- [ ] **Pydantic Schema-Validierung**
  - API-Response validieren bevor Daten in DuckDB landen
  - Frühzeitig erkennen wenn OpenF1 API das Schema ändert

- [ ] **dbt Tests erweitern**
  - `accepted_values` für `session_type` (Race, Qualifying, Practice)
  - `relationships` Tests zwischen Marts
  - `not_null` auf alle kritischen Schlüsselspalten
  - `freshness` Tests – warnt wenn Daten älter als X Stunden

- [ ] **dbt schema.yml vervollständigen**
  - Alle Spalten in allen Models dokumentieren
  - Konsistente Beschreibungen durchgehend

- [ ] **Pipeline-Status Badge im README**
  - GitHub Actions Badge einbinden
  - Zeigt live ob Pipeline grün oder rot ist

- [ ] **`requirements.txt` mit fixen Versionen**
  - Reproduzierbare Umgebung sicherstellen
  - Verhindert Breaking Changes durch Paket-Updates

- [ ] **Config-Datei anlegen**
  - `config.yml` für Konstanten wie YEAR, DELAY, MAX_RETRIES
  - Keine hardcodierten Werte mehr im Skript

- [ ] **`openf1_etl.py` umbenennen**
  - → `openf1_extract.py` (ELT, nicht ETL)

- [ ] **`derive_only.py` löschen**
  - Temporäres Skript – Logik ist in `openf1_extract.py` integriert

- [ ] **`dbt_project.yml` bereinigen**
  - Example-Warnung entfernen (unused configuration path)

---

## 🟢 Low Priority (Portfolio & Präsentation)

- [ ] **Power BI Dashboard fertigstellen**
  - Lap time Vergleich pro Fahrer und Event
  - Sektoranalyse (S1, S2, S3)
  - Starting Grid vs. Race Result
  - Wetter am Renntag
  - Team Performance Übersicht
  - Dark Canvas Design finalisieren

- [ ] **README finalisieren**
  - Architekturdiagramm einfügen (`docs/architecture.png`)
  - Lineage Graph Screenshot einfügen (`docs/lineage_graph.png`)
  - Power BI Dashboard Screenshot einfügen
  - Pipeline Status Badge einbinden

- [ ] **docs/ Ordner befüllen**
  - `architecture.png` – Architekturdiagramm exportieren
  - `lineage_graph.png` – Screenshot aus dbt docs
  - `dashboard_preview.png` – Power BI Screenshot

- [ ] **GitHub Repo aufräumen**
  - Topics/Tags setzen: `dbt`, `duckdb`, `power-bi`, `formula1`, `elt-pipeline`
  - Description auf GitHub setzen

- [ ] **dbt Snapshots einführen**
  - Slowly Changing Dimensions abbilden
  - Beispiel: Fahrer der das Team wechselt (historisch nachvollziehbar)

- [ ] **Intermediate dbt Layer**
  - Layer zwischen Staging und Marts für komplexe Transformationen
  - Bessere Modularität bei wachsender Modellanzahl

---

## 💡 Nice to Have (Erweiterungen)

- [ ] **MotherDuck Migration**
  - DuckDB in die Cloud migrieren
  - Power BI liest direkt aus MotherDuck statt lokalem Parquet
  - Echter Cloud Data Stack ohne lokale Abhängigkeit

- [ ] **Dashboard auf Power BI Service publishen**
  - Öffentlich zugänglicher Link für Portfolio
  - Automatischer Refresh via Gateway

- [ ] **Historische Saisons laden**
  - YEAR Parameter auf mehrere Saisons ausweiten
  - Historische Vergleiche im Dashboard ermöglichen

- [ ] **Parallelisierung via GitHub Actions Matrix**
  - Mehrere Saisons parallel laden
  - Fortgeschrittenes CI/CD Pattern

- [ ] **Airflow DAG**
  - Als Alternative zu GitHub Actions für Olist-Folgeprojekt
  - Zeigt Orchestrierungs-Know-how mit Industriestandard-Tool

---

## ✅ Erledigt

- [x] Projektstruktur angelegt (`ingestion/`, `warehouse/`, `transform/`, `data/`, `docs/`)
- [x] DuckDB als lokales Warehouse eingerichtet
- [x] dbt Core Projekt initialisiert und mit DuckDB verbunden
- [x] 5 Staging Models gebaut (`stg_drivers`, `stg_sessions`, `stg_laps`, `stg_meetings`, `stg_weather`)
- [x] 3 Mart Models gebaut (`fct_race_results`, `fct_lap_times`, `fct_weather`)
- [x] dbt Tests und Dokumentation mit Lineage Graph
- [x] Parquet Export für Power BI
- [x] Alle drei Tabellen in Power BI geladen
- [x] GitHub Actions Workflow angelegt (`f1_pipeline.yml`)
- [x] Projekt auf GitHub gepusht (`Buck-Data/F1-End-to-End-Project`)
- [x] `.gitignore` konfiguriert (DuckDB, Parquet, venv ausgeschlossen)
- [x] README und Backlog erstellt
