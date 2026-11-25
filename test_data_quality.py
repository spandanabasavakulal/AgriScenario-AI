
import pandas as pd
import numpy as np

from core.data_loader import load_agriculture_data

df = load_agriculture_data()

print("\n========== ORIGINAL DATASET ==========")
print("Shape:", df.shape)

print("\n========== MISSING VALUES ==========")
print(df.isnull().sum())

print("\n========== NUMERICAL CONVERSION ==========")

numeric_columns = [
    "year",
    "area_1000_ha",
    "production_1000_t",
    "yield_kg_per_ha"
]

for col in numeric_columns:

    converted = pd.to_numeric(df[col], errors="coerce")

    conversion_failures = (
        df[col].notna() & converted.isna()
    ).sum()

    print(f"\n{col}")
    print("Conversion failures:", conversion_failures)
    print("Minimum:", converted.min())
    print("Maximum:", converted.max())
    print("Negative values:", (converted < 0).sum())
    print("Zero values:", (converted == 0).sum())
    print("Infinite values:", np.isinf(
        converted.dropna()
    ).sum())

print("\n========== YEAR DISTRIBUTION ==========")
print(
    pd.to_numeric(df["year"], errors="coerce")
    .value_counts(dropna=False)
    .sort_index()
)

print("\n========== AREA DISTRIBUTION ==========")
print(
    pd.to_numeric(df["area_1000_ha"], errors="coerce")
    .describe()
)

print("\n========== PRODUCTION DISTRIBUTION ==========")
print(
    pd.to_numeric(df["production_1000_t"], errors="coerce")
    .describe()
)

print("\n========== YIELD DISTRIBUTION ==========")
print(
    pd.to_numeric(df["yield_kg_per_ha"], errors="coerce")
    .describe()
)
