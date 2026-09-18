"""
ai/llm.py
---------
Thin wrapper around an external LLM API (OpenAI-compatible schema, which
also works with many hosted Mistral/LLaMA endpoints).

Key design goal: NEVER crash the application because the LLM is
unavailable. If Config.DEMO_MODE is True, or if the live API call fails
for any reason (missing key, network error, bad response), we fall back
to the structured Demo Mode template response.
"""

import requests
from config import Config
from ai.prompts import SYSTEM_PROMPT, build_chat_prompt, demo_chat_response


class LLMError(Exception):
    """Raised internally when the live LLM call fails; always caught."""
    pass


def _call_openai_compatible_api(prompt: str) -> str:
    """
    Calls an OpenAI-compatible /chat/completions endpoint.
    Works with OpenAI itself, and with many providers (incl. some
    Mistral/LLaMA hosting services) that mirror the same request schema.
    """
    url = f"{Config.LLM_API_BASE.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {Config.LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": Config.LLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.4,
        "max_tokens": 800,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        raise LLMError(f"LLM API call failed: {exc}")


def generate_business_response(user_query: str, intent: str, context: str) -> dict:
    """
    Main entry point used by routes/chatbot.py.

    Returns:
        {
            "response": str,      # the final text to show the user
            "mode": "live" | "demo",
        }
    """
    if Config.DEMO_MODE:
        return {
            "response": demo_chat_response(user_query, intent, context),
            "mode": "demo",
        }

    prompt = build_chat_prompt(user_query, intent, context)
    try:
        text = _call_openai_compatible_api(prompt)
        return {"response": text, "mode": "live"}
    except LLMError:
        # Fail gracefully -> demo fallback, app never crashes
        return {
            "response": demo_chat_response(user_query, intent, context),
            "mode": "demo-fallback",
        }


def generate_raw_completion(prompt: str) -> dict:
    """
    Generic helper for other features (business plan / market analysis) that
    want free-form LLM text. Falls back to None on failure/demo mode so the
    caller can use its own template fallback.
    """
    if Config.DEMO_MODE:
        return {"response": None, "mode": "demo"}
    try:
        text = _call_openai_compatible_api(prompt)
        return {"response": text, "mode": "live"}
    except LLMError:
        return {"response": None, "mode": "demo-fallback"}
