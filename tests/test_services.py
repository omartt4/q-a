from app.services import generate_answer


def test_generate_answer_is_deterministic() -> None:
    assert generate_answer("What is Redis?") == generate_answer("What is Redis?")


def test_generate_answer_contains_question() -> None:
    assert "What is Redis?" in generate_answer("What is Redis?")
