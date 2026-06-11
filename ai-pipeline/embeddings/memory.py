import re

MEMORY_PATTERNS = [
    "who am i",
    "what is my name",
    "do you remember me",
    "what did i tell you",
    "who be me",
    "what did I ask you before",
    "what is your name"
]


def is_memory_question(question: str) -> bool:

    q = question.lower().strip()

    return any(
        phrase in q
        for phrase in MEMORY_PATTERNS
    )


def extract_name(history):

    for msg in reversed(history):

        text = msg["content"]

        patterns = [
            r"my name is (.+)",
            r"i am (.+)",
            r"i'm (.+)",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:
                return match.group(1).strip()

    return None