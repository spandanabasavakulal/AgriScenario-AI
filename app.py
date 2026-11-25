
import streamlit as st
import pandas as pd
import plotly.express as px

from core.data_loader import (
    load_agriculture_data,
    get_dataset_info
)

from core.data_processor import preprocess_data


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="AgriScenario AI",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================================
# 2. CUSTOM DESIGN
# =====================================================

st.markdown("""
<style>

.stApp {
    background-color: #F5F8F2;
}

h1, h2, h3 {
    color: #174D32;
}

[data-testid="stMetric"] {
    background-color: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #DCE8DC;
}

[data-testid="stSidebar"] {
    background-color: #E8F0E5;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# 3. APPLICATION HEADER
# =====================================================

st.title("🌾 AgriScenario AI")

st.subheader(
    "Agricultural Production Scenario Coordinator"
)

st.write(
    "Explore agricultural possibilities through "
    "historical data analysis and intelligent scenario simulation."
)

st.warning(
    "Scenario results are hypothetical calculations "
    "based on user-defined assumptions. They are not forecasts."
)


# =====================================================
# 4. LOAD AGRICULTURAL DATASET
# =====================================================

try:

    with st.spinner("Loading historical agricultural dataset..."):

        raw_df = load_agriculture_data()

        df, cleaning_report = preprocess_data(raw_df)

    info = get_dataset_info(df)

    if df.empty:
        st.error("No valid agricultural records available.")
        st.stop()

    st.success(
        f"Dataset loaded successfully! "
        f"{len(df):,} valid records available."
    )

except Exception as e:

    st.error(f"Dataset loading failed: {e}")

    st.stop()


# =====================================================
# 5. SIDEBAR FILTERS
# =====================================================

st.sidebar.title("🌾 AgriScenario AI")

st.sidebar.markdown("### Historical Data Filters")

# Crop selection

crop_options = [
    "All Crops"
] + sorted(
    df["crop"].dropna().unique().tolist()
)

selected_crop = st.sidebar.selectbox(
    "Select Crop",
    crop_options
)


# Filter available states according to crop

if selected_crop == "All Crops":

    crop_filtered_df = df.copy()

else:

    crop_filtered_df = df[
        df["crop"] == selected_crop
    ].copy()


# State selection

state_options = [
    "All States"
] + sorted(
    crop_filtered_df["state"].dropna().unique().tolist()
)

selected_state = st.sidebar.selectbox(
    "Select State",
    state_options
)


# Apply crop and state filters

filtered_df = crop_filtered_df.copy()

if selected_state != "All States":

    filtered_df = filtered_df[
        filtered_df["state"] == selected_state
    ].copy()


# Year selection

available_years = sorted(
    filtered_df["year"].dropna().unique().tolist()
)

if available_years:

    selected_years = st.sidebar.multiselect(
        "Select Agricultural Years",
        available_years,
        default=available_years
    )

    filtered_df = filtered_df[
        filtered_df["year"].isin(selected_years)
    ].copy()

else:

    filtered_df = filtered_df.iloc[0:0]


# Display active filters

st.sidebar.divider()

st.sidebar.markdown("### Active Selection")

st.sidebar.write(f"Crop: **{selected_crop}**")

st.sidebar.write(f"State: **{selected_state}**")

st.sidebar.write(
    f"Records: **{len(filtered_df):,}**"
)


# =====================================================
# 6. AGRICULTURAL OVERVIEW
# =====================================================

st.markdown("## Agricultural Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Historical Records",
    f"{info['total_records']:,}"
)

col2.metric(
    "Crop Categories",
    info["total_crops"]
)

col3.metric(
    "States",
    info["total_states"]
)

col4.metric(
    "Districts",
    info["total_districts"]
)

st.caption(
    f"Historical coverage: {info['year_min']} - {info['year_max']}"
)


# =====================================================
# 7. HISTORICAL PRODUCTION ANALYSIS
# =====================================================

st.divider()

st.markdown("## Historical Production Analysis")

if not filtered_df.empty:

    # Aggregate production and area

    total_production = filtered_df[
        "production_1000_t"
    ].sum()

    total_area = filtered_df[
        "area_1000_ha"
    ].sum()

    # Production-weighted yield
    # Production / Area * 1000 = kg per hectare

    weighted_yield = (
        (total_production / total_area) * 1000
        if total_area > 0
        else 0
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Recorded Production",
        f"{total_production:,.2f}",
        "Thousand Tonnes"
    )

    col2.metric(
        "Cumulative Area",
        f"{total_area:,.2f}",
        "Thousand Hectares"
    )

    col3.metric(
        "Weighted Average Yield",
        f"{weighted_yield:,.2f}",
        "kg/hectare"
    )

    # -------------------------------------------------
    # YEAR-WISE PRODUCTION
    # -------------------------------------------------

    st.markdown("### Year-wise Production Trend")

    yearly_data = (
        filtered_df
        .groupby("year", as_index=False)
        ["production_1000_t"]
        .sum()
        .sort_values("year")
    )

    fig = px.line(
        yearly_data,
        x="year",
        y="production_1000_t",
        markers=True,
        title="Historical Agricultural Production Trend",
        labels={
            "year": "Agricultural Year",
            "production_1000_t": "Production (Thousand Tonnes)"
        }
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # -------------------------------------------------
    # DISTRICT-WISE PRODUCTION
    # -------------------------------------------------

    st.markdown("### District-wise Production Comparison")

    district_data = (
        filtered_df
        .groupby("district", as_index=False)
        ["production_1000_t"]
        .sum()
        .sort_values(
            "production_1000_t",
            ascending=False
        )
        .head(10)
    )

    if not district_data.empty:

        fig2 = px.bar(
            district_data,
            x="district",
            y="production_1000_t",
            color="production_1000_t",
            title="Top 10 Districts by Recorded Production",
            labels={
                "district": "District",
                "production_1000_t": "Production (Thousand Tonnes)"
            },
            color_continuous_scale="Greens"
        )

        fig2.update_layout(
            template="plotly_white"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    # -------------------------------------------------
    # CROP-WISE PRODUCTION
    # -------------------------------------------------

    st.markdown("### Crop-wise Production Distribution")

    crop_data = (
        filtered_df
        .groupby("crop", as_index=False)
        ["production_1000_t"]
        .sum()
        .sort_values(
            "production_1000_t",
            ascending=False
        )
        .head(10)
    )

    if not crop_data.empty:

        fig3 = px.bar(
            crop_data,
            x="crop",
            y="production_1000_t",
            color="crop",
            title="Top Crops by Recorded Production",
            labels={
                "crop": "Crop",
                "production_1000_t": "Production (Thousand Tonnes)"
            }
        )

        fig3.update_layout(
            template="plotly_white",
            showlegend=False
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

else:

    st.warning(
        "No historical records available for the selected filters. "
        "Please change the crop, state or year selection."
    )


# =====================================================
# 8. DATASET QUALITY REPORT
# =====================================================

st.divider()

st.markdown("## Dataset Quality Report")

q1, q2, q3, q4, q5 = st.columns(5)

q1.metric(
    "Original Records",
    f"{cleaning_report['original_records']:,}"
)

q2.metric(
    "Duplicates Removed",
    f"{cleaning_report['duplicate_records_removed']:,}"
)

q3.metric(
    "Missing Records Removed",
    f"{cleaning_report.get('missing_records_removed', 0):,}"
)

q4.metric(
    "Invalid Records Removed",
    f"{cleaning_report['invalid_records_removed']:,}"
)

q5.metric(
    "Final Records",
    f"{cleaning_report['final_records']:,}"
)


# Production consistency validation

st.markdown("### Production Consistency Validation")

v1, v2 = st.columns(2)

v1.metric(
    "Consistent Records",
    f"{cleaning_report['production_consistent']:,}"
)

v2.metric(
    "Flagged Records",
    f"{cleaning_report['production_inconsistent']:,}"
)

st.info(
    "Production consistency is checked using the relationship "
    "between cultivated area, yield and production. "
    "Flagged records are retained for investigation; "
    "original dataset values are not overwritten."
)


# =====================================================
# 9. HISTORICAL DATA PREVIEW
# =====================================================

st.divider()

st.markdown("## Historical Dataset Preview")

st.write(
    f"Displaying {min(100, len(filtered_df))} of "
    f"{len(filtered_df):,} filtered records."
)

if not filtered_df.empty:

    st.dataframe(
        filtered_df.head(100),
        use_container_width=True,
        hide_index=True
    )

    # Download filtered dataset

    csv_data = filtered_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Filtered Agricultural Data",
        data=csv_data,
        file_name="agriculture_filtered_data.csv",
        mime="text/csv"
    )

else:

    st.info("No records available for preview.")


# =====================================================
# 10. FOOTER
# =====================================================

st.divider()

st.caption(
    "AgriScenario AI | Historical Data Analysis | "
    "Scenario-Based Agricultural Planning"
)

st.caption(
    "Dataset: India Public Agriculture – Hugging Face"
)
