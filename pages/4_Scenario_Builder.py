
import streamlit as st
import pandas as pd

from core.data_loader import load_agriculture_data
from core.data_processor import preprocess_data
from core.calculations import (
    get_baseline_metrics,
    simulate_scenario,
    verify_scenario
)

st.set_page_config(
    page_title="Scenario Builder",
    page_icon="🌾",
    layout="wide"
)

st.title("Agricultural Scenario Builder")
st.caption(
    "Simulate how changes in cultivated area and crop yield "
    "can affect agricultural production."
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "scenario_result" not in st.session_state:
    st.session_state["scenario_result"] = None

if "scenario_details" not in st.session_state:
    st.session_state["scenario_details"] = None

if "scenario_results" not in st.session_state:
    st.session_state["scenario_results"] = []

if "saved_scenario_key" not in st.session_state:
    st.session_state["saved_scenario_key"] = None


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data(show_spinner=False)
def prepare_data():
    raw_df = load_agriculture_data()
    processed_df, report = preprocess_data(raw_df)
    return processed_df, report


try:
    with st.spinner("Loading agricultural dataset..."):
        processed_df, report = prepare_data()

except Exception as e:
    st.error(f"Data loading failed: {e}")
    st.stop()


# Use only analysis-ready records
analysis_df = processed_df[
    processed_df["analysis_ready"] == True
].copy()

if analysis_df.empty:
    st.warning("No analysis-ready agricultural records available.")
    st.stop()


# Ensure year is numeric
analysis_df["year"] = pd.to_numeric(
    analysis_df["year"],
    errors="coerce"
)

analysis_df = analysis_df.dropna(subset=["year"])
analysis_df["year"] = analysis_df["year"].astype(int)


# --------------------------------------------------
# STEP 1: SELECT CROP
# --------------------------------------------------

st.header("Step 1: Select Agricultural Crop")

crop_options = sorted(
    analysis_df["crop"].dropna().unique().tolist()
)

selected_crop = st.selectbox(
    "Select Crop",
    crop_options
)


# --------------------------------------------------
# STEP 2: SELECT STATE AND YEAR
# --------------------------------------------------

st.header("Step 2: Select Region and Year")

crop_df = analysis_df[
    analysis_df["crop"] == selected_crop
].copy()

state_options = sorted(
    crop_df["state"].dropna().unique().tolist()
)

if not state_options:
    st.warning("No states available for the selected crop.")
    st.stop()

selected_state = st.selectbox(
    "Select State",
    state_options
)

state_df = crop_df[
    crop_df["state"] == selected_state
].copy()

year_options = sorted(
    state_df["year"].unique().tolist()
)

if not year_options:
    st.warning("No years available for this crop and state.")
    st.stop()

selected_year = st.selectbox(
    "Select Year",
    year_options
)


# --------------------------------------------------
# BASELINE DATA
# --------------------------------------------------

baseline_df = state_df[
    state_df["year"] == selected_year
].copy()

if baseline_df.empty:
    st.error("No baseline records found for this selection.")
    st.stop()


baseline = get_baseline_metrics(baseline_df)

baseline_area = float(baseline["baseline_area"])
baseline_production = float(baseline["baseline_production"])
baseline_yield = float(baseline["baseline_yield"])


# --------------------------------------------------
# DISPLAY BASELINE
# --------------------------------------------------

st.divider()
st.header("Baseline Agricultural Performance")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Cultivated Area",
    f"{baseline_area:,.2f} thousand ha"
)

col2.metric(
    "Production",
    f"{baseline_production:,.2f} thousand tonnes"
)

col3.metric(
    "Yield",
    f"{baseline_yield:,.2f} kg/ha"
)

col4.metric(
    "Records",
    f"{baseline.get('record_count', len(baseline_df)):,}"
)


# --------------------------------------------------
# STEP 3: CONFIGURE SCENARIO
# --------------------------------------------------

st.divider()
st.header("Step 3: Configure Your Scenario")

col1, col2 = st.columns(2)

with col1:
    area_change = st.slider(
        "Cultivated Area Change (%)",
        min_value=-50.0,
        max_value=100.0,
        value=0.0,
        step=1.0
    )

with col2:
    yield_change = st.slider(
        "Crop Yield Change (%)",
        min_value=-50.0,
        max_value=100.0,
        value=0.0,
        step=1.0
    )


area_factor = 1 + area_change / 100
yield_factor = 1 + yield_change / 100

st.info(
    f"Area multiplier: {area_factor:.2f} | "
    f"Yield multiplier: {yield_factor:.2f}"
)


# --------------------------------------------------
# STEP 4: RUN SIMULATION
# --------------------------------------------------

st.divider()
st.header("Step 4: Run Scenario Simulation")

