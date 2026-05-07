from datetime import date, datetime, time
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.notifications.models import PushSubscription, TaskReminder
from apps.notifications.services import dispatch_due_task_reminders
from apps.tasks.services import create_task_with_ai

User = get_user_model()


class NotificationReminderTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="notifyuser", password="strongpass123", email="notify@example.com")
        self.subscription = PushSubscription.objects.create(
            user=self.user,
            endpoint="https://example.com/push/123",
            p256dh_key="p256dh-key",
            auth_key="auth-key",
            is_active=True,
        )

    @patch("apps.notifications.services.send_web_push_message", return_value=True)
    def test_due_task_reminders_are_disabled(self, mocked_send):
        now = timezone.localtime()
        task = create_task_with_ai(
            user=self.user,
            title="Take my medicine",
            description="Evening reminder",
            planned_date=now.date(),
            planned_start_time=now.time().replace(second=0, microsecond=0),
        )

        sent_first = dispatch_due_task_reminders(current_time=now.replace(second=30, microsecond=0))
        sent_second = dispatch_due_task_reminders(current_time=now.replace(second=45, microsecond=0))

        self.assertEqual(sent_first, 0)
        self.assertEqual(sent_second, 0)
        self.assertEqual(mocked_send.call_count, 0)
        self.assertFalse(TaskReminder.objects.filter(task=task).exists())
