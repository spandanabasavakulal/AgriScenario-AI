
import pandas as pd
import numpy as np

ESSENTIAL_COLUMNS = [
    "state", "district", "year", "crop",
    "area_1000_ha", "production_1000_t",
    "yield_kg_per_ha"
]

NUMERICAL_COLUMNS = [
    "year", "area_1000_ha",
    "production_1000_t", "yield_kg_per_ha"
]


def preprocess_data(df):

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("Dataset is empty.")

    df = df.copy()
    original_count = len(df)

    missing_columns = [
        c for c in ESSENTIAL_COLUMNS if c not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    for col in ["record_uid", "source"]:
        if col not in df.columns:
            df[col] = pd.NA

    for col in ["state", "district", "crop", "record_uid", "source"]:
        df[col] = df[col].astype("string").str.strip()
        df[col] = df[col].replace("", pd.NA)

    for col in NUMERICAL_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df[NUMERICAL_COLUMNS] = df[NUMERICAL_COLUMNS].replace(
        [np.inf, -np.inf], np.nan
    )

    # Missing values
    missing_mask = df[ESSENTIAL_COLUMNS].isna().any(axis=1)
    df["has_missing_values"] = missing_mask

    # Invalid numerical values
    year_valid = (
        df["year"].notna()
        & df["year"].between(1900, 2100)
        & (df["year"] % 1 == 0)
    )

    invalid_mask = (
        (df["area_1000_ha"] < 0)
        | (df["production_1000_t"] < 0)
        | (df["yield_kg_per_ha"] < 0)
        | ~year_valid
    ).fillna(True)

    df["has_invalid_values"] = invalid_mask

    # Zero-value patterns
    df["zero_area_with_production"] = (
        (df["area_1000_ha"] == 0)
        & (df["production_1000_t"] > 0)
    ).fillna(False)

    df["zero_activity"] = (
        (df["area_1000_ha"] == 0)
        & (df["production_1000_t"] == 0)
        & (df["yield_kg_per_ha"] == 0)
    ).fillna(False)

    df["zero_production_with_positive_area"] = (
        (df["area_1000_ha"] > 0)
        & (df["production_1000_t"] == 0)
    ).fillna(False)

    df["zero_yield_with_positive_area"] = (
        (df["area_1000_ha"] > 0)
        & (df["yield_kg_per_ha"] == 0)
    ).fillna(False)

    # Duplicate IDs
    duplicate_mask = (
        df["record_uid"].notna()
        & df["record_uid"].duplicated(keep="first")
    )

    df["is_duplicate_uid"] = duplicate_mask

    # Production consistency
    eligible = (
        df["area_1000_ha"].gt(0)
        & df["production_1000_t"].notna()
        & df["yield_kg_per_ha"].notna()
        & ~invalid_mask
    )

    df["calculated_production_1000_t"] = np.nan

    df.loc[eligible, "calculated_production_1000_t"] = (
        df.loc[eligible, "area_1000_ha"]
        * df.loc[eligible, "yield_kg_per_ha"] / 1000
    )

    df["production_difference"] = (
        df["production_1000_t"]
        - df["calculated_production_1000_t"]
    )

    df["production_consistent"] = pd.Series(
        pd.NA, index=df.index, dtype="boolean"
    )

    consistent = np.isclose(
        df.loc[eligible, "production_1000_t"],
        df.loc[eligible, "calculated_production_1000_t"],
        rtol=0.02,
        atol=0.01
    )

    df.loc[eligible, "production_consistent"] = consistent

    inconsistent_mask = (
        eligible & df["production_consistent"].eq(False).fillna(False)
    )

    # Analysis-ready records
    df["analysis_ready"] = (
        ~missing_mask
        & ~invalid_mask
        & ~duplicate_mask
        & df["area_1000_ha"].gt(0)
        & ~inconsistent_mask
    ).fillna(False)

    valid_year = year_valid.fillna(False)
    df.loc[valid_year, "year"] = df.loc[valid_year, "year"].astype(int)

    ready_count = int(df["analysis_ready"].sum())
    consistent_count = int(df["production_consistent"].eq(True).sum())
    inconsistent_count = int(inconsistent_mask.sum())

    report = {
        "original_records": original_count,
        "preserved_records": len(df),
        "final_records": ready_count,
        "analysis_ready_records": ready_count,
        "missing_records_flagged": int(missing_mask.sum()),
        "invalid_records_flagged": int(invalid_mask.sum()),
        "duplicate_records_flagged": int(duplicate_mask.sum()),
        "zero_area_records": int((df["area_1000_ha"] == 0).sum()),
        "zero_area_with_production": int(
            df["zero_area_with_production"].sum()
        ),
        "zero_activity_records": int(df["zero_activity"].sum()),
        "zero_production_records": int(
            df["zero_production_with_positive_area"].sum()
        ),
        "zero_yield_records": int(
            df["zero_yield_with_positive_area"].sum()
        ),
        "production_consistent": consistent_count,
        "production_inconsistent": inconsistent_count,
        "consistency_not_evaluated": int(
            df["production_consistent"].isna().sum()
        ),
        "missing_uid_records": int(df["record_uid"].isna().sum()),
        "year_min": int(df.loc[valid_year, "year"].min()),
        "year_max": int(df.loc[valid_year, "year"].max()),
        "missing_records_removed": 0,
        "invalid_records_removed": 0,
        "duplicate_records_removed": 0
    }

    return df.reset_index(drop=True), report
