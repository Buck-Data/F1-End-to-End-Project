import requests
import pandas as pd
from pathlib import Path

url = "https://api.openf1.org/v1/drivers"
params = {}

response = requests.get(url, params=params)

print(response.status_code)
print(response.json()[0])

data = response.json()
df = pd.DataFrame(data)

output_dir = Path("data/raw")
output_dir.mkdir(parents=True, exist_ok=True)

df.to_parquet(output_dir / "f1_drivers_2026.parquet", index=False)

df_check = pd.read_parquet(output_dir / "f1_drivers_2026.parquet")
print(df_check.shape)
