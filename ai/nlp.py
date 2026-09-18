"""
ai/nlp.py
---------
A small, dependency-light NLP module used to:
    1. Clean and tokenize raw user text.
    2. Extract simple keywords.
    3. Classify the query into a business "intent" category.

Design choice for an academic project: instead of a heavyweight NLP
library, we use straightforward Python string processing for cleaning/
tokenization, and a transparent keyword-scoring rule-based classifier
for intent detection. This is intentionally easy to explain in a viva:
"we score the query against a dictionary of category keywords and pick
the category with the highest score".
"""

import re

# --- Intent categories and their trigger keywords ---
INTENT_KEYWORDS = {
    "BUSINESS_IDEA": [
        "idea", "start", "which business", "what business", "suggest a business",
        "new business", "startup idea", "business to start"
    ],
    "MARKETING": [
        "marketing", "advertise", "advertising", "promotion", "promote",
        "social media", "branding", "customers reach", "campaign"
    ],
    "FINANCE": [
        "budget", "investment", "funding", "loan", "capital", "finance",
        "financial", "cost", "pricing", "price", "profit", "revenue", "roi"
    ],
    "CUSTOMER_ANALYSIS": [
        "target customer", "customers", "customer segment", "audience",
        "who should", "buyer persona"
    ],
    "COMPETITION": [
        "competitor", "competition", "rival", "market share"
    ],
    "RISK_ANALYSIS": [
        "risk", "analyze the risk", "risky", "danger", "failure", "chances of failing"
    ],
    "BUSINESS_PLAN": [
        "business plan", "plan for", "roadmap", "strategy document"
    ],
    "SALES": [
        "sales", "increase sales", "sell more", "conversion"
    ],
}

STOPWORDS = {
    "a", "an", "the", "is", "are", "am", "i", "you", "we", "my", "our",
    "to", "for", "of", "in", "on", "and", "or", "with", "should", "how",
    "can", "what", "which", "do", "does", "it", "this", "that", "be"
}


def clean_text(text: str) -> str:
    """Lowercase, strip punctuation (keep currency symbols/numbers)."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9₹%\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize(text: str) -> list:
    """Split cleaned text into tokens, removing stopwords."""
    cleaned = clean_text(text)
    tokens = cleaned.split()
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


def extract_keywords(text: str, top_n: int = 8) -> list:
    """Return the most relevant (non-stopword) tokens from the query."""
    tokens = tokenize(text)
    # simple frequency-based ranking (fine for short queries)
    seen = []
    for t in tokens:
        if t not in seen:
            seen.append(t)
    return seen[:top_n]


def classify_intent(text: str) -> str:
    """
    Rule-based intent classifier.
    Scores the raw (lowercased) query against each category's keyword list
    and returns the category with the highest number of keyword hits.
    Falls back to "GENERAL_ADVICE" if nothing matches.
    """
    lowered = " " + clean_text(text) + " "
    scores = {}
    for category, keywords in INTENT_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw in lowered:
                score += 1
        if score > 0:
            scores[category] = score

    if not scores:
        return "GENERAL_ADVICE"

    # return the category with the highest score (ties -> first found)
    best_category = max(scores, key=scores.get)
    return best_category


def analyze_query(text: str) -> dict:
    """Convenience wrapper used by the chatbot route."""
    return {
        "original": text,
        "cleaned": clean_text(text),
        "tokens": tokenize(text),
        "keywords": extract_keywords(text),
        "intent": classify_intent(text),
    }


INTENT_LABELS = {
    "BUSINESS_IDEA": "Business Idea",
    "MARKETING": "Marketing",
    "FINANCE": "Finance",
    "CUSTOMER_ANALYSIS": "Customer Analysis",
    "COMPETITION": "Competition",
    "RISK_ANALYSIS": "Risk Analysis",
    "BUSINESS_PLAN": "Business Plan",
    "SALES": "Sales",
    "GENERAL_ADVICE": "General Business Advice",
}
