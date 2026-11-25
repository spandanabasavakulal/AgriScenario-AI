
import pandas as pd

from core.data_loader import load_agriculture_data

df = load_agriculture_data()

# Convert numerical columns
columns = [
    "area_1000_ha",
    "production_1000_t",
    "yield_kg_per_ha"
]

for col in columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Identify different data conditions
area_zero = df["area_1000_ha"] == 0
area_positive = df["area_1000_ha"] > 0

production_missing = df["production_1000_t"].isna()
yield_missing = df["yield_kg_per_ha"].isna()

production_zero = df["production_1000_t"] == 0
yield_zero = df["yield_kg_per_ha"] == 0

print("\n========== ZERO AREA ANALYSIS ==========")

print("Total zero-area records:", area_zero.sum())

print(
    "Zero area with missing production:",
    (area_zero & production_missing).sum()
)

print(
    "Zero area with available production:",
    (area_zero & ~production_missing).sum()
)

print(
    "Zero area with positive production:",
    (area_zero & (df["production_1000_t"] > 0)).sum()
)

print("\n========== MISSING DATA ANALYSIS ==========")

print(
    "Production and yield both missing:",
    (production_missing & yield_missing).sum()
)

print(
    "Production missing but yield available:",
    (production_missing & ~yield_missing).sum()
)

print(
    "Yield missing but production available:",
    (~production_missing & yield_missing).sum()
)

print(
    "Missing production/yield with positive area:",
    (
        area_positive &
        (production_missing | yield_missing)
    ).sum()
)

print("\n========== ZERO PRODUCTION/YIELD ==========")

print(
    "Zero production with positive area:",
    (area_positive & production_zero).sum()
)

print(
    "Zero yield with positive area:",
    (area_positive & yield_zero).sum()
)

print("\n========== SAMPLE ZERO-AREA RECORDS ==========")

print(
    df.loc[
        area_zero,
        [
            "state",
            "district",
            "year",
            "crop",
            "area_1000_ha",
            "production_1000_t",
            "yield_kg_per_ha"
        ]
    ].head(15).to_string(index=False)
)

