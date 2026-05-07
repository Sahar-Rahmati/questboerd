from django.conf import settings
from django.db import models

from apps.common.models import TimestampedModel, UUIDPrimaryKeyModel
from apps.tasks.models import Task


class PushSubscription(TimestampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="push_subscriptions")
    endpoint = models.TextField(unique=True)
    p256dh_key = models.TextField()
    auth_key = models.TextField()
    expiration_time = models.BigIntegerField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    last_seen_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.endpoint[:40]}"


class TaskReminder(UUIDPrimaryKeyModel):
    class ReminderType(models.TextChoices):
        EXACT_START = "exact_start", "Exact Start"

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="reminders")
    reminder_type = models.CharField(max_length=30, choices=ReminderType.choices, default=ReminderType.EXACT_START)
    scheduled_for = models.DateTimeField()
    sent_at = models.DateTimeField(auto_now_add=True)
    delivery_count = models.PositiveIntegerField(default=0)
    payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-sent_at"]
        constraints = [
            models.UniqueConstraint(fields=["task", "reminder_type"], name="unique_task_reminder_type"),
        ]
        indexes = [
            models.Index(fields=["scheduled_for"]),
        ]

    def __str__(self) -> str:
        return f"{self.task_id}:{self.reminder_type}"

