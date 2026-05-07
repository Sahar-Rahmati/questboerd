from datetime import date, time
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.reports.services import get_weekly_report
from apps.tasks.models import Task
from apps.tasks.services import (
    apply_xp_cap,
    archive_task,
    complete_task,
    create_task_with_ai,
    detect_anomalies,
    finish_task_session,
    get_ai_preview,
    pause_task_session,
    refresh_task_ai,
    resume_task_session,
    start_task_session,
)

User = get_user_model()


class TaskCompletionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="taskuser", password="strongpass123", email="task@example.com")

    def test_task_creation_saves_ai_fields(self):
        task = create_task_with_ai(
            user=self.user,
            title="Read 10 pages",
            description="Book club",
            planned_date=date.today(),
            planned_start_time=time(12, 30),
            planned_end_time=time(13, 0),
        )
        self.assertEqual(task.ai_detected_difficulty, "easy")
        self.assertEqual(task.ai_estimated_duration_minutes, 15)

    def test_task_creation_defaults_to_today_without_schedule(self):
        task = create_task_with_ai(
            user=self.user,
            title="Take out the trash",
            description="",
        )
        self.assertEqual(task.planned_date, timezone.localdate())
        self.assertIsNone(task.planned_start_time)
        self.assertIsNone(task.planned_end_time)

    def test_anomaly_detection_flags_excessive_duration(self):
        task = create_task_with_ai(
            user=self.user,
            title="Read 10 pages",
            description="",
            planned_date=date.today(),
            planned_start_time=time(12, 0),
            planned_end_time=time(12, 30),
        )
        flags = detect_anomalies(task=task, actual_duration_minutes=600)
        self.assertIn("suspicious_duration_over_3x_estimate", flags)

    def test_easy_task_xp_is_capped(self):
        xp, was_capped = apply_xp_cap(difficulty="easy", xp=200, anomaly_flags=["suspicious_duration_over_3x_estimate"])
        self.assertEqual(xp, 100)
        self.assertTrue(was_capped)

    def test_task_completion_awards_xp(self):
        task = create_task_with_ai(
            user=self.user,
            title="Read 10 pages",
            description="",
            planned_date=date.today(),
            planned_start_time=time(12, 0),
            planned_end_time=time(12, 30),
        )
        completion = complete_task(task=task, actual_duration_minutes=20)
        self.assertEqual(completion.earned_xp, 9)
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.total_xp, 9)

    def test_medium_task_xp_uses_full_minutes_with_new_multiplier(self):
        task = create_task_with_ai(
            user=self.user,
            title="Study mathematics",
            description="Focus session",
            planned_date=date.today(),
            planned_start_time=time(12, 30),
            planned_end_time=time(15, 30),
        )
        completion = complete_task(task=task, actual_duration_minutes=327)
        self.assertEqual(completion.earned_xp, 224)
        self.assertEqual(completion.xp_breakdown["difficulty_multiplier"], 2.0)

    def test_ai_multiplier_no_longer_changes_xp_formula(self):
        task = create_task_with_ai(
            user=self.user,
            title="Study mathematics",
            description="Focus session",
            planned_date=date.today(),
            planned_start_time=time(12, 30),
            planned_end_time=time(15, 30),
        )
        task.ai_multiplier = 2.5
        task.save(update_fields=["ai_multiplier", "updated_at"])

        completion = complete_task(task=task, actual_duration_minutes=69)

        self.assertEqual(completion.earned_xp, 52)
        self.assertEqual(completion.xp_breakdown["raw_xp"], 52)

    def test_ai_preview_uses_time_range_for_studying(self):
        preview = get_ai_preview(
            title="Study mathematics",
            description="Focus session",
            planned_start_time=time(12, 30),
            planned_end_time=time(15, 30),
        )
        self.assertEqual(preview["detected_category"], "study")
        self.assertEqual(preview["detected_difficulty"], "medium")

    def test_instant_task_preview_is_easy_without_end_time(self):
        preview = get_ai_preview(
            title="Drink water",
            description="",
            planned_start_time=time(12, 30),
        )
        self.assertEqual(preview["detected_category"], "hydration")
        self.assertEqual(preview["detected_difficulty"], "easy")

    def test_instant_task_stays_easy_even_with_long_schedule_window(self):
        preview = get_ai_preview(
            title="Drink water",
            description="",
            planned_start_time=time(12, 30),
            planned_end_time=time(15, 30),
        )
        self.assertEqual(preview["detected_difficulty"], "easy")
        self.assertEqual(preview["estimated_duration_minutes"], 5)

    def test_cooking_dinner_preview_keeps_real_task_estimate(self):
        preview = get_ai_preview(
            title="Cooking dinner",
            description="",
            planned_start_time=time(18, 0),
        )
        self.assertEqual(preview["detected_category"], "cooking")
        self.assertEqual(preview["detected_difficulty"], "medium")
        self.assertGreaterEqual(preview["estimated_duration_minutes"], 45)

    def test_refresh_task_ai_updates_existing_task_with_current_classifier(self):
        task = create_task_with_ai(
            user=self.user,
            title="Climb Mount Everest",
            description="High-altitude mountain climbing expedition",
            planned_date=date.today(),
            planned_start_time=time(6, 0),
            planned_end_time=time(23, 0),
        )
        task.ai_detected_category = "health"
        task.ai_detected_difficulty = "medium"
        task.ai_estimated_duration_minutes = 15
        task.ai_explanation = "Old wrong result."
        task.save(
            update_fields=[
                "ai_detected_category",
                "ai_detected_difficulty",
                "ai_estimated_duration_minutes",
                "ai_explanation",
                "updated_at",
            ]
        )

        refreshed = refresh_task_ai(task=task)

        self.assertEqual(refreshed.ai_detected_category, "workout")
        self.assertEqual(refreshed.ai_detected_difficulty, "extreme")
        self.assertNotEqual(refreshed.ai_explanation, "Old wrong result.")

    def test_only_one_active_session_is_allowed(self):
        first_task = create_task_with_ai(
            user=self.user,
            title="Study physics",
            description="",
            planned_date=date.today(),
            planned_start_time=time(12, 0),
            planned_end_time=time(13, 0),
        )
        second_task = create_task_with_ai(
            user=self.user,
            title="Read a chapter",
            description="",
            planned_date=date.today(),
            planned_start_time=time(14, 0),
            planned_end_time=time(15, 0),
        )
        start_task_session(task=first_task)
        with self.assertRaisesMessage(ValueError, "Finish 'Study physics' before starting another task."):
            start_task_session(task=second_task)

    def test_overlapping_planned_tasks_cannot_both_be_reward_earning_sessions(self):
        first_task = create_task_with_ai(
            user=self.user,
            title="Study for final exam",
            description="",
            planned_date=date.today(),
            planned_start_time=time(12, 30),
            planned_end_time=time(15, 0),
        )
        second_task = create_task_with_ai(
            user=self.user,
            title="Study for final exam again",
            description="",
            planned_date=date.today(),
            planned_start_time=time(13, 0),
            planned_end_time=time(16, 0),
        )
        session = start_task_session(task=first_task)
        session.started_at = timezone.now() - timedelta(minutes=90)
        session.save(update_fields=["started_at"])
        finish_task_session(task=first_task)
        with self.assertRaisesMessage(ValueError, "cannot start as a reward-earning session"):
            start_task_session(task=second_task)

    def test_finish_task_session_uses_tracked_time(self):
        task = create_task_with_ai(
            user=self.user,
            title="Study mathematics",
            description="Focus session",
            planned_date=date.today(),
            planned_start_time=time(12, 30),
            planned_end_time=time(15, 30),
        )
        session = start_task_session(task=task)
        session.started_at = timezone.now() - timedelta(minutes=69)
        session.save(update_fields=["started_at"])
        completion = finish_task_session(task=task)
        self.assertEqual(completion.actual_duration_minutes, 69)
        self.assertEqual(completion.task.status, "completed")

    def test_pause_and_resume_only_count_active_time(self):
        task = create_task_with_ai(
            user=self.user,
            title="Study mathematics",
            description="Focus session",
        )
        session = start_task_session(task=task)
        session.started_at = timezone.now() - timedelta(minutes=20)
        session.save(update_fields=["started_at"])

        pause_task_session(task=task)
        session.refresh_from_db()
        paused_seconds = session.accumulated_seconds

        session.paused_at = timezone.now() - timedelta(minutes=30)
        session.save(update_fields=["paused_at"])
        resume_task_session(task=task)

        session.refresh_from_db()
        session.started_at = timezone.now() - timedelta(minutes=10)
        session.save(update_fields=["started_at"])

        completion = finish_task_session(task=task)

        self.assertGreaterEqual(paused_seconds, 20 * 60)
        self.assertLess(paused_seconds, 21 * 60)
        self.assertEqual(completion.actual_duration_minutes, 30)
        session.refresh_from_db()
        self.assertEqual(session.accumulated_seconds, 1800)
        self.assertIsNone(session.paused_at)

    def test_paused_task_cannot_start_again_until_resumed(self):
        task = create_task_with_ai(
            user=self.user,
            title="Write essay",
            description="",
        )
        start_task_session(task=task)
        pause_task_session(task=task)

        with self.assertRaisesMessage(ValueError, "This task is paused. Resume it instead."):
            start_task_session(task=task)

    def test_archiving_completed_task_keeps_it_in_weekly_report(self):
        task = create_task_with_ai(
            user=self.user,
            title="Take out the trash",
            description="",
        )
        session = start_task_session(task=task)
        session.started_at = timezone.now() - timedelta(minutes=5)
        session.save(update_fields=["started_at"])
        finish_task_session(task=task)

        archive_task(task=task)
        task.refresh_from_db()
        report = get_weekly_report(user=self.user)

        self.assertTrue(task.is_archived)
        self.assertEqual(report["tasks_completed_count"], 1)
        self.assertEqual(report["hardest_tasks"][0]["title"], "Take out the trash")


class TaskDeletionBehaviorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="apiuser", password="strongpass123", email="api@example.com")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_completed_task_delete_archives_but_hides_from_task_list(self):
        task = create_task_with_ai(
            user=self.user,
            title="Clean the desk",
            description="",
        )
        session = start_task_session(task=task)
        session.started_at = timezone.now() - timedelta(minutes=12)
        session.save(update_fields=["started_at"])
        finish_task_session(task=task)

        delete_response = self.client.delete(f"/api/v1/tasks/{task.id}/")
        self.assertEqual(delete_response.status_code, 204)

        task.refresh_from_db()
        self.assertTrue(task.is_archived)
        self.assertEqual(Task.objects.filter(user=self.user, is_archived=False).count(), 0)

        list_response = self.client.get("/api/v1/tasks/")
        self.assertEqual(list_response.status_code, 200)
        listed_tasks = list_response.data.get("results", list_response.data)
        self.assertEqual(len(listed_tasks), 0)

        report = get_weekly_report(user=self.user)
        self.assertEqual(report["tasks_completed_count"], 1)
