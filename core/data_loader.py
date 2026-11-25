
import streamlit as st
import pandas as pd
from datasets import load_dataset


# Hugging Face dataset configuration
DATASET_ID = "therajasekhar/india-public-agriculture"
DATASET_SPLIT = "train"

# Columns required by the project
REQUIRED_COLUMNS = [
    "crop",
    "state",
    "district",
    "year",
    "area_1000_ha",
    "production_1000_t",
    "yield_kg_per_ha"
]


@st.cache_data(show_spinner=False)
def load_agriculture_data():
    """
    Load agricultural data from Hugging Face
    and validate the dataset structure.
    """

    try:
        dataset = load_dataset(
            DATASET_ID,
            split=DATASET_SPLIT
        )

        df = dataset.to_pandas()

        # Check whether dataset is empty
        if df.empty:
            raise ValueError("The agriculture dataset is empty.")

        # Check required columns
        missing_columns = [
            col for col in REQUIRED_COLUMNS
            if col not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Dataset is missing required columns: {missing_columns}"
            )

        return df

    except Exception as e:
        raise RuntimeError(
            f"Failed to load agriculture dataset: {str(e)}"
        ) from e


def get_dataset_info(df):
    """
    Generate basic statistical information
    about the agricultural dataset.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("Cannot generate statistics from an empty dataset.")

    missing_columns = [
        col for col in ["crop", "state", "district", "year"]
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns required for dataset information: {missing_columns}"
        )

    # Convert year into numeric format for safe calculation
    years = pd.to_numeric(df["year"], errors="coerce").dropna()

    if years.empty:
        raise ValueError("No valid year values found in the dataset.")

    return {
        "total_records": int(len(df)),
        "total_crops": int(df["crop"].nunique()),
        "total_states": int(df["state"].nunique()),
        "total_districts": int(df["district"].nunique()),
        "year_min": int(years.min()),
        "year_max": int(years.max()),
        "missing_values": int(df.isnull().sum().sum()),
        "total_columns": int(len(df.columns))
    }
