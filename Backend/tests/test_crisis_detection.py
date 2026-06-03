import pytest

from app.services.crisis_service import (
    CrisisMatch,
    classify_risk,
    compute_keyword_score,
    scan_keywords,
)


class TestKeywordScanning:
    def test_detects_suicidal_ideation(self):
        matches = scan_keywords("I want to kill myself")
        assert len(matches) > 0
        assert any(m.category == "suicidal_ideation" for m in matches)

    def test_detects_suicide_word(self):
        matches = scan_keywords("I've been thinking about suicide")
        assert len(matches) > 0
        assert any(m.category == "suicidal_ideation" for m in matches)

    def test_detects_wish_dead(self):
        matches = scan_keywords("I wish I were dead")
        assert len(matches) > 0
        assert any(m.severity >= 0.9 for m in matches)

    def test_detects_self_harm(self):
        matches = scan_keywords("I've been cutting myself lately")
        assert len(matches) > 0
        assert any(m.category == "self_harm" for m in matches)

    def test_detects_overdose(self):
        matches = scan_keywords("I overdosed last night")
        assert len(matches) > 0
        assert any(m.category == "substance_crisis" for m in matches)

    def test_detects_abuse(self):
        matches = scan_keywords("I'm being abused at home")
        assert len(matches) > 0
        assert any(m.category == "abuse" for m in matches)

    def test_detects_severe_distress(self):
        matches = scan_keywords("I can't take it anymore")
        assert len(matches) > 0
        assert any(m.category == "severe_distress" for m in matches)

    def test_no_false_positive_on_normal_text(self):
        matches = scan_keywords("I'm having a great day today!")
        assert len(matches) == 0

    def test_no_false_positive_on_mild_sadness(self):
        matches = scan_keywords("I feel a bit sad today")
        assert len(matches) == 0

    def test_no_false_positive_on_general_stress(self):
        matches = scan_keywords("Work has been really stressful lately")
        assert len(matches) == 0

    def test_no_false_positive_on_metaphor(self):
        matches = scan_keywords("I want to give up on this project")
        if matches:
            assert all(m.severity < 0.5 for m in matches)

    def test_dont_want_to_live(self):
        matches = scan_keywords("I don't want to live anymore")
        assert len(matches) > 0
        assert any(m.category == "suicidal_ideation" for m in matches)

    def test_better_off_dead(self):
        matches = scan_keywords("Everyone would be better off without me")
        assert len(matches) > 0


class TestKeywordScoring:
    def test_empty_matches_returns_zero(self):
        assert compute_keyword_score([]) == 0.0

    def test_single_match(self):
        matches = [CrisisMatch(phrase="suicide", category="suicidal_ideation", severity=0.95)]
        assert compute_keyword_score(matches) == 0.95

    def test_multiple_matches_returns_max(self):
        matches = [
            CrisisMatch(phrase="hopeless", category="severe_distress", severity=0.6),
            CrisisMatch(phrase="kill myself", category="suicidal_ideation", severity=1.0),
        ]
        assert compute_keyword_score(matches) == 1.0


class TestRiskClassification:
    def test_no_risk(self):
        assert classify_risk(0.0, 0.0, 0.0) == "none"

    def test_low_risk(self):
        result = classify_risk(0.3, 0.1, 0.0)
        assert result in ("low", "medium")

    def test_medium_risk(self):
        result = classify_risk(0.5, 0.4, 0.0)
        assert result in ("medium", "high")

    def test_high_risk(self):
        result = classify_risk(0.8, 0.7, 0.0)
        assert result in ("high", "critical")

    def test_critical_risk(self):
        result = classify_risk(1.0, 1.0, 0.5)
        assert result == "critical"

    def test_context_factor_elevates_risk(self):
        r1 = classify_risk(0.3, 0.3, 0.0)
        r2 = classify_risk(0.3, 0.3, 0.5)
        risk_order = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
        assert risk_order[r2] >= risk_order[r1]
