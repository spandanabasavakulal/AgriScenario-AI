# AgriScenario AI
### Intelligent Agricultural Data Analysis and Scenario Simulation System

AgriScenario AI is a Python-based agricultural data analysis and decision-support application designed to help users explore historical Indian agricultural data, understand crop production patterns, perform what-if scenario simulations, compare agricultural scenarios, and obtain AI-powered insights through Google's Gemini API.

The application combines historical data analysis, data quality validation, mathematical scenario simulation, rule-based agent workflows, interactive visualizations, and Generative AI into a single web-based platform.

---

## Table of Contents

1. Project Overview
2. Problem Statement
3. Project Objectives
4. Key Features
5. System Architecture
6. Dataset Description
7. Data Preprocessing and Quality Validation
8. Application Modules
9. Scenario Simulation Methodology
10. Agent Workflow
11. Gemini AI Integration
12. Technology Stack
13. Project Folder Structure
14. Installation and Setup
15. Running the Application
16. Environment Configuration
17. Example Scenario
18. Data Flow
19. Results and Implementation Details
20. Limitations
21. Future Enhancements
22. Security Considerations
23. Conclusion

---

## 1. Project Overview

Agriculture plays an important role in India's economy. Understanding agricultural production, crop performance, cultivated area, and regional differences is essential for effective agricultural planning and decision-making.

However, agricultural datasets often contain missing values, inconsistent records, and large volumes of information that are difficult to analyze manually.

AgriScenario AI addresses these challenges through an interactive application that allows users to:

- Explore historical agricultural records.
- Analyze crop-wise and state-wise production.
- Understand historical agricultural trends.
- Identify data quality issues.
- Simulate changes in cultivated area and crop yield.
- Compare multiple agricultural scenarios.
- Generate analytical recommendations through specialized agents.
- Ask agricultural questions using natural language through Gemini AI.

The system focuses on historical agricultural analysis and hypothetical scenario simulation rather than claiming to provide machine-learning-based future predictions.

## 2. Problem Statement

Agricultural decision-making requires understanding historical production patterns and evaluating how changes in cultivated area and crop yield can influence agricultural output.

However, analyzing large agricultural datasets manually is time-consuming. Data quality issues can also affect the reliability of analytical results.

There is a need for an integrated system that can process historical agricultural records, visualize production patterns, simulate hypothetical agricultural conditions, compare alternative scenarios, and provide understandable analytical insights.

**Proposed Solution:**

AgriScenario AI provides a centralized web application that integrates agricultural data preprocessing, historical analysis, scenario simulation, scenario comparison, rule-based agent workflows, and Gemini-powered natural-language interaction.

## 3. Project Objectives

The main objectives are:

1. Collect and load historical Indian agricultural data.
2. Validate agricultural records and identify data quality issues.
3. Preserve original records while identifying analysis-ready records.
4. Visualize agricultural production and yield patterns.
5. Analyze crop-wise and state-wise agricultural performance.
6. Develop a mathematical scenario simulation engine.
7. Allow users to save and compare multiple scenarios.
8. Implement specialized rule-based agricultural analysis agents.
9. Integrate Gemini API for natural-language agricultural question answering.
10. Provide an interactive and user-friendly web application.

## 4. Key Features

| Feature | Description |
|---|---|
| Agricultural Dashboard | Displays overall dataset statistics and visualizations. |
| Historical Data Explorer | Allows filtering and downloading agricultural records. |
| Historical Analysis | Analyzes production, yield, crop and regional trends. |
| Scenario Builder | Simulates agricultural production under user-defined changes. |
| Scenario Comparison | Compares multiple saved simulation results. |
| Agent Workflow | Executes five specialized rule-based agents. |
| AI Insights | Provides Gemini-powered agricultural explanations and question answering. |
| Data Quality Validation | Identifies missing, invalid, duplicate and inconsistent records. |
| CSV Export | Allows users to download filtered agricultural data. |

