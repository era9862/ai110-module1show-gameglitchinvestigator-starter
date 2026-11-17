# Model Card: AI Hint Coach

## What it is
A one-sentence hint generator (Claude, `claude-haiku-5-5`) inside a number-guessing game, protected by a validator and a rule-based fallback.

## Limitations and biases
- The validator only checks for a leaked secret and for direction words. It can't judge tone, accuracy of anything else the model says, or hints that leak the secret indirectly ("it's the square of 7").
- Direction detection is English-only keyword matching, so a valid hint in another language would be rejected and fall back.
- Hints are only as good as the prompt; I tested the guardrail with scripted replies, not a large sample of live model output.
- Playful tone is a design choice and may not suit every player. There is no demographic data, so bias risk is low, but the model's style isn't audited.

## Misuse potential
The risk is small: the game has no personal data. Possible issues are a player trying to extract the secret (the validator blocks replies that contain it, and the prompt never sends the secret to the model at all), and API-cost abuse if deployed publicly. Mitigations: the secret is never in the prompt, `max_tokens=80`, and a retry cap of 2. A public deployment would also need rate limiting and a key kept in server-side environment variables.

## What surprised me in testing
A naive substring check for the secret would flag "500" as a leak of 50. Edge cases in a guardrail matter as much as the main path. I was also surprised that the most valuable design choice was not the AI call but the fallback: it made every test deterministic and the game work without a key.

## Collaboration with AI
I used Claude Code to build this feature.

- **Accepted:** The suggestion to keep `check_guess` as the source of truth and have the AI only phrase the hint, with a validate-then-retry-then-fallback loop. I verified it by writing tests where the fake model leaks the secret or points the wrong way, and confirmed the player still sees a correct hint.
- **Changed / scoped down:** The validator uses string and regex checks instead of a second model call to judge each hint. A second call would add cost, latency, and another thing that can be wrong, while the simple checks are fully unit-testable. I also made the leak check match the secret only as a standalone number, so "500" doesn't count as leaking 50.

## Evaluation
11/11 pytest tests pass (see README for the table). Live-model quality has not been measured; a next step would be logging accept/reject rates from `game.log` over real play sessions.
