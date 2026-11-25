
import streamlit as st
import pandas as pd

from core.data_loader import (
    load_agriculture_data,
    get_dataset_info
)

from core.data_processor import preprocess_data


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AgriScenario AI - Dashboard",
    page_icon="🌾",
    layout="wide"
)

st.title("AgriScenario AI")
st.subheader("Agricultural Data Intelligence Dashboard")

st.markdown(
    """
    Explore historical agricultural data, monitor data quality,
    analyze crop production patterns, and simulate agricultural
    scenarios using historical records.
    """
)

st.divider()


# ============================================================
# 2. LOAD AND PROCESS DATA
# ============================================================

@st.cache_data(show_spinner=False)
def get_processed_dataset():

    raw_df = load_agriculture_data()

    processed_df, quality_report = preprocess_data(raw_df)

    return raw_df, processed_df, quality_report


try:

    with st.spinner("Loading agricultural dataset..."):

        raw_df, processed_df, report = get_processed_dataset()

        dataset_info = get_dataset_info(raw_df)

except Exception as e:

    st.error(f"Unable to load agricultural data: {e}")
    st.stop()


# Analysis-ready dataset
analysis_df = processed_df[
    processed_df["analysis_ready"]
].copy()


if processed_df.empty:

    st.error("Agricultural dataset is empty.")

    st.stop()


if analysis_df.empty:

    st.error("No analysis-ready records are available.")

    st.stop()


# ============================================================
# 3. DATASET OVERVIEW
# ============================================================

st.header("Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Original Records",
        f"{dataset_info['total_records']:,}"
    )

with col2:

    st.metric(
        "Preserved Records",
        f"{report['preserved_records']:,}"
    )

with col3:

    st.metric(
        "Analysis-Ready Records",
        f"{report['analysis_ready_records']:,}"
    )

with col4:

    st.metric(
        "Total Crops",
        f"{dataset_info['total_crops']:,}"
    )


col5, col6, col7, col8 = st.columns(4)

with col5:

    st.metric(
        "States",
        f"{dataset_info['total_states']:,}"
    )

with col6:

    st.metric(
        "Districts",
        f"{dataset_info['total_districts']:,}"
    )

with col7:

    st.metric(
        "Year Range",
        f"{dataset_info['year_min']}–{dataset_info['year_max']}"
    )

with col8:

    st.metric(
        "Production Consistent",
        f"{report['production_consistent']:,}"
    )


st.divider()


# ============================================================
# 4. DATA QUALITY ANALYSIS
# ============================================================

st.header("Data Quality Analysis")

st.caption(
    "All original records are preserved. Quality issues are "
    "identified using flags instead of deleting records."
)


col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Records Preserved",
        f"{report['preserved_records']:,}"
    )

with col2:

    st.metric(
        "Analysis Ready",
        f"{report['analysis_ready_records']:,}"
    )

with col3:

    st.metric(
        "Missing Records",
        f"{report['missing_records_flagged']:,}"
    )

with col4:

    st.metric(
        "Invalid Records",
        f"{report['invalid_records_flagged']:,}"
    )


# ------------------------------------------------------------
# DATA QUALITY SUMMARY
# ------------------------------------------------------------

st.subheader("Data Quality Summary")

quality_data = pd.DataFrame({

    "Category": [
        "Analysis Ready",
        "Missing Values",
        "Invalid Values",
        "Duplicate IDs",
        "Production Inconsistent"
    ],

    "Count": [
        report["analysis_ready_records"],
        report["missing_records_flagged"],
        report["invalid_records_flagged"],
        report["duplicate_records_flagged"],
        report["production_inconsistent"]
    ]

})

st.bar_chart(
    quality_data,
    x="Category",
    y="Count",
    color="#2980B9"
)


# ------------------------------------------------------------
# ZERO-VALUE ANALYSIS
# ------------------------------------------------------------

st.subheader("Zero-Value Pattern Analysis")

zero_data = pd.DataFrame({

    "Category": [
        "Zero Area",
        "Zero Activity",
        "Zero Area with Production",
        "Zero Production",
        "Zero Yield"
    ],

    "Count": [
        report["zero_area_records"],
        report["zero_activity_records"],
        report["zero_area_with_production"],
        report["zero_production_records"],
        report["zero_yield_records"]
    ]

})

st.bar_chart(
    zero_data,
    x="Category",
    y="Count",
    color="#E67E22"
)


# ------------------------------------------------------------
# PRODUCTION CONSISTENCY
# ------------------------------------------------------------

st.subheader("Production Consistency Validation")

consistent = report["production_consistent"]

inconsistent = report["production_inconsistent"]

