
import streamlit as st
import pandas as pd

from core.data_loader import load_agriculture_data
from core.data_processor import preprocess_data

st.set_page_config(
    page_title="Agent Workflow",
    page_icon="🤖",
    layout="wide"
)

st.title("Agentic Agricultural Analysis Workflow")
st.caption(
    "A sequence of specialized agents for agricultural data validation, "
    "performance analysis, and decision support."
)

# Load and preprocess data
@st.cache_data(show_spinner=False)
def prepare_data():
    raw_df = load_agriculture_data()
    processed_df, report = preprocess_data(raw_df)
    return processed_df, report

try:
    with st.spinner("Loading agricultural data..."):
        processed_df, report = prepare_data()

except Exception as e:
    st.error(f"Unable to load data: {e}")
    st.stop()

analysis_df = processed_df[
    processed_df["analysis_ready"] == True
].copy()

if analysis_df.empty:
    st.warning("No analysis-ready records are available.")
    st.stop()

st.divider()

# Agent 1: Data Quality Agent
st.subheader("Agent 1: Data Quality Agent")

if st.button("Run Data Quality Agent"):
    st.session_state["quality_agent_result"] = {
        "preserved": report["preserved_records"],
        "ready": report["analysis_ready_records"],
        "missing": report["missing_records_flagged"],
        "inconsistent": report["production_inconsistent"]
    }

if "quality_agent_result" in st.session_state:
    result = st.session_state["quality_agent_result"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Records Preserved", f"{result['preserved']:,}")
    c2.metric("Analysis-Ready Records", f"{result['ready']:,}")
    c3.metric("Missing Records Flagged", f"{result['missing']:,}")

    st.info(
        f"Production-inconsistent records flagged: "
        f"{result['inconsistent']:,}. No original records were deleted."
    )

st.divider()

# Agent 2: Production Analysis Agent
st.subheader("Agent 2: Production Analysis Agent")

if st.button("Run Production Analysis Agent"):
    crop_production = (
        analysis_df.groupby("crop")["production_1000_t"]
        .sum()
        .sort_values(ascending=False)
    )

    st.session_state["production_agent_result"] = {
        "top_crop": crop_production.index[0],
        "top_production": float(crop_production.iloc[0]),
        "crop_count": int(crop_production.shape[0])
    }

if "production_agent_result" in st.session_state:
    result = st.session_state["production_agent_result"]

    st.metric("Top Producing Crop", result["top_crop"])
    st.write(
        f"Aggregated production: {result['top_production']:,.2f} "
        "thousand tonnes"
    )
    st.write(f"Crops analyzed: {result['crop_count']}")

st.divider()

# Agent 3: Regional Analysis Agent
st.subheader("Agent 3: Regional Analysis Agent")

if st.button("Run Regional Analysis Agent"):
    state_production = (
        analysis_df.groupby("state")["production_1000_t"]
        .sum()
        .sort_values(ascending=False)
    )

    st.session_state["regional_agent_result"] = {
        "top_state": state_production.index[0],
        "top_production": float(state_production.iloc[0]),
        "state_count": int(state_production.shape[0])
    }

if "regional_agent_result" in st.session_state:
    result = st.session_state["regional_agent_result"]

    st.metric("Top Producing State", result["top_state"])
    st.write(
        f"Aggregated production: {result['top_production']:,.2f} "
        "thousand tonnes"
    )
    st.write(f"States analyzed: {result['state_count']}")

st.divider()

# Agent 4: Agricultural Risk Agent
st.subheader("Agent 4: Agricultural Risk Agent")

if st.button("Run Agricultural Risk Agent"):
    zero_area = int((analysis_df["area_1000_ha"] <= 0).sum())
    zero_production = int(
        (analysis_df["production_1000_t"] <= 0).sum()
    )

    st.session_state["risk_agent_result"] = {
        "zero_area": zero_area,
        "zero_production": zero_production
    }

if "risk_agent_result" in st.session_state:
    result = st.session_state["risk_agent_result"]

    st.write(f"Zero-area records in analysis subset: {result['zero_area']}")
    st.write(
        f"Zero-production records in analysis subset: "
        f"{result['zero_production']}"
    )

    st.info(
        "These checks describe the analysis-ready subset only. "
        "They are not a prediction of future agricultural risk."
    )

st.divider()

# Agent 5: Recommendation Agent
st.subheader("Agent 5: Recommendation Agent")

if st.button("Generate Recommendations"):
    recommendations = []

    if report["missing_records_flagged"] > 0:
        recommendations.append(
            "Review records with missing values before using them "
            "in detailed analysis."
        )

    if report["production_inconsistent"] > 0:
        recommendations.append(
            "Investigate records where reported production and "
            "area-yield calculations do not match."
        )

    if report["consistency_not_evaluated"] > 0:
        recommendations.append(
            "Review records where production consistency could not "
            "be evaluated."
        )

    recommendations.append(
        "Use analysis-ready records for quantitative comparisons."
    )

    st.session_state["recommendation_agent_result"] = recommendations

if "recommendation_agent_result" in st.session_state:
    for i, recommendation in enumerate(
        st.session_state["recommendation_agent_result"], start=1
    ):
        st.write(f"{i}. {recommendation}")

st.divider()

# Run complete workflow
st.subheader("Complete Agent Workflow")

if st.button("Run All Agents", type="primary"):
    crop_production = (
        analysis_df.groupby("crop")["production_1000_t"]
        .sum()
        .sort_values(ascending=False)
    )

    state_production = (
        analysis_df.groupby("state")["production_1000_t"]
        .sum()
        .sort_values(ascending=False)
    )

    st.session_state["workflow_summary"] = {
        "records": len(analysis_df),
        "top_crop": crop_production.index[0],
        "top_state": state_production.index[0],
        "inconsistent": report["production_inconsistent"]
    }

if "workflow_summary" in st.session_state:
    result = st.session_state["workflow_summary"]

    st.success("All workflow stages completed.")

    st.write(f"Analysis-ready records: {result['records']:,}")
    st.write(f"Top producing crop: {result['top_crop']}")
    st.write(f"Top producing state: {result['top_state']}")
    st.write(
        f"Production-inconsistent records flagged: "
        f"{result['inconsistent']:,}"
    )
