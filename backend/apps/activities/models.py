from django.conf import settings
from django.db import models

from apps.common.models import UUIDPrimaryKeyModel


class Activity(UUIDPrimaryKeyModel):
    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"
        EXTREME = "extreme", "Extreme"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=80)
    difficulty = models.CharField(max_length=20, choices=Difficulty.choices)
    estimated_duration_minutes = models.PositiveIntegerField()
    is_predefined = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_activities",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["is_predefined", "category", "title"]
        indexes = [
            models.Index(fields=["is_predefined", "category"]),
            models.Index(fields=["created_by"]),
        ]

    def __str__(self) -> str:
        return self.title