## 5. System Architecture

AgriScenario AI follows a modular architecture consisting of a presentation layer, application logic layer, data layer, and AI integration layer.

### Architecture Components

**1. Presentation Layer – Streamlit**

Provides the interactive web interface through seven application pages.

**2. Application Logic Layer – Python**

Handles data loading, preprocessing, calculations, scenario simulation, agent execution, and application workflows.

**3. Data Layer – Hugging Face Dataset**

Provides historical Indian agricultural records for analysis.

**4. AI Integration Layer – Google Gemini API**

Processes natural-language questions and generates contextual agricultural explanations using supplied statistics.

**5. Output Layer**

Displays dashboards, historical trends, simulation results, scenario comparisons, recommendations, and AI-generated responses.

### Architecture Flow

```text
                    USER
                      |
                      v
             STREAMLIT APPLICATION
                      |
       +--------------+--------------+
       |              |              |
       v              v              v
   Dashboard      Historical      AI Insights
                  Analysis
       |              |              |
       +--------------+--------------+
                      |
                      v
             APPLICATION LOGIC
                      |
       +--------------+--------------+
       |              |              |
       v              v              v
   Data Loader   Calculations    Agent Workflow
       |              |              |
       v              v              |
 Data Processor  Scenario Engine     |
       |              |              |
       +--------------+--------------+
                      |
          +-----------+-----------+
          |                       |
          v                       v
    HUGGING FACE              GEMINI API
    AGRICULTURE DATA          AI PROCESSING
          |                       |
          +-----------+-----------+
                      |
                      v
                FINAL OUTPUT
                      |
       +--------------+--------------+
       |              |              |
       v              v              v
     Charts       Simulations    AI Responses
```

## 6. Dataset Description

The application uses the following Hugging Face dataset:

**Dataset ID:** `therajasekhar/india-public-agriculture`

**Platform:** Hugging Face Datasets

**Dataset loading library:** `datasets`

**Historical period:** 2010–2017

**Total records:** 72,036

### Important Dataset Attributes

| Column | Description |
|---|---|
| crop | Agricultural crop name |
| state | Indian state |
| district | District name |
| year | Agricultural year |
| area_1000_ha | Cultivated area in thousand hectares |
| production_1000_t | Production in thousand tonnes |
| yield_kg_per_ha | Agricultural yield in kilograms per hectare |

### Dataset Loading

The dataset is loaded using the Hugging Face `load_dataset()` function.

```python
from datasets import load_dataset

dataset = load_dataset(
    "therajasekhar/india-public-agriculture",
    split="train"
)

df = dataset.to_pandas()
```

The loaded dataset is converted into a Pandas DataFrame for further processing and analysis.

## 7. Data Preprocessing and Quality Validation

Data preprocessing is implemented through:

`core/data_loader.py`

`core/data_processor.py`

The data loader retrieves the agricultural dataset and validates the required columns.

The data processor performs data quality checks and creates additional indicators to identify problematic records.

### Implemented Validation Checks

**1. Missing Value Detection**

Identifies records containing missing values in important agricultural attributes.

**2. Numeric Validation**

Checks numeric agricultural fields and identifies invalid numeric values.

**3. Duplicate Detection**

Identifies duplicate records using the record identification logic.

**4. Zero-Value Analysis**

Identifies records with zero area, zero production, zero yield, and other zero-value patterns.

**5. Production Consistency Validation**

Checks whether recorded production is consistent with cultivated area and yield.

The validation formula is:

```text
Expected Production =
(Area × Yield) / 1000
```

The system compares expected production against recorded production using numerical tolerance.

**6. Analysis-Ready Record Identification**

Creates an `analysis_ready` indicator to identify records suitable for the application's main analytical calculations.

### Important Data Preservation Strategy

The system does not delete original agricultural records during preprocessing.

Instead, it preserves all records and flags problematic records separately.

