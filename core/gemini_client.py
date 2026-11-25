
import streamlit as st
from google import genai

MODEL_NAME = "gemini-3.6-flash"


def get_gemini_client():
    api_key = st.secrets.get("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. "
            "Check .streamlit/secrets.toml."
        )

    return genai.Client(api_key=api_key)


def generate_ai_insights(agricultural_data):
    client = get_gemini_client()

    prompt = f"""
You are an agricultural data analysis assistant.

Analyze the following verified agricultural statistics:

{agricultural_data}

Provide your response under these headings:

1. Overall Agricultural Performance
2. Important Crop Insights
3. Regional Performance
4. Production and Yield Interpretation
5. Practical Agricultural Recommendations
6. Limitations and Uncertainties

Rules:
- Use only the supplied statistics for numerical claims.
- Do not invent missing data.
- Distinguish observations from recommendations.
- Do not claim correlation proves causation.
- Do not present historical statistics as future predictions.
- Use clear, professional language.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text


def ask_agriculture_question(question, agricultural_data, chat_history=None):
    client = get_gemini_client()

    history_text = ""

    if chat_history:
        for message in chat_history[-8:]:
            role = "User" if message["role"] == "user" else "Assistant"
            history_text += f"\n{role}: {message['content']}"

    prompt = f"""
You are AgriScenario AI, an intelligent agricultural data assistant.

You help users understand Indian agricultural statistics.

AVAILABLE VERIFIED DATA:
{agricultural_data}

PREVIOUS CONVERSATION:
{history_text}

CURRENT USER QUESTION:
{question}

INSTRUCTIONS:
1. Answer clearly and directly.
2. Use the supplied agricultural data for numerical claims.
3. Never invent statistics or unsupported facts.
4. Respect the selected crop and state filters.
5. If the data does not contain the answer, explain that clearly.
6. Distinguish historical observations from future predictions.
7. Explain technical agricultural concepts in simple language.
8. For questions unrelated to agriculture or the supplied dataset,
   politely explain your scope.
9. Maintain context from previous messages.

Provide a helpful, structured answer.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text

