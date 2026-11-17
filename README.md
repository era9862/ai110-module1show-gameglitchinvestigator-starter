# Glitchy Guesser with an AI Hint Coach

## Original project

This builds on **Game Glitch Investigator: The Impossible Guesser** (Modules 1-3). The original was an AI-generated Streamlit number-guessing game that shipped with bugs: hints that pointed the wrong way, a "New Game" button that didn't reset state, and attempt counters that went negative on invalid input. The goal was to find and fix those bugs, move the logic into `logic_utils.py`, and cover it with pytest.

## Summary

The fixed game now has an **AI hint coach**: after each guess, Claude writes a short, playful hint. LLMs can be wrong or leak answers, so the coach is wrapped in a guardrail loop. Every AI reply is checked (does it reveal the secret? does it point the right way?), retried if it fails, and replaced by the deterministic hint if it still fails. The game therefore never gives a lying hint, with or without an API key. That reliability is the point: the original project was about AI-written code that lies, and this one makes AI output verifiable.

## Architecture overview

Source: [diagrams/architecture.mmd](diagrams/architecture.mmd) (Mermaid).

- **app.py** is the Streamlit UI and holds game state in `st.session_state`.
- **logic_utils.py** holds the pure game logic. `check_guess` is the ground truth for whether a guess is high, low, or correct.
- **ai_coach.py** is the agentic part. It plans (build a prompt from the outcome), acts (calls Claude), and checks its own work (`validate_hint`), retrying up to twice, then falling back to the rule-based hint. All outcomes are logged to `game.log`.
- **Testing and humans:** `pytest` checks the logic and the guardrail with a fake client. A person reviews `game.log` and the on-screen "Hint source" label to see when the AI was used or rejected.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here   # optional; without it the game uses rule-based hints
python -m streamlit run app.py
pytest                                   # run the tests
```

## Sample interactions

Secret = 50, Normal difficulty (1-100). The first two rows come from the guardrail unit tests (scripted fake model replies); the third is the no-API-key path, which I ran locally. I have not recorded live Claude outputs yet.

| Guess | Model reply | Guardrail result | Player sees |
|---|---|---|---|
| 60 | "Nice try, go lower!" | Pass | "Nice try, go lower!" (source: AI coach) |
| 60 | "Go lower, it's 50!" then "Go lower, friend." | First rejected (leaks secret), retry passes | "Go lower, friend." (source: AI coach) |
| 60 | "Go higher!" twice | Both rejected (wrong direction) | "📉 Go LOWER!" (source: rule-based) |
| 40 | no API key | Skipped | "📈 Go HIGHER!" (source: rule-based) |

## Design decisions

- **Deterministic ground truth, AI as wrapper.** `check_guess` decides the outcome; the AI only phrases it. Trade-off: less creative freedom, but a hint can never be wrong.
- **Validator uses simple string checks** (secret as a standalone number, direction words) instead of a second LLM call. Cheap and testable, but it can miss subtle issues like a misleading tone.
- **Graceful fallback over failing.** No key, no network, or a bad reply all degrade to the original behavior.
- **Small fast model** (`claude-haiku-5-5`) because the task is one sentence per guess.
- **Dependency injection** (`client=`) so tests never hit the network.

## Testing summary

`pytest`: **11 of 11 tests passed** (5 original logic tests, 6 coach tests).

| Test input | Evaluation criteria | Result |
|---|---|---|
| AI says "go lower" for a too-high guess | Accepted, source = ai | Pass |
| AI reply contains the secret | Rejected and retried | Pass |
| AI says "go higher" for a too-high guess, twice | Falls back to rule-based hint | Pass |
| API raises an exception, twice | Falls back, no crash | Pass |
| Reply mentions 500 when secret is 50 | Not treated as a leak | Pass |
| Empty or over-long reply | Rejected | Pass |

What I learned: a plain substring check for the secret would wrongly reject "500" for secret 50, so the validator uses digit boundaries and that edge case has a test. Not tested: real Claude responses and the Streamlit UI itself.

## Reflection

Fixing the original bugs showed that AI-generated code can look right and be wrong. Adding AI to the product meant treating its output the same way: assume it can be wrong, verify it against something deterministic, and decide ahead of time what happens when it is. See [model_card.md](model_card.md) for the responsible-AI reflection and [reflection.md](reflection.md) for the original debugging write-up.