This allows users to retain the original dataset while using a more reliable subset for analytical calculations.

### Actual Preprocessing Results

The following results were obtained during implementation:

| Data Quality Metric | Result |
|---|---:|
| Original records | 72,036 |
| Preserved records | 72,036 |
| Analysis-ready records | 35,493 |
| Missing records flagged | 14,904 |
| Invalid records flagged | 0 |
| Duplicate records flagged | 0 |
| Zero-area records | 26,178 |
| Zero-area records with production | 169 |
| Zero-activity records | 21,151 |
| Zero-production records | 821 |
| Zero-yield records | 674 |
| Production-consistent records | 35,493 |
| Production-inconsistent records | 61 |
| Consistency not evaluated | 36,482 |

**Important:** The 36,482 records for which consistency was not evaluated should not be interpreted as confirmed consistent records. The 35,493 analysis-ready records form the main analytical subset.

## 8. Application Modules

The application contains seven major modules.

### 8.1 Dashboard

The Dashboard provides an overall summary of the agricultural dataset.

**Implemented functionality:**

- Displays total agricultural records.
- Displays the number of crops, states, and districts.
- Shows the historical year range.
- Displays missing and inconsistent record statistics.
- Visualizes zero-value patterns.
- Displays production consistency information.
- Shows crop distribution.
- Shows state-wise distribution.
- Displays historical production trends.
- Identifies top-producing crops.
- Provides dataset preview.
- Supports CSV export.

The Dashboard helps users understand the dataset before performing detailed analysis.

### 8.2 Historical Data Explorer

The Historical Data module allows users to explore individual agricultural records.

**Implemented functionality:**

- Crop-based filtering.
- State-based filtering.
- Year-based filtering.
- Display of filtered historical records.
- Dataset overview metrics.
- CSV download functionality.

The module uses the analysis-ready dataset for its main record exploration workflow.

### 8.3 Historical Analysis

The Historical Analysis module focuses on identifying agricultural production and yield patterns.

**Implemented functionality:**

- Overall agricultural performance metrics.
- Year-wise production trends.
- Crop-wise production analysis.
- State-wise production analysis.
- Crop yield comparison.
- Interactive Plotly visualizations.
- Detailed agricultural data tables.

This module helps users understand historical differences in crop production and regional performance.

### 8.4 Scenario Builder

The Scenario Builder is a mathematical what-if simulation module.

It allows users to select:

- Crop.
- State.
- Year.
- Area change percentage.
- Yield change percentage.

The system calculates baseline agricultural metrics and uses the user-defined changes to calculate simulated agricultural production.

**Example:**

Suppose the baseline values are:

```text
Baseline Area       = 100
Baseline Production = 500
Baseline Yield      = 5000

Area Change         = +10%
Yield Change        = +5%
```

The application calculates:

```text
New Area = 100 × 1.10

New Yield = 5000 × 1.05

New Production = 500 × 1.10 × 1.05

New Production = 577.5
```

The module displays:

- Baseline area.
- Simulated area.
- Baseline production.
- Simulated production.
- Baseline yield.
- Simulated yield.
- Production difference.
- Production percentage change.

The user can also save the scenario for comparison.

### 8.5 Scenario Comparison

The Scenario Comparison module allows users to compare multiple saved scenarios.

After generating a scenario in Scenario Builder, users can save it with a scenario name.

The application stores the scenario details in Streamlit Session State.

The comparison module retrieves saved scenarios and displays:

- Scenario names.
- Baseline production.
- Simulated production.
- Production difference.
- Percentage change.
- Comparative metrics.
- Interactive charts.
- CSV export.

**Example:**

| Scenario | Area Change | Yield Change |
|---|---:|---:|
| Baseline | 0% | 0% |
| Scenario A | +10% | +5% |
| Scenario B | +5% | +10% |

Users can compare the resulting simulated production to understand the impact of different assumptions.

