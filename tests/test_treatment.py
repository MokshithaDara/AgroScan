from utils.treatment import get_treatment_plan


def test_treatment_plan_includes_weather_caution_for_humidity():
    plan = get_treatment_plan(
        "Chilli - Whitefly",
        weather={"humidity": 86, "temperature": 30, "condition": "clear sky"},
    )
    assert isinstance(plan["steps"], list)
    assert len(plan["steps"]) >= 3
    assert any("Humidity" in item for item in plan["weather_cautions"])


def test_treatment_plan_fallback_for_unknown_disease():
    plan = get_treatment_plan("UnknownDisease")
    assert "summary" in plan
    assert len(plan["steps"]) >= 1
