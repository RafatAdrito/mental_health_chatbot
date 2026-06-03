import pytest

from app.utils.safety import sanitize_response


class TestSanitizeResponse:
    def test_catches_diagnosis_language(self):
        text = "Based on what you've told me, you have depression and should seek help."
        result = sanitize_response(text)
        assert "you have depression" not in result
        assert "healthcare professional" in result

    def test_catches_medication_recommendation(self):
        text = "You should take Prozac to help with your symptoms."
        result = sanitize_response(text)
        assert "Prozac" not in result.lower() or "not able to recommend" in result
        assert "doctor" in result or "psychiatrist" in result

    def test_passes_safe_text(self):
        text = "It sounds like you're going through a tough time. Would you like to talk about it?"
        result = sanitize_response(text)
        assert result == text

    def test_passes_coping_strategy(self):
        text = "Some people find breathing exercises helpful. Would you like to try one?"
        result = sanitize_response(text)
        assert result == text

    def test_catches_suffer_from_language(self):
        text = "You suffer from anxiety disorder based on your symptoms."
        result = sanitize_response(text)
        assert "suffer from anxiety" not in result

    def test_catches_diagnosis_with_clinical_terms(self):
        text = "You are showing signs of bipolar disorder."
        result = sanitize_response(text)
        assert "showing signs of bipolar" not in result
