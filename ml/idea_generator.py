"""
ml/idea_generator.py
---------------------
Business Idea Generator.

Given a budget (and optional category keywords), returns a short list of
concrete business ideas as a STRUCTURED, COMPARABLE table — not free-form
text — with each idea's typical investment, and a genuine ML-predicted risk
level (reusing the same trained Random Forest model from ml/predict.py, not
a fake/static label).

This is intentionally curated + rule-filtered rather than LLM-generated, so
every idea shown is guaranteed to be sensible and the risk score is always
real, deterministic model output.
"""

from ml.predict import predict_risk, ModelNotTrainedError

# Curated idea catalog: typical investment, operating cost, and market
# assumptions used to query the real risk model for each candidate idea.
IDEA_CATALOG = [
    {"name": "Tutoring / Coaching Service", "keywords": ["education", "tutor", "teach", "student"],
     "investment": 25000, "operating_cost": 3000, "business_type": "Education",
     "market_demand": "High", "competition": "Medium"},
    {"name": "Home-Based Tiffin / Meal Delivery", "keywords": ["food", "tiffin", "meal", "restaurant", "cooking"],
     "investment": 75000, "operating_cost": 15000, "business_type": "Food & Beverage",
     "market_demand": "High", "competition": "High"},
    {"name": "Cloud Kitchen", "keywords": ["food", "restaurant", "delivery", "kitchen"],
     "investment": 400000, "operating_cost": 60000, "business_type": "Food & Beverage",
     "market_demand": "High", "competition": "High"},
    {"name": "Curated Clothing / Fashion Store (Online)", "keywords": ["clothing", "fashion", "apparel", "boutique"],
     "investment": 150000, "operating_cost": 20000, "business_type": "Fashion & Clothing",
     "market_demand": "Medium", "competition": "High"},
    {"name": "Retail Convenience Store", "keywords": ["retail", "shop", "store", "grocery"],
     "investment": 500000, "operating_cost": 45000, "business_type": "Retail",
     "market_demand": "Medium", "competition": "High"},
    {"name": "E-commerce / Reselling Store", "keywords": ["ecommerce", "online", "reselling", "dropship"],
     "investment": 100000, "operating_cost": 12000, "business_type": "E-commerce",
     "market_demand": "Medium", "competition": "Medium"},
    {"name": "Digital Marketing / Social Media Agency", "keywords": ["marketing", "digital", "social media", "agency"],
     "investment": 50000, "operating_cost": 8000, "business_type": "Services",
     "market_demand": "High", "competition": "Medium"},
    {"name": "Home Cleaning / Repair Services", "keywords": ["cleaning", "repair", "service", "home"],
     "investment": 60000, "operating_cost": 10000, "business_type": "Services",
     "market_demand": "Medium", "competition": "Medium"},
    {"name": "Mobile App / Website Development Studio", "keywords": ["technology", "app", "software", "website", "tech"],
     "investment": 150000, "operating_cost": 25000, "business_type": "Technology",
     "market_demand": "High", "competition": "Medium"},
    {"name": "Handmade / Eco-Friendly Products", "keywords": ["handmade", "eco", "craft", "sustainable"],
     "investment": 40000, "operating_cost": 6000, "business_type": "Manufacturing",
     "market_demand": "Medium", "competition": "Low"},
    {"name": "Cafe / Juice Bar", "keywords": ["cafe", "coffee", "juice", "bar", "food"],
     "investment": 300000, "operating_cost": 40000, "business_type": "Food & Beverage",
     "market_demand": "Medium", "competition": "High"},
    {"name": "Fitness / Yoga Studio", "keywords": ["fitness", "gym", "yoga", "wellness"],
     "investment": 350000, "operating_cost": 35000, "business_type": "Services",
     "market_demand": "Medium", "competition": "Medium"},
]


def generate_ideas(budget: float, keywords: list = None, experience: str = "Medium", top_n: int = 4) -> list:
    """
    Filters IDEA_CATALOG to ideas that fit within the given budget (typical
    investment <= budget * 1.15, i.e. small headroom allowed), optionally
    biased toward the given keywords, and scores each with the real trained
    Random Forest risk model. Returns a structured, comparable list.

    Returns:
        [{"name": ..., "investment": ..., "predicted_risk": ..., "potential": ...}, ...]
        sorted by a simple "best fit" heuristic (lower risk + higher demand first).
    """
    keywords = [k.lower() for k in (keywords or [])]

    candidates = [idea for idea in IDEA_CATALOG if idea["investment"] <= budget * 1.15]
    if not candidates:
        # budget too small for anything in the catalog -> show the cheapest options anyway
        candidates = sorted(IDEA_CATALOG, key=lambda i: i["investment"])[:top_n]

    def keyword_score(idea):
        if not keywords:
            return 0
        return sum(1 for kw in keywords if any(kw in ik for ik in idea["keywords"]))

    candidates = sorted(candidates, key=keyword_score, reverse=True)

    results = []
    for idea in candidates[: max(top_n, 6)]:
        target_market = "Small" if budget < 200000 else ("Medium" if budget < 750000 else "Large")
        try:
            prediction = predict_risk(
                business_type=idea["business_type"], investment=idea["investment"],
                market_demand=idea["market_demand"], competition=idea["competition"],
                experience=experience, operating_cost=idea["operating_cost"],
                target_market=target_market,
            )
            risk = prediction["predicted_risk"]
        except ModelNotTrainedError:
            risk = "Unknown (model not trained)"

        potential = idea["market_demand"]  # High/Medium/Low demand doubles as "potential" label

        results.append({
            "name": idea["name"],
            "investment": idea["investment"],
            "predicted_risk": risk,
            "potential": potential,
            "business_type": idea["business_type"],
        })

    risk_rank = {"Low Risk": 0, "Medium Risk": 1, "High Risk": 2}
    potential_rank = {"High": 0, "Medium": 1, "Low": 2}
    results.sort(key=lambda r: (risk_rank.get(r["predicted_risk"], 3), potential_rank.get(r["potential"], 3)))

    return results[:top_n]
