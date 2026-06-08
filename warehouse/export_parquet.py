import duckdb
import os

os.makedirs("data/processed", exist_ok=True)

con = duckdb.connect("warehouse/f1.duckdb", read_only=True)
marts = ["fact_race_results", "fact_lap_times", "fact_weather"]

for mart in marts:
    con.execute(f"""
        COPY main.{mart} TO 'data/processed/{mart}.parquet' (FORMAT PARQUET)
    """)
    print(f"✓ {mart}.parquet exportiert")

con.close()
print("\nExport abgeschlossen.")