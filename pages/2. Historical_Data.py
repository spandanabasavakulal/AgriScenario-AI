import streamlit as st
import pandas as pd

from core.data_loader import load_agriculture_data
from core.data_processor import preprocess_data


st.set_page_config(
    page_title="Historical Data | AgriScenario AI",
    page_icon="🌾",
    layout="wide"
)

st.title("Historical Agricultural Data")
st.write(
    "Explore, filter, and download historical agricultural records."
)


@st.cache_data(show_spinner="Loading agricultural data...")
def get_data():
    raw_df = load_agriculture_data()
    processed_df, report = preprocess_data(raw_df)
    return processed_df, report


try:
    df, report = get_data()

except Exception as e:
    st.error(f"Unable to load agricultural data: {e}")
    st.stop()


# Use only analysis-ready records for analytical filtering
analysis_df = df[df["analysis_ready"]].copy()

st.success(
    f"Loaded {len(df):,} records. "
    f"{len(analysis_df):,} records are analysis-ready."
)

st.divider()

# Filters
st.subheader("Filter Historical Records")

col1, col2, col3 = st.columns(3)

with col1:
    crops = sorted(analysis_df["crop"].dropna().unique().tolist())
    selected_crops = st.multiselect(
        "Select Crops",
        crops,
        default=[]
    )

with col2:
    states = sorted(analysis_df["state"].dropna().unique().tolist())
    selected_states = st.multiselect(
        "Select States",
        states,
        default=[]
    )

with col3:
    years = sorted(
        analysis_df["year"].dropna().astype(int).unique().tolist()
    )
    selected_years = st.multiselect(
        "Select Years",
        years,
        default=years
    )

filtered_df = analysis_df.copy()

if selected_crops:
    filtered_df = filtered_df[
        filtered_df["crop"].isin(selected_crops)
    ]

if selected_states:
    filtered_df = filtered_df[
        filtered_df["state"].isin(selected_states)
    ]

if selected_years:
    filtered_df = filtered_df[
        filtered_df["year"].isin(selected_years)
    ]
else:
    filtered_df = filtered_df.iloc[0:0]


st.divider()

# Summary metrics
st.subheader("Filtered Dataset Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Records", f"{len(filtered_df):,}")
c2.metric("Crops", f"{filtered_df['crop'].nunique():,}")
c3.metric("States", f"{filtered_df['state'].nunique():,}")

total_production = filtered_df["production_1000_t"].sum()
c4.metric("Production (1000 tonnes)", f"{total_production:,.2f}")


st.divider()

# Dataset table
st.subheader("Historical Records")

if filtered_df.empty:
    st.warning("No records match the selected filters.")
else:
    display_columns = [
        "state",
        "district",
        "year",
        "crop",
        "area_1000_ha",
        "production_1000_t",
        "yield_kg_per_ha"
    ]

    st.dataframe(
        filtered_df[display_columns],
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        f"Displaying {len(filtered_df):,} matching analysis-ready records."
    )


st.divider()

# Download
st.subheader("Export Historical Data")

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Data as CSV",
    data=csv_data,
    file_name="agri_historical_data.csv",
    mime="text/csv",
    disabled=filtered_df.empty
)