"""tests/test_chatbot.py - chatbot route + business plan generation."""


def test_chat_requires_login(client):
    response = client.get("/chat", follow_redirects=True)
    assert b"Login" in response.data or b"log in" in response.data.lower()


def test_send_message_creates_conversation(registered_user):
    response = registered_user.post("/chat", data={
        "message": "Suggest a business idea for a college student",
        "conv_id": "",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Business Overview" in response.data or b"DEMO MODE" in response.data


def test_empty_message_is_rejected(registered_user):
    response = registered_user.post("/chat", data={
        "message": "",
        "conv_id": "",
    }, follow_redirects=True)
    assert b"Please type a question" in response.data


def test_business_plan_generation(registered_user):
    response = registered_user.post("/business-plan", data={
        "business_name": "Test Clothing Co",
        "business_type": "Fashion & Clothing",
        "location": "Bengaluru",
        "budget": "300000",
        "target_customers": "Young professionals",
        "product": "Ethnic wear",
        "goals": "Grow to 2 stores in 2 years",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Executive Summary" in response.data


def test_market_analysis_generation(registered_user):
    response = registered_user.post("/market-analysis", data={
        "business_type": "Cafe",
        "location": "Bengaluru",
        "target_customers": "College students",
        "budget": "200000",
        "product": "Coffee and snacks",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Target Market" in response.data
