from db import get_db
import pandas as pd

with get_db() as con:
    df = pd.read_sql_query("SELECT * FROM raw_levels", con)

bad_bpm = df[pd.to_numeric(df["bpm"], errors="coerce").isna()]
bad_tiles = df[pd.to_numeric(df["tilecount"], errors="coerce").isna()]

print(f"{len(df)} total rows")
print(f"{len(bad_bpm)} rows with a bad bpm value")
print(f"{len(bad_tiles)} rows with a bad tilecount value")
print(bad_bpm[["id", "bpm"]].head(10))
print(bad_tiles[["id", "tilecount"]].head(10))