from django.conf import settings
from django.db import models

from apps.common.models import UUIDPrimaryKeyModel


class XPTransaction(UUIDPrimaryKeyModel):
    class TransactionType(models.TextChoices):
        TASK_COMPLETION = "task_completion", "Task Completion"
        STREAK_BONUS = "streak_bonus", "Streak Bonus"
        ADJUSTMENT = "adjustment", "Adjustment"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="xp_transactions")
    task_completion = models.ForeignKey(
        "tasks.TaskCompletion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="xp_transactions",
    )
    amount = models.IntegerField()
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "created_at"])]


class WalletTransaction(UUIDPrimaryKeyModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet_transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255)
    related_level = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "related_level", "reason"], name="unique_wallet_reward_per_reason_level")
        ]


class LevelHistory(UUIDPrimaryKeyModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="level_history")
    old_level = models.PositiveIntegerField()
    new_level = models.PositiveIntegerField()
    reward_granted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "new_level"], name="unique_level_history_entry_per_level")
        ]


class StreakLog(UUIDPrimaryKeyModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="streak_logs")
    date = models.DateField()
    completed_all_tasks = models.BooleanField(default=False)
    streak_after_evaluation = models.PositiveIntegerField(default=0)
    bonus_xp_awarded = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "date"], name="unique_streak_log_per_user_date")
        ]
