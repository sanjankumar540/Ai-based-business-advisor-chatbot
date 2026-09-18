"""
ai/prompts.py
-------------
Prompt templates for the LLM, and structured DEMO MODE fallback content.

Demo Mode is used automatically whenever no live LLM API key is configured
(see config.Config.DEMO_MODE), so the app is always fully demonstrable.
"""

SYSTEM_PROMPT = """You are an AI Business Assistant helping entrepreneurs and
startup founders. You must answer using the retrieved knowledge-base context
where relevant, plus your own general business knowledge. If the context
includes the user's saved business profile numbers, prefer referencing those
specific figures over generic advice. Always structure your answer with
clear sections. Never guarantee financial outcomes. Keep answers practical,
concise, and actionable.

IMPORTANT FORMATTING RULE: Do NOT use Markdown syntax. Do not use asterisks
for bold (**text**), do not use pipe-character tables (| col | col |), do
not use # headers. Write plain text only. For section titles, write the
title in capital letters on its own line followed by a colon, like:
BUSINESS OVERVIEW:
Then write the paragraph content below it in plain sentences. Use simple
numbered lists (1. 2. 3.) with plain text, not Markdown bullets."""


def build_chat_prompt(user_query: str, intent: str, context: str) -> str:
    """Builds the final prompt sent to the LLM, combining RAG context + query."""
    context_block = context if context else "(No closely matching knowledge-base article was found; answer using general business knowledge.)"
    prompt = f"""
Detected query category: {intent}

Relevant knowledge base context:
---
{context_block}
---

User question: "{user_query}"

Respond with clearly labeled sections such as:
- Business Overview
- Target Customers
- Estimated Budget (if relevant)
- Marketing Strategy (if relevant)
- Required Resources
- Competition
- Risks
- Revenue Opportunities
- Recommended Next Steps

Only include sections that are relevant to the question. Keep it concise and structured.
"""
    return prompt.strip()


# ---------------------------------------------------------------------------
# DEMO MODE structured fallback response.
# This is used when Config.DEMO_MODE is True (no LLM API key configured), or
# if a live LLM call fails for any reason (network error, invalid key, etc.)
# ---------------------------------------------------------------------------

def demo_chat_response(user_query: str, intent: str, context: str) -> str:
    intent_label = intent.replace("_", " ").title()

    template = f"""[DEMO MODE RESPONSE — no live LLM API key configured]

DETECTED CATEGORY: {intent_label}

BUSINESS OVERVIEW:
Based on your question — "{user_query.strip()}" — here is general guidance. This is a
template-based demo answer; connect a real LLM API key in .env for fully
generated, query-specific responses.

TARGET CUSTOMERS:
Identify a narrow initial customer segment (age group, income level, location)
rather than trying to serve everyone at once. Validate demand with that group first.

ESTIMATED BUDGET:
Start with a lean budget covering only essential setup costs (inventory/equipment,
basic marketing, a simple online presence). Avoid large fixed costs until demand
is proven.

MARKETING STRATEGY:
Use low-cost digital channels first — social media, local community groups, and
word of mouth — before investing in paid advertising.

REQUIRED RESOURCES:
A small founding team, a minimum viable product/service, basic accounting, and a
simple way to accept payments and track orders.

COMPETITION:
Study 3-5 direct competitors: their pricing, customer reviews, and what they are
missing. Differentiate on service quality, niche focus, or price.

RISKS:
Common risks include underestimating operating costs, misjudging demand, and cash
flow gaps in the first 6-12 months. Keep a financial buffer.

REVENUE OPPORTUNITIES:
Look for upsell/cross-sell options, repeat-purchase incentives, and, once stable,
a second sales channel (e.g., online alongside offline).

RECOMMENDED NEXT STEPS:
1. Validate the idea with 10-20 potential customers.
2. Build a minimum viable version of the product/service.
3. Launch a small pilot before scaling investment.
4. Track key numbers weekly (sales, cost, customer feedback).

For a precise, numbers-based feasibility check instead of general guidance,
use the Business Analyzer tool from the sidebar.
"""
    return template.strip()


def demo_business_plan_template(data: dict) -> str:
    """Fallback business-plan generator used in Demo Mode."""
    name = data.get("business_name", "Your Business")
    btype = data.get("business_type", "General Business")
    location = data.get("location", "Not specified")
    budget = data.get("budget", "Not specified")
    target_customers = data.get("target_customers", "Not specified")
    product = data.get("product", "Not specified")
    goals = data.get("goals", "Not specified")

    return f"""BUSINESS PLAN — {name}
(DEMO MODE — template-based; connect an LLM API key for AI-generated detail)

1. Executive Summary
   {name} is a {btype} business planned for {location}, offering {product}
   to {target_customers}, with an estimated budget of {budget}.

2. Business Description
   The business focuses on {product} within the {btype} sector, aiming to meet
   the stated goal(s): {goals}.

3. Target Market
   Primary target: {target_customers} located in/around {location}.

4. Customer Segments
   Segment demand by price sensitivity (budget vs premium) and usage
   frequency to prioritize marketing spend.

5. Competitor Analysis
   Identify local and online competitors offering similar {product}. Compare
   pricing, quality, and customer service gaps you can exploit.

6. Marketing Strategy
   Combine low-cost digital marketing (social media, local SEO) with
   community/word-of-mouth channels appropriate for {location}.

7. Operations Plan
   Define supplier/vendor relationships, daily operating workflow, and
   staffing needs proportional to the {budget} budget.

8. Financial Overview
   Budget: {budget}. Track fixed costs (rent, salaries) vs variable costs
   (inventory, marketing) monthly. Maintain a 3–6 month expense buffer.

9. Risk Analysis
   Key risks: demand uncertainty, competition, and cash flow gaps. Mitigate
   by starting with a pilot/minimum viable offering.

10. Growth Strategy
    Once the pilot validates demand, reinvest profits into a second location,
    channel, or product line rather than scaling all at once.
"""


def demo_market_analysis_template(data: dict) -> dict:
    """Fallback market-analysis generator used in Demo Mode."""
    return {
        "target_market": f"Customers interested in {data.get('product', 'this product/service')} "
                          f"within {data.get('location', 'the specified location')}.",
        "customer_profile": f"Primary buyers: {data.get('target_customers', 'general consumers')} "
                             f"with budget-conscious to mid-range spending habits.",
        "competition_level": "Medium (estimated) — based on typical saturation for this business type. "
                              "Verify with local market research.",
        "opportunities": [
            "Underserved niche segments within the target customer group",
            "Growing preference for online/local discovery channels",
            "Bundling or subscription-style offers for repeat revenue",
        ],
        "threats": [
            "Established competitors with existing brand loyalty",
            "Rising operating/input costs",
            "Changing customer preferences",
        ],
        "recommended_strategy": "Start with a focused pilot in a narrow customer segment, "
                                 "gather feedback, then expand marketing spend gradually.",
        "note": "These are AI/demo-generated estimates, not verified market statistics."
    }
