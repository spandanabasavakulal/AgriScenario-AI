
import streamlit as st
import pandas as pd
import plotly.express as px

from core.data_loader import load_agriculture_data
from core.data_processor import preprocess_data
from core.gemini_client import (
    generate_ai_insights,
    ask_agriculture_question
)

st.set_page_config(
    page_title="AI Insights | AgriScenario AI",
    page_icon="💡",
    layout="wide"
)

st.title("AI-Powered Agricultural Insights")
st.caption(
    "Explore historical agricultural statistics "
    "and interact with Gemini AI."
)


# ---------------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------------

@st.cache_data(show_spinner=False)
def prepare_data():
    raw_df = load_agriculture_data()
    return preprocess_data(raw_df)


try:
    with st.spinner("Loading agricultural dataset..."):
        processed_df, report = prepare_data()

except Exception as e:
    st.error(f"Data loading failed: {e}")
    st.stop()


if "analysis_ready" not in processed_df.columns:
    st.error("The analysis_ready column is missing.")
    st.stop()


analysis_df = processed_df[
    processed_df["analysis_ready"] == True
].copy()


if analysis_df.empty:
    st.warning("No analysis-ready records are available.")
    st.stop()


# ---------------------------------------------------------
# 2. SIDEBAR FILTERS
# ---------------------------------------------------------

st.sidebar.header("Insight Filters")

crops = sorted(
    analysis_df["crop"].dropna().astype(str).unique().tolist()
)

states = sorted(
    analysis_df["state"].dropna().astype(str).unique().tolist()
)

selected_crop = st.sidebar.selectbox(
    "Select Crop",
    ["All"] + crops
)

selected_state = st.sidebar.selectbox(
    "Select State",
    ["All"] + states
)


filtered_df = analysis_df.copy()

if selected_crop != "All":
    filtered_df = filtered_df[
        filtered_df["crop"].astype(str) == selected_crop
    ]

if selected_state != "All":
    filtered_df = filtered_df[
        filtered_df["state"].astype(str) == selected_state
    ]


if filtered_df.empty:
    st.warning(
        "No records match the selected filters. "
        "Change the crop or state."
    )
    st.stop()


# ---------------------------------------------------------
# 3. AGRICULTURAL STATISTICS
# ---------------------------------------------------------

crop_production = (
    filtered_df.groupby("crop")["production_1000_t"]
    .sum()
    .sort_values(ascending=False)
)

state_production = (
    filtered_df.groupby("state")["production_1000_t"]
    .sum()
    .sort_values(ascending=False)
)


crop_yield_df = filtered_df.groupby("crop").agg(
    total_production=("production_1000_t", "sum"),
    total_area=("area_1000_ha", "sum")
)

crop_yield_df["yield_kg_per_ha"] = (
    crop_yield_df["total_production"] * 1000
    / crop_yield_df["total_area"].replace(0, pd.NA)
)

crop_yield = (
    crop_yield_df["yield_kg_per_ha"]
    .dropna()
    .sort_values(ascending=False)
)


yearly_production = (
    filtered_df.groupby("year")["production_1000_t"]
    .sum()
    .reset_index()
    .sort_values("year")
)


total_production = float(
    filtered_df["production_1000_t"].sum()
)

total_area = float(
    filtered_df["area_1000_ha"].sum()
)

average_yield = (
    total_production * 1000 / total_area
    if total_area > 0 else 0.0
)


# ---------------------------------------------------------
# 4. KEY METRICS
# ---------------------------------------------------------

st.subheader("Key Agricultural Insights")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Records Analyzed",
    f"{len(filtered_df):,}"
)

c2.metric(
    "Crops",
    int(filtered_df["crop"].nunique())
)

c3.metric(
    "States",
    int(filtered_df["state"].nunique())
)

c4.metric(
    "Total Production",
    f"{total_production:,.2f} thousand tonnes"
)


# ---------------------------------------------------------
# 5. CROP PERFORMANCE
# ---------------------------------------------------------

st.divider()
st.subheader("Crop Performance Insights")

