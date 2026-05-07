from types import SimpleNamespace
from django.test import SimpleTestCase
from unittest.mock import patch

from apps.ai_engine.services import AIClassificationResult, classify_task, parse_openai_response


class AIClassifierTests(SimpleTestCase):
    def test_parse_openai_response_uses_output_text(self):
        response = SimpleNamespace(
            output_text='{"detected_category":"workout","detected_difficulty":"medium"}',
            output=[],
        )
        payload = parse_openai_response(response)
        self.assertEqual(payload["detected_category"], "workout")

    def test_parse_openai_response_falls_back_to_output_blocks(self):
        response = SimpleNamespace(
            output_text="",
            output=[],
            model_dump=lambda: {
                "output": [
                    {
                        "content": [
                            {
                                "text": '{"detected_category":"study","detected_difficulty":"hard"}'
                            }
                        ]
                    }
                ]
            },
        )
        payload = parse_openai_response(response)
        self.assertEqual(payload["detected_difficulty"], "hard")

    def test_read_10_pages_is_easy(self):
        result = classify_task(title="Read 10 pages", description="")
        self.assertEqual(result.detected_category, "reading")
        self.assertEqual(result.detected_difficulty, "easy")
        self.assertEqual(result.estimated_duration_minutes, 15)

    def test_build_authentication_system_is_extreme(self):
        result = classify_task(title="Build authentication system", description="For the API")
        self.assertEqual(result.detected_category, "coding")
        self.assertEqual(result.detected_difficulty, "extreme")
        self.assertEqual(result.ai_multiplier, 2.5)

    def test_drink_water_is_easy_even_with_long_schedule_context(self):
        result = classify_task(title="Drink water", description="", planned_duration_minutes=180)
        self.assertEqual(result.detected_category, "hydration")
        self.assertEqual(result.detected_difficulty, "easy")
        self.assertEqual(result.estimated_duration_minutes, 5)

    def test_take_my_medicine_is_easy_health_task(self):
        result = classify_task(title="Take my medicine", description="")
        self.assertEqual(result.detected_category, "health")
        self.assertEqual(result.detected_difficulty, "easy")
        self.assertEqual(result.estimated_duration_minutes, 10)

    def test_cooking_dinner_is_not_treated_as_instant_task(self):
        result = classify_task(title="Cooking dinner", description="")
        self.assertEqual(result.detected_category, "cooking")
        self.assertEqual(result.detected_difficulty, "medium")
        self.assertGreaterEqual(result.estimated_duration_minutes, 45)

    def test_study_text_does_not_become_hard_only_from_time_block(self):
        result = classify_task(title="Study mathematics", description="Focus session", planned_duration_minutes=180)
        self.assertEqual(result.detected_category, "study")
        self.assertEqual(result.detected_difficulty, "medium")

    def test_everest_is_not_misclassified_as_health_from_substring_match(self):
        result = classify_task(title="Climb Mount Everest", description="", planned_duration_minutes=1020)
        self.assertNotEqual(result.detected_category, "health")
        self.assertEqual(result.detected_category, "workout")

    def test_long_everest_climb_fallback_is_extreme(self):
        result = classify_task(title="Climb Mount Everest", description="High-altitude mountain climbing expedition", planned_duration_minutes=1020)
        self.assertEqual(result.detected_difficulty, "extreme")

    @patch("apps.ai_engine.services.classify_task_with_openai")
    def test_openai_result_is_used_when_available(self, classify_task_with_openai):
        classify_task_with_openai.return_value = AIClassificationResult(
            detected_category="outdoor endurance",
            estimated_workload="very heavy",
            estimated_duration_minutes=360,
            detected_difficulty="extreme",
            ai_multiplier=2.5,
            explanation="The model detected a long, demanding mountain hike with sustained physical effort.",
            anomaly_risk_rules={},
            is_quick_task=False,
            provider="openai",
            effort_domain="physical",
            stakes_level="high",
            confidence_score=0.92,
        )
        result = classify_task(title="Hiking", description="Mountain trail from 6 AM to 2 PM", planned_duration_minutes=480)
        self.assertEqual(result.detected_difficulty, "extreme")
        self.assertEqual(result.provider, "openai")

    @patch("apps.ai_engine.services.classify_task_with_openai")
    def test_openai_exam_prep_is_calibrated_up_when_model_is_too_low(self, classify_task_with_openai):
        classify_task_with_openai.return_value = AIClassificationResult(
            detected_category="study",
            estimated_workload="moderate",
            estimated_duration_minutes=300,
            detected_difficulty="medium",
            ai_multiplier=1.4,
            explanation="The model saw a long study block.",
            anomaly_risk_rules={},
            is_quick_task=False,
            provider="openai",
            effort_domain="cognitive",
            stakes_level="critical",
            confidence_score=0.81,
        )
        result = classify_task(title="Prepare for final exam", description="", planned_duration_minutes=300)
        self.assertEqual(result.detected_difficulty, "extreme")
        self.assertGreaterEqual(result.ai_multiplier, 2.5)

    @patch("apps.ai_engine.services.classify_task_with_openai")
    def test_openai_hiking_is_calibrated_up_when_model_is_too_low(self, classify_task_with_openai):
        classify_task_with_openai.return_value = AIClassificationResult(
            detected_category="outdoor endurance",
            estimated_workload="moderate",
            estimated_duration_minutes=440,
            detected_difficulty="medium",
            ai_multiplier=1.4,
            explanation="The model saw a long hiking block.",
            anomaly_risk_rules={},
            is_quick_task=False,
            provider="openai",
            effort_domain="physical",
            stakes_level="normal",
            confidence_score=0.79,
        )
        result = classify_task(title="Hiking", description="Mountain trail", planned_duration_minutes=440)
        self.assertEqual(result.detected_difficulty, "extreme")
        self.assertGreaterEqual(result.ai_multiplier, 2.5)