**Storage Note:** Scenario results are currently stored in Streamlit Session State. They are temporary and are not persisted in a permanent database.

### 8.6 Agent Workflow

The Agent Workflow module divides agricultural analysis into five specialized rule-based agents.

Each agent performs a particular analytical responsibility.

**Agent 1 – Data Quality Agent**

Examines dataset quality indicators, including missing records and production inconsistencies.

**Agent 2 – Production Analysis Agent**

Analyzes crop production and identifies important production patterns.

**Agent 3 – Regional Analysis Agent**

Examines state-wise agricultural production and identifies leading regions.

**Agent 4 – Agricultural Risk Agent**

Examines agricultural data risk indicators such as zero-area and zero-production patterns.

**Agent 5 – Recommendation Agent**

Generates recommendations based on the findings and available data quality information.

### Agent Workflow Process

```text
       AGRICULTURAL DATA
                |
                v
        DATA QUALITY AGENT
                |
                v
      PRODUCTION ANALYSIS AGENT
                |
                v
       REGIONAL ANALYSIS AGENT
                |
                v
      AGRICULTURAL RISK AGENT
                |
                v
       RECOMMENDATION AGENT
                |
                v
        FINAL AGENT SUMMARY
```

The agents are implemented using rule-based Python logic. They are not five independent generative AI models.

### 8.7 AI Insights – Gemini Integration

The AI Insights module integrates Google's Gemini API to provide natural-language interaction with agricultural data.

The application supports two main AI features.

**A. Gemini-Powered Agricultural Insights**

The application prepares selected agricultural statistics and sends them to Gemini.

Gemini generates an explanation under sections such as:

- Overall Agricultural Performance.
- Important Crop Insights.
- Regional Performance.
- Production and Yield Interpretation.
- Practical Agricultural Recommendations.
- Limitations and Uncertainties.

**B. Ask AgriScenario AI**

Users can enter questions through a text input interface.

Example questions:

```text
Which crop has the highest production?

Explain the historical agricultural trends.

Which state has the highest production?

How does increasing cultivated area
affect agricultural production?
```

### Gemini Question-Answering Workflow

```text
        USER QUESTION
              |
              v
       AI INSIGHTS PAGE
              |
              v
      PREPARE AGRICULTURAL
          STATISTICS
              |
              v
       GEMINI CLIENT
              |
              v
        GEMINI API
              |
              v
       GENERATED RESPONSE
              |
              v
        DISPLAY IN CHAT
```

The Gemini client is implemented in:

`core/gemini_client.py`

The integration uses the Google Gen AI Python SDK.

The model configured in the current implementation is:

`gemini-3.6-flash`

The application sends the user's question, relevant agricultural statistics, and recent conversation history to Gemini.

The generated response is displayed in the Streamlit chat interface.

The integration uses the supplied agricultural context for numerical claims. Its answers depend on the completeness of the statistics passed into the prompt.

## 9. Scenario Simulation Methodology

Scenario simulation is implemented in:

`core/calculations.py`

The application calculates the impact of area and yield changes on baseline agricultural production.

### Mathematical Formula

Let:

- \(P_b\) = Baseline production
- \(A\) = Area change percentage
- \(Y\) = Yield change percentage

The simulated production is:

\[
P_s = P_b \times (1 + A/100) \times (1 + Y/100)
\]

Production difference:

\[
D = P_s - P_b
\]

Production percentage change:

\[
C = \frac{P_s-P_b}{P_b}\times100
\]

### Implementation Example

```python
from core.calculations import simulate_scenario

result = simulate_scenario(
    baseline_area=100,
    baseline_production=500,
    baseline_yield=5000,
    area_change_pct=10,
    yield_change_pct=5
)

print(result)
```

Expected output includes:

```text
baseline_area: 100
baseline_production: 500
baseline_yield: 5000

simulated_area: 110
simulated_production: 577.5
simulated_yield: 5250

area_change_pct: 10
yield_change_pct: 5

production_difference: 77.5
production_change_pct: 15.5
```

