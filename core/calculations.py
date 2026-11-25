
import pandas as pd
import numpy as np


# ============================================================
# 1. REQUIRED COLUMNS
# ============================================================

REQUIRED_COLUMNS = [
    "area_1000_ha",
    "production_1000_t",
    "yield_kg_per_ha"
]


# ============================================================
# 2. INPUT VALIDATION
# ============================================================

def validate_inputs(area_change_pct, yield_change_pct):

    try:
        area_change_pct = float(area_change_pct)
        yield_change_pct = float(yield_change_pct)

    except (TypeError, ValueError):
        raise ValueError("Scenario changes must be numeric.")

    if not np.isfinite(area_change_pct) or not np.isfinite(yield_change_pct):
        raise ValueError("Scenario changes must be finite.")

    if not -100 < area_change_pct <= 500:
        raise ValueError("Area change must be greater than -100% and at most 500%.")

    if not -100 < yield_change_pct <= 500:
        raise ValueError("Yield change must be greater than -100% and at most 500%.")

    return area_change_pct, yield_change_pct


# ============================================================
# 3. BASELINE METRICS
# ============================================================

def get_baseline_metrics(df, include_inconsistent=False):

    if not isinstance(df, pd.DataFrame) or df.empty:
        raise ValueError("A non-empty pandas DataFrame is required.")

    missing = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    data = df.copy()

    for col in REQUIRED_COLUMNS:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.replace([np.inf, -np.inf], np.nan)

    data = data.dropna(subset=REQUIRED_COLUMNS)

    data = data[
        (data["area_1000_ha"] > 0) &
        (data["production_1000_t"] >= 0) &
        (data["yield_kg_per_ha"] >= 0)
    ].copy()

    # Exclude production-inconsistent records by default
    if (
        not include_inconsistent
        and "production_consistent" in data.columns
    ):
        data = data[
            data["production_consistent"].eq(True)
        ].copy()

    if data.empty:
        raise ValueError("No eligible records available for baseline calculation.")

    # If multiple years are selected, calculate annual totals
    if "year" in data.columns:

        annual = (
            data.groupby("year")
            .agg(
                area=("area_1000_ha", "sum"),
                production=("production_1000_t", "sum")
            )
        )

        baseline_area = annual["area"].mean()
        baseline_production = annual["production"].mean()

        # Average annual area-weighted yield
        weighted_yield = (
            data["area_1000_ha"] *
            data["yield_kg_per_ha"]
        ).sum() / data["area_1000_ha"].sum()

        years_included = int(data["year"].nunique())

    else:

        baseline_area = data["area_1000_ha"].sum()
        baseline_production = data["production_1000_t"].sum()

        weighted_yield = (
            data["area_1000_ha"] *
            data["yield_kg_per_ha"]
        ).sum() / baseline_area

        years_included = 1

    values = [
        baseline_area,
        baseline_production,
        weighted_yield
    ]

    if not all(np.isfinite(v) for v in values):
        raise ValueError("Baseline calculation generated invalid values.")

    return {
        "baseline_area": float(baseline_area),
        "baseline_production": float(baseline_production),
        "baseline_yield": float(weighted_yield),
        "record_count": int(len(data)),
        "years_included": years_included
    }


# ============================================================
# 4. SCENARIO SIMULATION
# ============================================================

def simulate_scenario(
    baseline_area,
    baseline_production,
    baseline_yield,
    area_change_pct,
    yield_change_pct
):

    area_change_pct, yield_change_pct = validate_inputs(
        area_change_pct,
        yield_change_pct
    )

    try:
        baseline_area = float(baseline_area)
        baseline_production = float(baseline_production)
        baseline_yield = float(baseline_yield)

    except (TypeError, ValueError):
        raise ValueError("Baseline metrics must be numeric.")

    values = [
        baseline_area,
        baseline_production,
        baseline_yield
    ]

    if not all(np.isfinite(v) for v in values):
        raise ValueError("Baseline values must be finite.")

    if baseline_area <= 0:
        raise ValueError("Baseline area must be positive.")

    if baseline_production < 0 or baseline_yield < 0:
        raise ValueError("Production and yield cannot be negative.")

    area_factor = 1 + area_change_pct / 100
    yield_factor = 1 + yield_change_pct / 100

    simulated_area = baseline_area * area_factor

    simulated_yield = baseline_yield * yield_factor

    simulated_production = (
        baseline_production *
        area_factor *
        yield_factor
    )

    results = [
        simulated_area,
        simulated_yield,
        simulated_production
    ]

    if not all(np.isfinite(v) for v in results):
        raise ValueError("Simulation generated invalid numerical results.")

    production_difference = (
        simulated_production - baseline_production
    )

    production_change_pct = (
        production_difference / baseline_production * 100
        if baseline_production > 0
        else None
    )

    return {
        "baseline_area": baseline_area,
        "baseline_production": baseline_production,
        "baseline_yield": baseline_yield,

        "simulated_area": float(simulated_area),
        "simulated_production": float(simulated_production),
        "simulated_yield": float(simulated_yield),

        "area_change_pct": area_change_pct,
        "yield_change_pct": yield_change_pct,

        "production_difference": float(production_difference),

        "production_change_pct": (
            float(production_change_pct)
            if production_change_pct is not None
            else None
        ),

        "area_factor": float(area_factor),
        "yield_factor": float(yield_factor)
    }


