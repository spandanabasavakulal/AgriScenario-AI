
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Scenario Comparison",
    page_icon="📊",
    layout="wide"
)

st.title("Scenario Comparison")
st.caption("Compare historical agricultural performance with simulated scenarios.")

# Retrieve saved scenarios
scenarios = st.session_state.get("scenario_results", [])

if not scenarios:
    st.warning(
        "No saved scenarios found. Go to Scenario Builder, "
        "create a scenario, and save it before comparing."
    )
    st.stop()

# Normalize scenario data
comparison_data = []

for index, scenario in enumerate(scenarios):
    comparison_data.append({
        "Scenario": scenario.get("scenario_name", f"Scenario {index + 1}"),
        "Baseline Production": scenario.get("baseline_production", 0),
        "Simulated Production": scenario.get("simulated_production", 0),
        "Production Change": scenario.get("production_difference", 0),
        "Change (%)": scenario.get("production_change_percentage", 0)
    })

comparison_df = pd.DataFrame(comparison_data)

st.subheader("Scenario Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Scenarios Compared", len(comparison_df))
col2.metric(
    "Highest Simulated Production",
    f"{comparison_df['Simulated Production'].max():,.2f}"
)
col3.metric(
    "Largest Production Change",
    f"{comparison_df['Change (%)'].max():.2f}%"
)

st.divider()

st.subheader("Production Comparison")

chart_df = comparison_df.melt(
    id_vars="Scenario",
    value_vars=["Baseline Production", "Simulated Production"],
    var_name="Production Type",
    value_name="Production"
)

fig = px.bar(
    chart_df,
    x="Scenario",
    y="Production",
    color="Production Type",
    barmode="group",
    title="Baseline vs Simulated Production"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Production Change by Scenario")

fig2 = px.bar(
    comparison_df,
    x="Scenario",
    y="Change (%)",
    color="Change (%)",
    title="Percentage Change in Production"
)

st.plotly_chart(fig2, use_container_width=True)

st.subheader("Detailed Comparison")
st.dataframe(comparison_df, use_container_width=True)

st.download_button(
    label="Download Comparison CSV",
    data=comparison_df.to_csv(index=False).encode("utf-8"),
    file_name="scenario_comparison.csv",
    mime="text/csv"
)
