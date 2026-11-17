from ai_coach import get_coach_hint, validate_hint


class FakeClient:
    """Stands in for anthropic.Anthropic, returning scripted replies."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = 0
        self.messages = self

    def create(self, **kwargs):
        self.calls += 1
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        block = type("B", (), {"text": reply})()
        return type("R", (), {"content": [block]})()


def hint(client, guess=60, secret=50):
    return get_coach_hint(guess, secret, 1, 100, [], client=client)


def test_good_ai_hint_is_used():
    text, src = hint(FakeClient(["Nice try, go lower!"]))
    assert src == "ai" and text == "Nice try, go lower!"


def test_leaking_secret_is_rejected_then_retried():
    c = FakeClient(["Go lower, it's 50!", "Go lower, friend."])
    text, src = hint(c)
    assert src == "ai" and "50" not in text and c.calls == 2


def test_wrong_direction_falls_back_to_rule_based():
    c = FakeClient(["Go higher!", "Try higher!"])
    text, src = hint(c)
    assert src == "fallback" and "LOWER" in text


def test_api_error_falls_back():
    c = FakeClient([RuntimeError("boom"), RuntimeError("boom")])
    text, src = hint(c)
    assert src == "fallback" and "LOWER" in text


def test_secret_substring_of_other_number_is_not_a_leak():
    ok, _ = validate_hint("Go lower than 500 maybe", "Too High", 50)
    assert ok


def test_empty_and_long_replies_rejected():
    assert not validate_hint("", "Too High", 50)[0]
    assert not validate_hint("lower " * 50, "Too High", 50)[0]
