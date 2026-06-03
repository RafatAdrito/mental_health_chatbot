import re
from dataclasses import dataclass


@dataclass
class CrisisMatch:
    phrase: str
    category: str
    severity: float


_CRISIS_PATTERNS: list[tuple[str, str, float]] = [
    (r"\b(want|wanna|going)\s+to\s+(die|kill\s+myself|end\s+(it|my\s+life|everything))\b", "suicidal_ideation", 1.0),
    (r"\b(kill|hurt)\s+myself\b", "suicidal_ideation", 1.0),
    (r"\bsuicid(e|al)\b", "suicidal_ideation", 0.95),
    (r"\bend\s+(it\s+all|my\s+life|everything)\b", "suicidal_ideation", 0.95),
    (r"\b(don'?t|do\s+not)\s+want\s+to\s+(live|be\s+alive|exist|be\s+here)\b", "suicidal_ideation", 0.9),
    (r"\bnot\s+worth\s+living\b", "suicidal_ideation", 0.9),
    (r"\bbetter\s+off\s+(dead|without\s+me)\b", "suicidal_ideation", 0.9),
    (r"\bno\s+reason\s+to\s+live\b", "suicidal_ideation", 0.9),
    (r"\bwish\s+i\s+(was|were)\s+dead\b", "suicidal_ideation", 0.95),
    (r"\bplanning\s+(to\s+)?(die|kill|end)\b", "suicidal_ideation", 1.0),

    (r"\bcut(ting)?\s+my(self)?\b", "self_harm", 0.85),
    (r"\bself[- ]?harm\b", "self_harm", 0.85),
    (r"\bhurt(ing)?\s+myself\b", "self_harm", 0.85),
    (r"\bburn(ing)?\s+myself\b", "self_harm", 0.85),

    (r"\b(being|getting)\s+(beat(en)?|abus(ed|ing)|assault(ed)?|rap(ed|ing))\b", "abuse", 0.8),
    (r"\b(domestic|physical|sexual)\s+(violence|abuse)\b", "abuse", 0.8),

    (r"\boverdos(e|ed|ing)\b", "substance_crisis", 0.9),
    (r"\bpoisoned\b", "substance_crisis", 0.85),

    (r"\b(completely|totally|utterly)\s+(hopeless|worthless|alone)\b", "severe_distress", 0.6),
    (r"\bgive\s+up\b", "severe_distress", 0.4),
    (r"\bcan'?t\s+(take|handle|do)\s+(it|this)\s+(anymore|any\s+more)\b", "severe_distress", 0.6),
    (r"\bno\s+(hope|point)\b", "severe_distress", 0.5),
]

_COMPILED_PATTERNS = [(re.compile(p, re.IGNORECASE), cat, sev) for p, cat, sev in _CRISIS_PATTERNS]


def scan_keywords(text: str) -> list[CrisisMatch]:
    matches = []
    for pattern, category, severity in _COMPILED_PATTERNS:
        m = pattern.search(text)
        if m:
            matches.append(CrisisMatch(phrase=m.group(), category=category, severity=severity))
    return matches


def compute_keyword_score(matches: list[CrisisMatch]) -> float:
    if not matches:
        return 0.0
    return max(m.severity for m in matches)


def classify_risk(keyword_score: float, llm_score: float, context_factor: float = 0.0) -> str:
    composite = keyword_score * 0.3 + llm_score * 0.5 + context_factor * 0.2
    if composite >= 0.75:
        return "critical"
    elif composite >= 0.5:
        return "high"
    elif composite >= 0.25:
        return "medium"
    elif composite > 0.0:
        return "low"
    return "none"


CRISIS_HOTLINES = [
    {
        "name": "National Institute of Mental Health (NIMH)",
        "contact": "+880-2-58153975",
        "description": "Government specialized mental health hospital providing psychiatric consultations, psychotherapy, inpatient care, and emergency mental health services.",
        "available": "24/7",
    },
    {
        "name": "Kaan Pete Roi",
        "contact": "01779-554391",
        "description": "Free emotional support and crisis intervention helpline operated by trained volunteers for people experiencing emotional distress.",
        "available": "Daily, 6 PM - 10 PM",
    },
    {
        "name": "SAJIDA Foundation Tele-Mental Health Support (SHOJON)",
        "contact": "09606119900",
        "description": "Tele-mental health counseling and psychological support service offering professional guidance and referrals.",
        "available": "Call for current service hours",
    },
    {
        "name": "Hi-Tech Modern Psychiatric Hospital",
        "contact": "01602-268405, 01711-662709",
        "description": "Private psychiatric hospital offering emergency mental health care, counseling, psychotherapy, addiction treatment, and inpatient services.",
        "available": "24/7",
    },
]
