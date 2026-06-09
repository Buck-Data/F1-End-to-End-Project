import json
import os
import duckdb
from pathlib import Path

DB_PATH = Path(os.environ.get("DUCKDB_PATH", Path(__file__).parent / "f1.duckdb"))
RAW_PATH = Path(__file__).parent.parent / "data" / "raw"
STATE_FILE = Path(__file__).parent / ".duckdb_state.json"

FILES = {
    "drivers":        "f1_drivers_2026.parquet",
    "laps":           "f1_laps_2026.parquet",
    "meetings":       "f1_meetings_2026.parquet",
    "sessions":       "f1_sessions_2026.parquet",
    "weather":        "f1_weather_2026.parquet",
    "positions":      "f1_positions_2026.parquet",
    "starting_grid":  "f1_starting_grid_2026.parquet",
    "session_results": "f1_session_results_2026.parquet",
}


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"mtimes": {}}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def main():
    state = load_state()
    stored_mtimes = state["mtimes"]

    con = duckdb.connect(str(DB_PATH))
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")

    loaded, skipped = 0, 0
    new_mtimes = dict(stored_mtimes)

    for table, filename in FILES.items():
        filepath = RAW_PATH / filename
        if not filepath.exists():
            print(f"[SKIP] raw.{table} — Datei nicht gefunden")
            skipped += 1
            continue

        current_mtime = filepath.stat().st_mtime
        if stored_mtimes.get(filename) == current_mtime:
            count = con.execute(f"SELECT COUNT(*) FROM raw.{table}").fetchone()[0]
            print(f"[--]   raw.{table}: unverändert ({count} Zeilen)")
            skipped += 1
            continue

        con.execute(f"""
            CREATE OR REPLACE TABLE raw.{table} AS
            SELECT * FROM read_parquet('{filepath.as_posix()}')
        """)
        count = con.execute(f"SELECT COUNT(*) FROM raw.{table}").fetchone()[0]
        print(f"[OK]   raw.{table}: {count} Zeilen geladen")
        new_mtimes[filename] = current_mtime
        loaded += 1

    con.close()
    save_state({"mtimes": new_mtimes})
    print(f"\nFertig: {loaded} Tabellen neu geladen, {skipped} übersprungen.")


if __name__ == "__main__":
    main()