not_evaluated = report["consistency_not_evaluated"]

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Consistent Records",
        f"{consistent:,}"
    )

with col2:

    st.metric(
        "Inconsistent Records",
        f"{inconsistent:,}"
    )

with col3:

    st.metric(
        "Not Evaluated",
        f"{not_evaluated:,}"
    )


consistency_data = pd.DataFrame({

    "Status": [
        "Consistent",
        "Inconsistent",
        "Not Evaluated"
    ],

    "Records": [
        consistent,
        inconsistent,
        not_evaluated
    ]

})

st.bar_chart(
    consistency_data,
    x="Status",
    y="Records"
)


st.divider()


# ============================================================
# 5. CROP DISTRIBUTION
# ============================================================

st.header("Crop Distribution")

crop_counts = (

    analysis_df["crop"]
    .value_counts()
    .head(10)
    .rename_axis("Crop")
    .reset_index(name="Records")

)

st.caption(
    "Top 10 crops based on analysis-ready historical records."
)

st.bar_chart(
    crop_counts,
    x="Crop",
    y="Records",
    color="#E67E22"
)


st.divider()


# ============================================================
# 6. STATE-WISE AGRICULTURAL DISTRIBUTION
# ============================================================

st.header("State-wise Agricultural Distribution")

state_counts = (

    analysis_df["state"]
    .value_counts()
    .head(10)
    .rename_axis("State")
    .reset_index(name="Records")

)

st.caption(
    "Top 10 states based on analysis-ready agricultural records."
)

st.bar_chart(
    state_counts,
    x="State",
    y="Records",
    color="#8E44AD"
)


st.divider()


# ============================================================
# 7. HISTORICAL AGRICULTURAL TRENDS
# ============================================================

st.header("Historical Agricultural Trends")

yearly_data = (

    analysis_df.groupby("year")
    .agg(

        Total_Area=(
            "area_1000_ha",
            "sum"
        ),

        Total_Production=(
            "production_1000_t",
            "sum"
        )

    )
    .reset_index()
    .sort_values("year")

)


col1, col2 = st.columns(2)

with col1:

    st.subheader("Year-wise Cultivated Area")

    st.line_chart(
        yearly_data,
        x="year",
        y="Total_Area",
        color="#3498DB"
    )


with col2:

    st.subheader("Year-wise Agricultural Production")

    st.line_chart(
        yearly_data,
        x="year",
        y="Total_Production",
        color="#27AE60"
    )


st.caption(
    "Area: thousand hectares | "
    "Production: thousand tonnes | "
    "Charts use analysis-ready records only."
)


st.divider()


# ============================================================
# 8. TOP PRODUCING CROPS
# ============================================================

st.header("Top Producing Crops")

crop_production = (

    analysis_df.groupby("crop")
    .agg(
        Total_Production=(
            "production_1000_t",
            "sum"
        )
    )
    .reset_index()
    .sort_values(
        "Total_Production",
        ascending=False
    )
    .head(10)

)

st.bar_chart(
    crop_production,
    x="crop",
    y="Total_Production",
    color="#16A085"
)

st.caption(
    "Top 10 crops ranked by cumulative production "
    "across the available historical period."
)


st.divider()


# ============================================================
# 9. PROCESSED DATASET PREVIEW
# ============================================================

st.header("Processed Dataset Preview")

st.caption(
    "Preview includes all preserved records and their quality flags."
)

st.dataframe(
    processed_df.head(20),
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 10. DATA QUALITY REPORT
# ============================================================

with st.expander("View Complete Data Quality Report"):

    report_df = pd.DataFrame(

        list(report.items()),

        columns=[
            "Metric",
            "Value"
        ]

    )

    st.dataframe(
        report_df,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# 11. DOWNLOAD DATASETS
# ============================================================

st.header("Export Agricultural Data")

col1, col2 = st.columns(2)


with col1:

    st.subheader("Complete Processed Dataset")

    processed_csv = processed_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(

        label="Download Complete Dataset",

        data=processed_csv,

        file_name="agriculture_processed_data.csv",

        mime="text/csv",

        use_container_width=True

    )


with col2:

    st.subheader("Analysis-Ready Dataset")

    analysis_csv = analysis_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(

        label="Download Analysis-Ready Dataset",

        data=analysis_csv,

        file_name="agriculture_analysis_ready.csv",

        mime="text/csv",

        use_container_width=True

    )


# ============================================================
# 12. FOOTER
# ============================================================

st.divider()

st.caption(
    "AgriScenario AI | Agricultural Data Intelligence "
    "| Dataset: therajasekhar/india-public-agriculture"
)
