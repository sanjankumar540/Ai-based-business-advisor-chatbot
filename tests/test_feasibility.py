"""tests/test_feasibility.py - Feasibility Engine + Health Score sanity checks."""

from ml.feasibility import compute_feasibility, compute_health_score


def test_feasibility_basic_math():
    result = compute_feasibility(
        startup_cost=100000, monthly_rent=5000, raw_material_cost_per_month=10000,
        marketing_budget_per_month=2000, other_monthly_expenses=1000,
        num_employees=1, avg_employee_cost=8000,
        expected_price_per_order=100, expected_daily_customers=20,
    )
    assert result["daily_revenue"] == 2000
    assert result["monthly_revenue"] == 60000
    assert result["monthly_cost"] == 5000 + 10000 + 2000 + 1000 + 8000
    assert result["net_profit"] == result["monthly_revenue"] - result["monthly_cost"]


def test_feasibility_handles_zero_startup_cost():
    result = compute_feasibility(
        startup_cost=0, monthly_rent=0, raw_material_cost_per_month=0,
        marketing_budget_per_month=0, other_monthly_expenses=0,
        num_employees=0, avg_employee_cost=0,
        expected_price_per_order=50, expected_daily_customers=10,
    )
    assert result["roi_pct"] == 0.0  # avoids division by zero


def test_feasibility_never_breaks_even_when_unprofitable():
    result = compute_feasibility(
        startup_cost=500000, monthly_rent=50000, raw_material_cost_per_month=50000,
        marketing_budget_per_month=20000, other_monthly_expenses=10000,
        num_employees=5, avg_employee_cost=20000,
        expected_price_per_order=10, expected_daily_customers=5,
    )
    assert result["net_profit"] < 0
    assert result["breakeven_months"] is None


def test_health_score_within_bounds():
    feasibility = compute_feasibility(
        startup_cost=200000, monthly_rent=10000, raw_material_cost_per_month=15000,
        marketing_budget_per_month=5000, other_monthly_expenses=2000,
        num_employees=2, avg_employee_cost=10000,
        expected_price_per_order=200, expected_daily_customers=30,
    )
    health = compute_health_score(feasibility, "Medium Risk", "Medium", "High")
    for key in ["financial_score", "risk_score", "competition_score", "market_score", "growth_score", "overall_score"]:
        assert 0 <= health[key] <= 100
