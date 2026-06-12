import duckdb
from pathlib import Path

DB_PATH = Path(__file__).parent / "f1.duckdb"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

con = duckdb.connect(str(DB_PATH), read_only=True)

marts = [
    "fact_lap_times",
    "fact_weather",
    "fact_championship_drivers",
    "fact_championship_teams",
    "dim_drivers",
    "dim_meetings",
    "dim_sessions",
    "fact_positions",
    "fact_sector_times",
    "fact_stints",
]

for mart in marts:
    out = OUTPUT_DIR / f"{mart}.parquet"
    con.execute(f"COPY main.{mart} TO '{out.as_posix()}' (FORMAT PARQUET)")
    print(f"✓ {mart}.parquet exportiert")

con.close()
print("\nExport abgeschlossen.")