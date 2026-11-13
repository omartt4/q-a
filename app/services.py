import hashlib


def generate_answer(question: str) -> str:
    digest = hashlib.sha256(question.strip().encode("utf-8")).hexdigest()[:12]
    return f"Generated answer for: {question.strip()} (reference {digest})"