### Scenario Verification

The application also includes scenario verification through the `verify_scenario()` function.

This checks the calculated scenario result according to the implemented verification logic.

**Methodological Note:** The scenario engine performs deterministic mathematical simulation using user-defined assumptions. It does not train a machine-learning model or predict actual future agricultural output.

## 10. Technology Stack

| Technology | Implementation Purpose |
|---|---|
| Python | Core application programming |
| Streamlit | Web interface and application pages |
| Pandas | Data loading, transformation and analysis |
| NumPy | Numerical calculations and validation |
| Plotly Express | Interactive charts and graphs |
| Hugging Face Datasets | Agricultural dataset retrieval |
| Google Gen AI SDK | Gemini API communication |
| Google Gemini | Natural-language AI responses |
| Streamlit Session State | Temporary scenario and chat state |
| Git and GitHub | Version control and source code management |
| VS Code | Development environment |

## 11. Project Folder Structure

```text
agri-scenario-ai/
│
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml
│
├── core/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── data_processor.py
│   ├── calculations.py
│   └── gemini_client.py
│
├── pages/
│   ├── 1_Dashboard.py
│   ├── 2_Historical_Data.py
│   ├── 3_Historical_Analysis.py
│   ├── 4_Scenario_Builder.py
│   ├── 5_Scenario_Comparison.py
│   ├── 6_Agent_Workflow.py
│   └── 7_AI_Insights.py
│
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

### Important Files

| File | Responsibility |
|---|---|
| `app.py` | Main Streamlit application entry point |
| `data_loader.py` | Loads agricultural dataset |
| `data_processor.py` | Performs preprocessing and quality checks |
| `calculations.py` | Performs baseline and scenario calculations |
| `gemini_client.py` | Integrates Gemini API |
| `1_Dashboard.py` | Displays agricultural dashboard |
| `2_Historical_Data.py` | Displays and filters historical records |
| `3_Historical_Analysis.py` | Performs historical agricultural analysis |
| `4_Scenario_Builder.py` | Simulates agricultural scenarios |
| `5_Scenario_Comparison.py` | Compares saved scenarios |
| `6_Agent_Workflow.py` | Executes rule-based agents |
| `7_AI_Insights.py` | Provides AI insights and question answering |

## 12. Installation and Setup

Follow these instructions to run the project locally.

### Step 1: Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### Step 2: Navigate to the Project Directory

```bash
cd agri-scenario-ai
```

### Step 3: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 4: Activate the Virtual Environment

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```cmd
venv\Scripts\activate
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Configure Gemini API

Create a Google Gemini API key through Google AI Studio:

https://aistudio.google.com/apikey

Create the following file:

`.streamlit/secrets.toml`

Add:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

Replace the placeholder with your actual API key.

Do not upload the API key to GitHub.

### Step 7: Run the Application

```bash
streamlit run app.py
```

The application will be available at:

```text
http://localhost:8501
```

## 13. Environment Configuration

The application uses Streamlit Secrets to securely access the Gemini API key.

Example:

```toml
GEMINI_API_KEY = "your_api_key"
```

The Gemini client accesses the configured key through:

```python
import streamlit as st
from google import genai

api_key = st.secrets.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)
```

For deployment, configure the same secret through the hosting platform's secret management settings.

## 14. Example Scenario

Consider an agricultural scenario in which the baseline production is 500 thousand tonnes.

The user assumes:

- Cultivated area increases by 10%.
- Crop yield increases by 5%.

The application calculates:

\[
500 \times 1.10 \times 1.05 = 577.5
\]

| Metric | Baseline | Simulated |
|---|---:|---:|
| Area | 100 | 110 |
| Production | 500 | 577.5 |
| Yield | 5,000 | 5,250 |

The simulated production increases by 77.5 thousand tonnes, representing a 15.5% increase.

