
from core.data_loader import load_agriculture_data
import pandas as pd

df = load_agriculture_data()

for col in [
    "area_1000_ha",
    "production_1000_t",
    "yield_kg_per_ha"
]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

print("\nZERO AREA RECORDS BY CROP")

print(
    df[df["area_1000_ha"] == 0]
    .groupby("crop")
    .size()
    .sort_values(ascending=False)
    .head(15)
)

print("\nZERO AREA RECORDS BY YEAR")

print(
    df[df["area_1000_ha"] == 0]
    .groupby("year")
    .size()
)

print("\nZERO AREA WITH POSITIVE PRODUCTION")

print(
    df[
        (df["area_1000_ha"] == 0) &
        (df["production_1000_t"] > 0)
    ][
        ["state", "district", "year", "crop",
         "area_1000_ha", "production_1000_t",
         "yield_kg_per_ha"]
    ].head(20).to_string(index=False)
)
