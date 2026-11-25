
import streamlit as st
import pandas as pd
import numpy as np

from core.data_loader import load_agriculture_data
from core.data_processor import preprocess_data


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.title("Historical Agricultural Analysis")

st.subheader(
    "Crop Production, Yield and Growth Analysis"
)

st.write(
    "Analyze historical agricultural performance across "
    "crops, states and years using analysis-ready records."
)

st.divider()


# ============================================================
# 2. LOAD DATA
# ============================================================

@st.cache_data(show_spinner=False)
def get_analysis_data():

    raw_df = load_agriculture_data()

    processed_df, report = preprocess_data(raw_df)

    analysis_df = processed_df[
        processed_df["analysis_ready"]
    ].copy()

    return analysis_df, report


try:

    with st.spinner("Preparing historical analysis..."):

        df, report = get_analysis_data()

except Exception as e:

    st.error(f"Unable to load agricultural data: {e}")
    st.stop()


if df.empty:

    st.error("No analysis-ready records are available.")
    st.stop()


# ============================================================
# 3. INTERACTIVE FILTERS
# ============================================================

st.sidebar.header("Analysis Filters")

crop_options = sorted(df["crop"].dropna().unique())

state_options = sorted(df["state"].dropna().unique())

year_options = sorted(df["year"].dropna().astype(int).unique())


selected_crops = st.sidebar.multiselect(
    "Select Crops",
    crop_options,
    default=crop_options
)

selected_states = st.sidebar.multiselect(
    "Select States",
    state_options,
    default=state_options
)

selected_years = st.sidebar.multiselect(
    "Select Years",
    year_options,
    default=year_options
)


filtered_df = df[
    df["crop"].isin(selected_crops)
    & df["state"].isin(selected_states)
    & df["year"].isin(selected_years)
].copy()


if filtered_df.empty:

    st.warning(
        "No records match the selected filters. "
        "Please select at least one crop, state and year."
    )

    st.stop()


st.sidebar.divider()

st.sidebar.caption(
    "Analysis uses records classified as analysis-ready "
    "by the preprocessing module."
)


# ============================================================
# 4. OVERALL AGRICULTURAL PERFORMANCE
# ============================================================

st.header("Overall Agricultural Performance")

total_records = len(filtered_df)

total_production = filtered_df[
    "production_1000_t"
].sum()

total_area = filtered_df[
    "area_1000_ha"
].sum()

weighted_yield = (
    (
        filtered_df["area_1000_ha"]
        * filtered_df["yield_kg_per_ha"]
    ).sum() / total_area
    if total_area > 0 else 0
)


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Records",
    f"{total_records:,}"
)

col2.metric(
    "Total Production",
    f"{total_production:,.2f}"
)

col3.metric(
    "Total Cultivated Area",
    f"{total_area:,.2f}"
)

col4.metric(
    "Weighted Average Yield",
    f"{weighted_yield:,.2f}"
)

st.caption(
    "Production: thousand tonnes | "
    "Area: thousand hectares | "
    "Yield: kg per hectare"
)

st.divider()


# ============================================================
# 5. CROP-WISE PRODUCTION ANALYSIS
# ============================================================

st.header("Crop-wise Production Analysis")

crop_analysis = (

    filtered_df.groupby("crop")
    .agg(
        Total_Production=(
            "production_1000_t",
            "sum"
        ),
        Total_Area=(
            "area_1000_ha",
            "sum"
        ),
        Average_Yield=(
            "yield_kg_per_ha",
            "mean"
        )
    )
    .reset_index()
    .sort_values(
        "Total_Production",
        ascending=False
    )

)

st.subheader("Production by Crop")

st.bar_chart(
    crop_analysis,
    x="crop",
    y="Total_Production",
    color="#16A085"
)

st.dataframe(
    crop_analysis,
    use_container_width=True,
    hide_index=True
)

st.divider()


# ============================================================
# 6. STATE-WISE PRODUCTION COMPARISON
# ============================================================

st.header("State-wise Production Comparison")

state_analysis = (

    filtered_df.groupby("state")
    .agg(
        Total_Production=(
            "production_1000_t",
            "sum"
        ),
        Total_Area=(
            "area_1000_ha",
            "sum"
        ),
        Average_Yield=(
            "yield_kg_per_ha",
            "mean"
        )
    )
    .reset_index()
    .sort_values(
        "Total_Production",
        ascending=False
    )

)

col1, col2 = st.columns(2)

with col1:

    st.subheader("Top 10 Producing States")

    st.bar_chart(
        state_analysis.head(10),
        x="state",
        y="Total_Production",
        color="#2980B9"
    )

