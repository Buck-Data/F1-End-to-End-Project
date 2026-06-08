import duckdb
import pandas as pd
from pathlib import Path

con = duckdb.connect("warehouse/f1.duckdb")
con.execute("CREATE SCHEMA IF NOT EXISTS raw")

raw_path = Path("data/raw")

files = {
    "drivers":  "f1_drivers_2026.parquet",
    "laps":     "f1_laps_2026.parquet",
    "meetings": "f1_meetings_2026.parquet",
    "sessions": "f1_sessions_2026.parquet",
    "weather":  "f1_weather_2026.parquet",
    "positions": "f1_positions_2026.parquet",
}

for table, filename in files.items():
    filepath = raw_path / filename
    con.execute(f"""
        CREATE OR REPLACE TABLE raw.{table} AS
        SELECT * FROM read_parquet('{filepath}')
    """)
    count = con.execute(f"SELECT COUNT(*) FROM raw.{table}").fetchone()[0]
    print(f"✓ raw.{table}: {count} Zeilen")

con.close()
print("\nRaw-Load abgeschlossen.")