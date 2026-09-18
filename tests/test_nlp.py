"""tests/test_nlp.py - NLP intent classification."""

from ai.nlp import classify_intent, clean_text, tokenize, extract_keywords


def test_classify_marketing_intent():
    assert classify_intent("What marketing strategy should I use?") == "MARKETING"


def test_classify_business_idea_intent():
    assert classify_intent("I have 5 lakh rupees, which business can I start?") == "BUSINESS_IDEA"


def test_classify_risk_intent():
    assert classify_intent("Analyze the risks of starting a restaurant") == "RISK_ANALYSIS"


def test_classify_falls_back_to_general():
    assert classify_intent("Tell me something interesting") == "GENERAL_ADVICE"


def test_clean_text_lowercases_and_strips_punctuation():
    result = clean_text("Hello, World!!!")
    assert result == "hello world"


def test_tokenize_removes_stopwords():
    tokens = tokenize("What is the best business for me")
    assert "the" not in tokens
    assert "business" in tokens


def test_extract_keywords_returns_list():
    keywords = extract_keywords("marketing strategy for clothing business")
    assert isinstance(keywords, list)
    assert len(keywords) > 0