if st.button(
    "Run Scenario Simulation",
    type="primary",
    width="stretch"
):

    try:
        # IMPORTANT: Use the actual function signature
        result = simulate_scenario(
            baseline_area,
            baseline_production,
            baseline_yield,
            area_change,
            yield_change
        )

        # Verify using the actual function signature
        verification = verify_scenario(result)

        st.session_state["scenario_result"] = result

        st.session_state["scenario_details"] = {
            "crop": selected_crop,
            "state": selected_state,
            "year": selected_year,
            "area_change": area_change,
            "yield_change": yield_change
        }

        st.session_state["verification_result"] = verification

        # Allow saving this newly generated scenario
        st.session_state["saved_scenario_key"] = None

        st.success("Scenario simulation completed successfully.")

    except Exception as e:
        st.error(f"Scenario simulation failed: {e}")


# --------------------------------------------------
# STEP 5: DISPLAY RESULTS
# --------------------------------------------------

result = st.session_state.get("scenario_result")
details = st.session_state.get("scenario_details")

if result is not None and details is not None:

    # Display results only for the selection that generated them
    current_selection = (
        selected_crop,
        selected_state,
        selected_year,
        area_change,
        yield_change
    )

    result_selection = (
        details["crop"],
        details["state"],
        details["year"],
        details["area_change"],
        details["yield_change"]
    )

    if current_selection == result_selection:

        st.divider()
        st.header("Step 5: Scenario Results")

        production_difference = result["production_difference"]
        production_change = result["production_change_pct"]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Baseline Production",
            f"{result['baseline_production']:,.2f}"
        )

        col2.metric(
            "Simulated Production",
            f"{result['simulated_production']:,.2f}",
            delta=f"{production_difference:+,.2f}"
        )

        col3.metric(
            "Production Change",
            f"{production_change:+.2f}%"
        )

        st.subheader("Detailed Scenario Results")

        result_table = pd.DataFrame({
            "Metric": [
                "Baseline Area",
                "Simulated Area",
                "Baseline Production",
                "Simulated Production",
                "Baseline Yield",
                "Simulated Yield",
                "Area Change",
                "Yield Change",
                "Production Difference",
                "Production Change"
            ],
            "Value": [
                result["baseline_area"],
                result["simulated_area"],
                result["baseline_production"],
                result["simulated_production"],
                result["baseline_yield"],
                result["simulated_yield"],
                f"{result['area_change_pct']:.2f}%",
                f"{result['yield_change_pct']:.2f}%",
                result["production_difference"],
                f"{result['production_change_pct']:.2f}%"
            ]
        })

        st.dataframe(
            result_table,
            hide_index=True,
            width="stretch"
        )

        # Verification information
        st.subheader("Scenario Verification")

        verification = st.session_state.get(
            "verification_result"
        )

        st.write(verification)

        # --------------------------------------------------
        # STEP 6: SAVE SCENARIO
        # --------------------------------------------------

        st.divider()
        st.header("Step 6: Save Scenario for Comparison")

        scenario_name = st.text_input(
            "Enter Scenario Name",
            value=(
                f"{selected_crop}_{selected_state}_"
                f"{selected_year}_Scenario"
            )
        )

        if st.button(
            "Save Scenario for Comparison",
            width="stretch"
        ):

            if not scenario_name.strip():
                st.warning("Please enter a scenario name.")

            else:
                scenario_key = (
                    selected_crop,
                    selected_state,
                    selected_year,
                    area_change,
                    yield_change,
                    scenario_name.strip()
                )

                if (
                    st.session_state["saved_scenario_key"]
                    == scenario_key
                ):
                    st.warning("This scenario has already been saved.")

                else:
                    scenario_data = {
                        "scenario_name": scenario_name.strip(),
                        "crop": selected_crop,
                        "state": selected_state,
                        "year": selected_year,
                        "area_change": result["area_change_pct"],
                        "yield_change": result["yield_change_pct"],
                        "baseline_production": result["baseline_production"],
                        "simulated_production": result["simulated_production"],
                        "production_difference": result["production_difference"],
                        "production_change_percentage": result["production_change_pct"]
                    }

                    st.session_state["scenario_results"].append(
                        scenario_data
                    )

                    st.session_state["saved_scenario_key"] = scenario_key

                    st.success(
                        "Scenario saved successfully! "
                        "Open Scenario Comparison to compare it."
                    )

    else:
        st.info(
            "Your selection has changed. Run the simulation again "
            "to generate results for the current selection."
        )


# --------------------------------------------------
# SAVED SCENARIO COUNT
# --------------------------------------------------

st.divider()

saved_scenarios = st.session_state.get(
    "scenario_results",
    []
)

st.subheader("Saved Scenarios")

st.metric(
    "Total Scenarios Saved",
    len(saved_scenarios)
)

if saved_scenarios:
    st.dataframe(
        pd.DataFrame(saved_scenarios),
        hide_index=True,
        width="stretch"
    )
