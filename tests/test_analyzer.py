"""tests/test_analyzer.py - Business Analyzer, Idea Generator, Competitor Analysis routes."""


def test_business_analyzer_requires_login(client):
    response = client.get("/business-analyzer", follow_redirects=True)
    assert b"Login" in response.data or b"log in" in response.data.lower()


def test_business_analyzer_full_flow(registered_user):
    response = registered_user.post("/business-analyzer", data={
        "business_name": "Test Cafe", "business_type": "Food & Beverage",
        "location": "Bengaluru", "startup_cost": "300000",
        "target_customers": "College students", "expected_price_per_order": "150",
        "expected_daily_customers": "40", "num_employees": "2",
        "avg_employee_cost": "12000", "monthly_rent": "15000",
        "raw_material_cost_per_month": "20000", "marketing_budget_per_month": "10000",
        "other_monthly_expenses": "5000", "business_experience": "Low",
        "market_demand": "High", "competition": "High",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Business Health Score" in response.data
    assert b"Financial Feasibility" in response.data
    assert b"ML Risk Prediction" in response.data


def test_my_businesses_lists_saved_profile(registered_user):
    registered_user.post("/business-analyzer", data={
        "business_name": "Test Store", "business_type": "Retail",
        "startup_cost": "200000", "expected_price_per_order": "100",
        "expected_daily_customers": "20",
    }, follow_redirects=True)
    response = registered_user.get("/my-businesses")
    assert b"Test Store" in response.data


def test_idea_generator_returns_results(registered_user):
    response = registered_user.post("/idea-generator", data={
        "budget": "300000", "keywords": "food", "experience": "Medium",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Comparable Business Opportunities" in response.data


def test_competitor_analysis_returns_table(registered_user):
    response = registered_user.post("/competitor-analysis", data={
        "competitor_name": ["Cafe A", "Cafe B"],
        "competitor_price": ["150", "180"],
        "competitor_strength": ["Location", "Brand"],
        "competitor_weakness": ["Price", "Slow service"],
        "your_differentiator": "Faster delivery",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Cafe A" in response.data
    assert b"Faster delivery" in response.data