# ============================================================
# 5. SCENARIO VERIFICATION
# ============================================================

def verify_scenario(result):

    if not isinstance(result, dict):
        raise ValueError("Scenario result must be a dictionary.")

    required = [
        "baseline_production",
        "simulated_production",
        "area_factor",
        "yield_factor"
    ]

    missing = [key for key in required if key not in result]

    if missing:
        raise ValueError(f"Missing scenario values: {missing}")

    try:
        baseline = float(result["baseline_production"])
        actual = float(result["simulated_production"])
        area_factor = float(result["area_factor"])
        yield_factor = float(result["yield_factor"])

    except (TypeError, ValueError):
        raise ValueError("Scenario verification values must be numeric.")

    values = [baseline, actual, area_factor, yield_factor]

    if not all(np.isfinite(v) for v in values):
        raise ValueError("Verification values must be finite.")

    if baseline < 0 or actual < 0:
        raise ValueError("Production cannot be negative.")

    if area_factor <= 0 or yield_factor <= 0:
        raise ValueError("Adjustment factors must be positive.")

    expected = baseline * area_factor * yield_factor

    if not np.isfinite(expected):
        raise ValueError("Expected production exceeds numerical limits.")

    is_valid = np.isclose(
        expected,
        actual,
        rtol=1e-9,
        atol=1e-9
    )

    return {
        "is_valid": bool(is_valid),
        "expected_production": float(expected),
        "calculated_production": float(actual),
        "difference": float(abs(expected - actual))
    }


# ============================================================
# 6. MULTIPLE SCENARIO COMPARISON
# ============================================================

def compare_scenarios(baseline, scenarios):

    if not isinstance(baseline, dict):
        raise ValueError("Baseline must be a dictionary.")

    if not isinstance(scenarios, dict):
        raise ValueError("Scenarios must be a dictionary.")

    required_baseline = [
        "baseline_area",
        "baseline_production",
        "baseline_yield"
    ]

    missing = [
        key for key in required_baseline
        if key not in baseline
    ]

    if missing:
        raise ValueError(f"Missing baseline values: {missing}")

    rows = [{
        "Scenario": "Historical Baseline",
        "Area (1000 ha)": baseline["baseline_area"],
        "Production (1000 tonnes)": baseline["baseline_production"],
        "Yield (kg/ha)": baseline["baseline_yield"],
        "Production Change (%)": 0.0
    }]

    required_scenario = [
        "simulated_area",
        "simulated_production",
        "simulated_yield",
        "production_change_pct"
    ]

    for name, result in scenarios.items():

        if not isinstance(result, dict):
            raise ValueError(f"Invalid scenario: {name}")

        missing = [
            key for key in required_scenario
            if key not in result
        ]

        if missing:
            raise ValueError(
                f"Missing values in scenario {name}: {missing}"
            )

        rows.append({
            "Scenario": str(name),
            "Area (1000 ha)": result["simulated_area"],
            "Production (1000 tonnes)": result["simulated_production"],
            "Yield (kg/ha)": result["simulated_yield"],
            "Production Change (%)": result["production_change_pct"]
        })

    return pd.DataFrame(rows)


# ============================================================
# 7. SCENARIO SUMMARY
# ============================================================

def get_scenario_summary(result):

    change = result["production_change_pct"]

    if change is None:
        interpretation = (
            "Percentage change unavailable because baseline production is zero."
        )

    elif change > 0:
        interpretation = f"Production increases by {change:.2f}%."

    elif change < 0:
        interpretation = f"Production decreases by {abs(change):.2f}%."

    else:
        interpretation = "Production remains unchanged."

    return {
        "interpretation": interpretation,
        "production_difference": result["production_difference"],
        "production_change_pct": change
    }
