import duckdb
import os
from pathlib import Path

# Verbindung zur DuckDB
con = duckdb.connect("warehouse/f1.duckdb")

# Raw Schema anlegen
con.execute("CREATE SCHEMA IF NOT EXISTS raw")

# Parquet-Files in DuckDB laden
raw_path = Path("data/raw")

files = {
    "drivers":  "f1_drivers_2026.parquet",
    "laps":     "f1_laps_2026.parquet",
    "meetings": "f1_meetings_2026.parquet",
    "sessions": "f1_sessions_2026.parquet",
    "weather":  "f1_weather_2026.parquet",
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

# Marts als Parquet exportieren für Power BI
os.makedirs("data/processed", exist_ok=True)

con = duckdb.connect("warehouse/f1.duckdb", read_only=True)
marts = ["fact_race_results", "fact_lap_times", "fact_weather"]

for mart in marts:
    con.execute(f"""
        COPY main.{mart} TO 'data/processed/{mart}.parquet' (FORMAT PARQUET)
    """)
    print(f"✓ {mart}.parquet exportiert")

con.close()
print("\nPipeline abgeschlossen.")