with col2:

    st.subheader("Lowest 10 Producing States")

    st.bar_chart(
        state_analysis.tail(10).sort_values(
            "Total_Production",
            ascending=True
        ),
        x="state",
        y="Total_Production",
        color="#E67E22"
    )


st.dataframe(
    state_analysis,
    use_container_width=True,
    hide_index=True
)

st.divider()


# ============================================================
# 7. YEAR-WISE PRODUCTION TRENDS
# ============================================================

st.header("Year-wise Production Trends")

yearly_analysis = (

    filtered_df.groupby("year")
    .agg(
        Total_Production=(
            "production_1000_t",
            "sum"
        ),
        Total_Area=(
            "area_1000_ha",
            "sum"
        ),
        Average_Yield=(
            "yield_kg_per_ha",
            "mean"
        )
    )
    .reset_index()
    .sort_values("year")

)

col1, col2 = st.columns(2)

with col1:

    st.subheader("Annual Production")

    st.line_chart(
        yearly_analysis,
        x="year",
        y="Total_Production",
        color="#27AE60"
    )

with col2:

    st.subheader("Annual Cultivated Area")

    st.line_chart(
        yearly_analysis,
        x="year",
        y="Total_Area",
        color="#3498DB"
    )


st.divider()


# ============================================================
# 8. YEAR-OVER-YEAR PRODUCTION GROWTH
# ============================================================

st.header("Year-over-Year Production Growth")

yearly_analysis["Production_Growth_Percentage"] = (
    yearly_analysis["Total_Production"]
    .pct_change(fill_method=None)
    * 100
)

growth_df = yearly_analysis.dropna(
    subset=["Production_Growth_Percentage"]
).copy()


if not growth_df.empty:

    st.bar_chart(
        growth_df,
        x="year",
        y="Production_Growth_Percentage",
        color="#8E44AD"
    )

    latest_growth = growth_df.iloc[-1]

    col1, col2 = st.columns(2)

    col1.metric(
        "Latest Year",
        int(latest_growth["year"])
    )

    col2.metric(
        "Production Growth",
        f"{latest_growth['Production_Growth_Percentage']:.2f}%"
    )

    st.dataframe(
        growth_df[
            [
                "year",
                "Total_Production",
                "Production_Growth_Percentage"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "At least two years of data are required "
        "to calculate year-over-year growth."
    )


st.divider()


# ============================================================
# 9. CROP YIELD ANALYSIS
# ============================================================

st.header("Crop Yield Analysis")

yield_analysis = (

    filtered_df.groupby("crop")
    .agg(
        Average_Yield=(
            "yield_kg_per_ha",
            "mean"
        ),
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
    .sort_values(
        "Average_Yield",
        ascending=False
    )

)

st.subheader("Average Yield by Crop")

st.bar_chart(
    yield_analysis.head(10),
    x="crop",
    y="Average_Yield",
    color="#D35400"
)

st.dataframe(
    yield_analysis,
    use_container_width=True,
    hide_index=True
)


st.divider()


# ============================================================
# 10. BEST AND LOWEST PERFORMING CROPS
# ============================================================

st.header("Crop Performance Ranking")

if not crop_analysis.empty:

    best_crop = crop_analysis.iloc[0]

    lowest_crop = crop_analysis.iloc[-1]

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Highest Production Crop")

        st.metric(
            "Crop",
            best_crop["crop"]
        )

        st.metric(
            "Total Production",
            f"{best_crop['Total_Production']:,.2f}"
        )

    with col2:

        st.subheader("Lowest Production Crop")

        st.metric(
            "Crop",
            lowest_crop["crop"]
        )

        st.metric(
            "Total Production",
            f"{lowest_crop['Total_Production']:,.2f}"
        )


st.divider()


# ============================================================
# 11. DOWNLOAD ANALYSIS RESULTS
# ============================================================

st.header("Export Analysis Results")

col1, col2, col3 = st.columns(3)


with col1:

    crop_csv = crop_analysis.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "Download Crop Analysis",
        crop_csv,
        "crop_analysis.csv",
        "text/csv",
        use_container_width=True
    )


with col2:

    state_csv = state_analysis.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "Download State Analysis",
        state_csv,
        "state_analysis.csv",
        "text/csv",
        use_container_width=True
    )


with col3:

    yearly_csv = yearly_analysis.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "Download Yearly Analysis",
        yearly_csv,
        "yearly_analysis.csv",
        "text/csv",
        use_container_width=True
    )


# ============================================================
# 12. FOOTER
# ============================================================

st.divider()

st.caption(
    "AgriScenario AI | Historical Agricultural Analysis "
    "| Source: therajasekhar/india-public-agriculture"
)
