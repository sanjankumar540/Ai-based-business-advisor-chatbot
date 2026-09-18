"""
ml/feasibility.py
------------------
Business Feasibility Engine.

Pure, deterministic financial calculations (no AI/LLM involved) — this is
what makes the project a genuine "decision support system" rather than a
chatbot: every number here is calculated directly from the founder's own
inputs, and the same inputs always give the same numbers.

All monetary values are assumed to be in the same currency the user enters
(the UI labels them in ₹, but the math is currency-agnostic).
"""


def compute_feasibility(
    startup_cost: float,
    monthly_rent: float,
    raw_material_cost_per_month: float,
    marketing_budget_per_month: float,
    other_monthly_expenses: float,
    num_employees: int,
    avg_employee_cost: float,
    expected_price_per_order: float,
    expected_daily_customers: float,
) -> dict:
    """
    Computes core feasibility metrics from structured business inputs.

    Returns a dict with:
        monthly_revenue, monthly_cost, gross_profit, net_profit,
        profit_margin_pct, roi_pct (annualized), breakeven_months,
        payback_months, daily_revenue, employee_cost_monthly
    """
    daily_revenue = expected_price_per_order * expected_daily_customers
    monthly_revenue = daily_revenue * 30

    employee_cost_monthly = num_employees * avg_employee_cost
    monthly_cost = (
        monthly_rent + raw_material_cost_per_month + marketing_budget_per_month
        + other_monthly_expenses + employee_cost_monthly
    )

    net_profit = monthly_revenue - monthly_cost
    profit_margin_pct = (net_profit / monthly_revenue * 100) if monthly_revenue > 0 else 0.0

    # Annualized ROI on the startup investment
    annual_profit = net_profit * 12
    roi_pct = (annual_profit / startup_cost * 100) if startup_cost > 0 else 0.0

    # Break-even: how many months of net profit are needed to recover startup cost
    if net_profit > 0:
        breakeven_months = round(startup_cost / net_profit, 1)
        payback_months = breakeven_months  # same concept for this simplified model
    else:
        breakeven_months = None  # never breaks even at current assumptions
        payback_months = None

    return {
        "daily_revenue": round(daily_revenue, 2),
        "monthly_revenue": round(monthly_revenue, 2),
        "monthly_cost": round(monthly_cost, 2),
        "employee_cost_monthly": round(employee_cost_monthly, 2),
        "net_profit": round(net_profit, 2),
        "profit_margin_pct": round(profit_margin_pct, 2),
        "roi_pct": round(roi_pct, 2),
        "breakeven_months": breakeven_months,
        "payback_months": payback_months,
    }


def compute_health_score(feasibility: dict, risk_level: str, competition: str, market_demand: str) -> dict:
    """
    Combines the feasibility numbers + ML risk prediction + qualitative
    inputs into a transparent 0-100 "Business Health Score" made up of
    five sub-scores. Every sub-score's formula is explicit and documented
    here (no black box) so it can be explained in a viva.
    """
    # --- Financial Score (0-100): based on profit margin and ROI ---
    margin = feasibility["profit_margin_pct"]
    roi = feasibility["roi_pct"]
    financial_score = max(0, min(100, (margin * 1.2) + (roi * 0.3)))

    # --- Risk Score (0-100, higher = safer): inverse of ML risk level ---
    risk_score_map = {"Low Risk": 85, "Medium Risk": 55, "High Risk": 25}
    risk_score = risk_score_map.get(risk_level, 50)

    # --- Competition Score (0-100, higher = less competitive pressure) ---
    competition_score_map = {"Low": 85, "Medium": 55, "High": 30}
    competition_score = competition_score_map.get(competition, 50)

    # --- Market Score (0-100): based on stated market demand ---
    market_score_map = {"Low": 30, "Medium": 60, "High": 90}
    market_score = market_score_map.get(market_demand, 50)

    # --- Growth Score (0-100): based on break-even speed ---
    breakeven = feasibility["breakeven_months"]
    if breakeven is None:
        growth_score = 15  # never breaks even under current assumptions
    elif breakeven <= 6:
        growth_score = 90
    elif breakeven <= 12:
        growth_score = 70
    elif breakeven <= 24:
        growth_score = 45
    else:
        growth_score = 20

    overall_score = round(
        (financial_score * 0.30) + (risk_score * 0.25) + (competition_score * 0.15)
        + (market_score * 0.15) + (growth_score * 0.15)
    )
    overall_score = max(0, min(100, overall_score))

    return {
        "financial_score": round(financial_score),
        "risk_score": round(risk_score),
        "competition_score": round(competition_score),
        "market_score": round(market_score),
        "growth_score": round(growth_score),
        "overall_score": overall_score,
    }