if not crop_production.empty:

    st.write(
        f"**Highest production crop:** "
        f"{crop_production.index[0]}"
    )

    plot_df = (
        crop_production
        .rename("production_1000_t")
        .reset_index()
    )

    fig = px.bar(
        plot_df,
        x="crop",
        y="production_1000_t",
        title="Production by Crop",
        labels={
            "crop": "Crop",
            "production_1000_t": "Production (1000 tonnes)"
        }
    )

    st.plotly_chart(fig, width="stretch")


# ---------------------------------------------------------
# 6. REGIONAL PERFORMANCE
# ---------------------------------------------------------

st.subheader("Regional Performance Insights")

if not state_production.empty:

    st.write(
        f"**Highest production state:** "
        f"{state_production.index[0]}"
    )

    plot_df = (
        state_production.head(10)
        .rename("production_1000_t")
        .reset_index()
    )

    fig = px.bar(
        plot_df,
        x="state",
        y="production_1000_t",
        title="Top 10 Producing States",
        labels={
            "state": "State",
            "production_1000_t": "Production (1000 tonnes)"
        }
    )

    st.plotly_chart(fig, width="stretch")


# ---------------------------------------------------------
# 7. CROP YIELD ANALYSIS
# ---------------------------------------------------------

st.subheader("Crop Yield Insights")

if not crop_yield.empty:

    st.write(
        f"**Highest aggregate yield crop:** "
        f"{crop_yield.index[0]}"
    )

    plot_df = (
        crop_yield
        .rename("yield_kg_per_ha")
        .reset_index()
    )

    fig = px.bar(
        plot_df,
        x="crop",
        y="yield_kg_per_ha",
        title="Area-Weighted Yield by Crop",
        labels={
            "crop": "Crop",
            "yield_kg_per_ha": "Yield (kg/ha)"
        }
    )

    st.plotly_chart(fig, width="stretch")


# ---------------------------------------------------------
# 8. HISTORICAL TRENDS
# ---------------------------------------------------------

st.subheader("Historical Production Trends")

fig = px.line(
    yearly_production,
    x="year",
    y="production_1000_t",
    markers=True,
    title="Year-wise Agricultural Production",
    labels={
        "year": "Year",
        "production_1000_t": "Production (1000 tonnes)"
    }
)

st.plotly_chart(fig, width="stretch")


# ---------------------------------------------------------
# 9. RULE-BASED RECOMMENDATIONS
# ---------------------------------------------------------

st.divider()
st.subheader("Agricultural Recommendations")

recommendations = []

if report.get("production_inconsistent", 0) > 0:
    recommendations.append(
        "Investigate records flagged for production inconsistency."
    )

if report.get("missing_records_flagged", 0) > 0:
    recommendations.append(
        "Review records with missing values to improve data completeness."
    )

if not crop_production.empty:
    recommendations.append(
        f"Study {crop_production.index[0]} "
        "as the highest-producing crop in the selected data."
    )

if not state_production.empty:
    recommendations.append(
        f"Examine agricultural practices in "
        f"{state_production.index[0]}, "
        "the highest-producing state in the selected data."
    )

for i, item in enumerate(recommendations, start=1):
    st.write(f"**{i}.** {item}")


# ---------------------------------------------------------
# 10. PREPARE VERIFIED DATA FOR GEMINI
# ---------------------------------------------------------

agricultural_data = {
    "dataset": "Indian Historical Agriculture Dataset",
    "selected_crop": selected_crop,
    "selected_state": selected_state,
    "records_analyzed": int(len(filtered_df)),
    "total_production_1000_tonnes": round(total_production, 2),
    "total_area_1000_hectares": round(total_area, 2),
    "average_yield_kg_per_ha": round(average_yield, 2),
    "crops_analyzed": int(filtered_df["crop"].nunique()),
    "states_analyzed": int(filtered_df["state"].nunique()),

    "top_producing_crop": (
        str(crop_production.index[0])
        if not crop_production.empty else None
    ),

    "top_producing_state": (
        str(state_production.index[0])
        if not state_production.empty else None
    ),

    "highest_yield_crop": (
        str(crop_yield.index[0])
        if not crop_yield.empty else None
    ),

    "yearly_production": {
        str(row["year"]): round(
            float(row["production_1000_t"]), 2
        )
        for _, row in yearly_production.iterrows()
    },

    "data_quality": {
        "original_records": int(
            report.get("original_records", 0)
        ),
        "preserved_records": int(
            report.get("preserved_records", 0)
        ),
        "analysis_ready_records": int(
            report.get("analysis_ready_records", 0)
        ),
        "missing_records_flagged": int(
            report.get("missing_records_flagged", 0)
        ),
        "production_inconsistent": int(
            report.get("production_inconsistent", 0)
        )
    }
}


