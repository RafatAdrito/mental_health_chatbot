from app.tools.coping import get_coping_strategies


class TestCopingStrategies:
    def test_returns_anxiety_strategies(self):
        result = get_coping_strategies.invoke({"mood": "anxiety", "intensity": "moderate"})
        assert "anxiety" in result.lower()
        assert "Grounding" in result or "Breathing" in result or "Thought" in result

    def test_returns_depression_strategies(self):
        result = get_coping_strategies.invoke({"mood": "depression", "intensity": "mild"})
        assert "depression" in result.lower()

    def test_returns_general_for_unknown_mood(self):
        result = get_coping_strategies.invoke({"mood": "confused", "intensity": "moderate"})
        assert "general" in result.lower()

    def test_defaults_to_moderate_intensity(self):
        result = get_coping_strategies.invoke({"mood": "stress", "intensity": "unknown"})
        assert len(result) > 0

    def test_severe_includes_reach_out(self):
        result = get_coping_strategies.invoke({"mood": "general", "intensity": "severe"})
        assert "alone" in result.lower() or "help" in result.lower()
