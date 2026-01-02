from src.utils import normalize_text


def test_normalize_text_strips():
    assert normalize_text("  hi  ") == "hi"
