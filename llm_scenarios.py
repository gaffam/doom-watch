"""LLM-based scenario generation utilities."""

import openai


def generate_scenario(prompt: str) -> str:
    """Return LLM-generated scenario text."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            timeout=10,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception:
        return ""