# ---------------------------------------------------------
# 11. GEMINI AI AGRICULTURAL INSIGHTS
# ---------------------------------------------------------

st.divider()
st.header("Gemini-Powered Agricultural Advisor")

st.write(
    "Generate an AI interpretation of the actual "
    "statistics in the selected dataset."
)

if st.button(
    "Generate AI Agricultural Insights",
    type="primary",
    width="stretch"
):

    try:
        with st.spinner(
            "Gemini is analyzing agricultural statistics..."
        ):

            result = generate_ai_insights(
                agricultural_data
            )

        st.session_state["gemini_agri_insights"] = result

        st.session_state["gemini_insights_filter"] = (
            selected_crop,
            selected_state
        )

    except Exception as e:
        st.error(f"Gemini API Error: {e}")


if (
    "gemini_agri_insights" in st.session_state
    and st.session_state.get("gemini_insights_filter")
    == (selected_crop, selected_state)
):

    st.subheader("AI-Generated Analysis")

    st.markdown(
        st.session_state["gemini_agri_insights"]
    )


# ---------------------------------------------------------
# 12. ASK AGRISCENARIO AI - USER INPUT CHAT
# ---------------------------------------------------------

st.divider()

st.header("Ask AgriScenario AI")

st.write(
    "Ask questions about agricultural production, "
    "crop performance, state-wise statistics, "
    "yield, or historical trends."
)

st.info(
    f"Gemini is currently using data for "
    f"Crop: {selected_crop} | State: {selected_state}"
)


# Separate chat history for each filter selection
chat_key = f"agri_chat_{selected_crop}_{selected_state}"

if chat_key not in st.session_state:
    st.session_state[chat_key] = []


# Display previous messages
for message in st.session_state[chat_key]:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# User input form
# Normal form keeps the input box at this position
# instead of pinning it to the bottom of the page.

with st.form(
    key=f"agri_question_form_{selected_crop}_{selected_state}",
    clear_on_submit=True
):

    user_question = st.text_area(
        "Enter your agricultural question",
        placeholder=(
            "Example: Which crop has the highest production? "
            "Compare the top two crops."
        ),
        height=100
    )

    submitted = st.form_submit_button(
        "Send Question",
        type="primary",
        width="stretch"
    )


if submitted:

    question = user_question.strip()

    if not question:

        st.warning("Please enter a question before submitting.")

    else:

        previous_history = (
            st.session_state[chat_key].copy()
        )

        st.session_state[chat_key].append({
            "role": "user",
            "content": question
        })

        try:

            with st.spinner(
                "AgriScenario AI is generating your answer..."
            ):

                answer = ask_agriculture_question(
                    question=question,
                    agricultural_data=agricultural_data,
                    chat_history=previous_history
                )

            st.session_state[chat_key].append({
                "role": "assistant",
                "content": answer
            })

            st.rerun()

        except Exception as e:

            st.session_state[chat_key].pop()

            st.error(
                f"Unable to generate response: {e}"
            )


# Clear chat
if st.button(
    "Clear Chat",
    key=f"clear_agri_chat_{selected_crop}_{selected_state}"
):

    st.session_state[chat_key] = []
    st.rerun()


# ---------------------------------------------------------
# 13. DOWNLOAD AGRICULTURAL DATA
# ---------------------------------------------------------

# Download section intentionally comes AFTER the question box.

st.divider()

st.subheader("Download Agricultural Data")

st.download_button(
    label="Download Filtered Agricultural Data",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="agri_scenario_insights.csv",
    mime="text/csv",
    width="stretch"
)
