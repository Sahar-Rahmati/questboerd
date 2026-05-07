from django.conf import settings
from django.db import models

from apps.activities.models import Activity
from apps.common.models import TimestampedModel, UUIDPrimaryKeyModel


class Task(TimestampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks")
    activity = models.ForeignKey(Activity, on_delete=models.PROTECT, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    planned_date = models.DateField()
    planned_start_time = models.TimeField(null=True, blank=True)
    planned_end_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    ai_detected_category = models.CharField(max_length=80, default="general")
    ai_detected_difficulty = models.CharField(max_length=20, choices=Activity.Difficulty.choices, default=Activity.Difficulty.EASY)
    ai_estimated_duration_minutes = models.PositiveIntegerField(default=15)
    ai_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)
    ai_explanation = models.TextField(blank=True)
    anomaly_flags = models.JSONField(default=dict, blank=True)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["planned_date", "created_at"]
        indexes = [
            models.Index(fields=["user", "planned_date"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "is_archived"]),
        ]

    def __str__(self) -> str:
        return self.title


class TaskCompletion(UUIDPrimaryKeyModel):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name="completion")
    actual_duration_minutes = models.PositiveIntegerField()
    earned_xp = models.PositiveIntegerField()
    xp_breakdown = models.JSONField(default=dict)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-completed_at"]


class TaskSession(UUIDPrimaryKeyModel):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name="session")
    started_at = models.DateTimeField()
    paused_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    accumulated_seconds = models.PositiveIntegerField(default=0)
    tracked_duration_minutes = models.PositiveIntegerField(default=0)
    reward_blocked_reason = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-started_at"]
