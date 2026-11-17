"""AI hint coach with guardrails.

The coach asks Claude for a short, in-character hint after each guess. Because
LLM output is not trustworthy by default, every reply passes a validator
(plan -> act -> check): it must not leak the secret and must point the player
in the correct direction. A failing reply is retried, and if retries run out
(or no API key / network is available) the deterministic hint from
``check_guess`` is used instead, so the game never shows a wrong hint.
"""
import logging
import os
import re

from logic_utils import check_guess

logger = logging.getLogger("glitchy_guesser.coach")

MODEL = "claude-haiku-5-5"
MAX_ATTEMPTS = 2

_DIRECTION_WORDS = {
    "Too High": ("lower", "smaller", "less", "down"),
    "Too Low": ("higher", "larger", "greater", "more", "up"),
}
_OPPOSITE_WORDS = {
    "Too High": ("higher", "larger", "greater"),
    "Too Low": ("lower", "smaller"),
}


def validate_hint(text, outcome, secret):
    """Return (ok, reason). Guardrail applied to every AI-written hint."""
    if not text or not text.strip():
        return False, "empty reply"
    if len(text) > 200:
        return False, "too long"
    if re.search(rf"(?<!\d){secret}(?!\d)", text):
        return False, "leaks the secret number"
    lowered = text.lower()
    if outcome == "Win":
        return True, "ok"
    if any(w in lowered for w in _OPPOSITE_WORDS[outcome]):
        return False, "points the wrong direction"
    if not any(w in lowered for w in _DIRECTION_WORDS[outcome]):
        return False, "gives no direction"
    return True, "ok"


def _build_client():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic
        return anthropic.Anthropic()
    except Exception as exc:  # missing package, bad config, etc.
        logger.warning("Could not create Anthropic client: %s", exc)
        return None


def _ask_model(client, guess, outcome, low, high, history):
    prompt = (
        "You are a playful coach for a number guessing game. The player "
        f"guessed {guess} in the range {low}-{high}; the result was "
        f"'{outcome}'. Previous guesses: {history}. Reply with ONE short "
        "sentence (under 25 words) telling them whether to go higher or "
        "lower. Never reveal the secret number."
    )
    resp = client.messages.create(
        model=MODEL,
        max_tokens=80,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


def get_coach_hint(guess, secret, low, high, history, client=None):
    """Return (hint_text, source) where source is 'ai' or 'fallback'."""
    outcome, base_message = check_guess(guess, secret)
    if outcome == "Win":
        return base_message, "fallback"

    client = client or _build_client()
    if client is None:
        logger.info("No AI client available; using rule-based hint")
        return base_message, "fallback"

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            text = _ask_model(client, guess, outcome, low, high, history)
        except Exception as exc:
            logger.error("AI call failed (attempt %d): %s", attempt, exc)
            continue
        ok, reason = validate_hint(text, outcome, secret)
        if ok:
            logger.info("AI hint accepted (attempt %d)", attempt)
            return text, "ai"
        logger.warning("AI hint rejected (attempt %d): %s", attempt, reason)

    logger.warning("Falling back to rule-based hint")
    return base_message, "fallback"
