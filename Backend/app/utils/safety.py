import re

_UNSAFE_PATTERNS: list[tuple[re.Pattern, str]] = [
    (
        re.compile(
            r"\byou\s+(have|suffer\s+from|are\s+diagnosed\s+with|are\s+showing\s+signs\s+of)\s+"
            r"(depression|anxiety|bipolar|schizophrenia|ptsd|ocd|adhd|bpd|"
            r"panic\s+disorder|eating\s+disorder|personality\s+disorder|"
            r"clinical\s+\w+|major\s+\w+|generalized\s+\w+)",
            re.IGNORECASE,
        ),
        "It sounds like you're going through a difficult time. I'd encourage you to discuss what you're experiencing with a qualified healthcare professional who can provide a proper assessment.",
    ),
    (
        re.compile(
            r"\b(you\s+should|i\s+recommend|try\s+taking|take|prescribe)\s+"
            r"(medication|pills?|drugs?|antidepressants?|ssri|benzodiazepines?|"
            r"xanax|prozac|zoloft|lexapro|wellbutrin|sertraline|fluoxetine|"
            r"citalopram|escitalopram|venlafaxine|duloxetine|buspirone|"
            r"alprazolam|clonazepam|lorazepam|diazepam)",
            re.IGNORECASE,
        ),
        "I'm not able to recommend specific medications. Please consult with a doctor or psychiatrist who can evaluate your needs and discuss treatment options with you.",
    ),
    (
        re.compile(
            r"\bi\s+(diagnose|am\s+diagnosing)\s+you\b",
            re.IGNORECASE,
        ),
        "I'm not qualified to make diagnoses. A licensed mental health professional can provide a proper evaluation.",
    ),
]


def sanitize_response(text: str) -> str:
    for pattern, replacement in _UNSAFE_PATTERNS:
        if pattern.search(text):
            text = pattern.sub(replacement, text)
    return text