The result demonstrates how changes in area and yield can influence production under the selected assumptions.

## 15. Complete Data Flow

The complete application follows this workflow:

1. The user opens the Streamlit application.
2. The application loads the historical agricultural dataset from Hugging Face.
3. The data loader converts the dataset into a Pandas DataFrame.
4. The data processor validates the agricultural records.
5. The application identifies analysis-ready records.
6. The dashboard displays dataset statistics and visualizations.
7. Users explore historical data and agricultural trends.
8. The Scenario Builder calculates hypothetical production changes.
9. The Scenario Comparison module compares saved simulation results.
10. The Agent Workflow executes specialized rule-based analytical components.
11. The AI Insights module prepares relevant statistics and user questions.
12. Gemini generates contextual natural-language responses.
13. The application displays the final analytical results.

## 16. Implementation Results

The application successfully implements the following major capabilities:

- Loading 72,036 historical agricultural records.
- Preserving original records during preprocessing.
- Identifying 35,493 analysis-ready records.
- Performing data quality checks.
- Visualizing crop-wise and state-wise production.
- Analyzing historical agricultural trends.
- Performing area and yield-based scenario simulations.
- Saving and comparing scenarios within the current Streamlit session.
- Executing five specialized rule-based agents.
- Integrating Google Gemini for agricultural question answering.
- Exporting filtered agricultural data as CSV.

## 17. Limitations

The current implementation has the following limitations:

1. **Historical Dataset:** The current dataset covers 2010–2017 and does not automatically represent current agricultural conditions.

2. **Scenario Simulation:** The Scenario Builder uses mathematical calculations and user assumptions rather than trained predictive models.

3. **Temporary Scenario Storage:** Scenario results are stored in Streamlit Session State and are not permanently stored in a database.

4. **Rule-Based Agents:** The five agents use predefined analytical logic and are not independent autonomous LLM agents.

5. **Gemini Response Quality:** The quality of AI responses depends on the statistics and context supplied to the Gemini API.

6. **Data Coverage:** Agricultural conclusions are limited to the available dataset and the records selected for analysis.

## 18. Future Enhancements

Potential improvements include:

- Integration of more recent agricultural datasets.
- Addition of machine-learning-based crop production forecasting.
- Permanent scenario storage using SQLite or PostgreSQL.
- Improved scenario management and historical comparison.
- Integration of weather and soil information.
- More advanced agricultural risk assessment.
- Improved agent coordination and reasoning.
- More comprehensive data-grounded Gemini question answering.
- Deployment as a publicly accessible web application.

## 19. Security Considerations

- Gemini API keys must be stored using Streamlit Secrets.
- Never commit `.streamlit/secrets.toml` to GitHub.
- Add secret files to `.gitignore`.
- Avoid printing API keys in application logs.
- Keep API credentials separate from application source code.

## 20. Conclusion

AgriScenario AI provides an integrated platform for understanding historical agricultural performance and exploring hypothetical agricultural production scenarios.

By combining agricultural data preprocessing, interactive visualization, historical analysis, mathematical simulation, rule-based agent workflows, and Generative AI, the application makes agricultural information easier to explore and understand.

The platform provides users with a structured way to examine agricultural records, compare alternative production assumptions, and interact with agricultural statistics through natural-language questions.

The project demonstrates the practical integration of Python, data analytics, Streamlit, and Generative AI in an agricultural decision-support application.

---

## 👩‍💻 Development

**Project:** AgriScenario AI

**Domain:** Agriculture | Data Analytics | Generative AI | Decision Support

**Primary Language:** Python

**Application Framework:** Streamlit

**AI Integration:** Google Gemini API

**Dataset Platform:** Hugging Face

---

**Disclaimer:** AgriScenario AI is an analytical and educational decision-support application. Its historical analysis and hypothetical scenario calculations should not be interpreted as guaranteed agricultural outcomes or professional agronomic advice.
