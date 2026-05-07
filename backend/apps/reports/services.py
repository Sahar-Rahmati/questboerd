from __future__ import annotations

from datetime import timedelta

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from apps.gamification.models import WalletTransaction, XPTransaction
from apps.tasks.models import TaskCompletion

DIFFICULTY_ORDER = {"easy": 1, "medium": 2, "hard": 3, "extreme": 4}


def week_bounds(reference_date=None):
    today = reference_date or timezone.localdate()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start, end


def get_weekly_report(*, user, reference_date=None):
    start, end = week_bounds(reference_date)
    completions = TaskCompletion.objects.filter(task__user=user, completed_at__date__range=(start, end)).select_related("task", "task__activity")
    xp_transactions = XPTransaction.objects.filter(user=user, created_at__date__range=(start, end))
    wallet_transactions = WalletTransaction.objects.filter(user=user, created_at__date__range=(start, end))
    category_breakdown = list(
        completions.values("task__activity__category").annotate(count=Count("id")).order_by("-count")
    )
    daily_xp = list(
        xp_transactions.annotate(day=TruncDate("created_at")).values("day").annotate(total_xp=Sum("amount")).order_by("day")
    )
    hardest = sorted(
        [
            {
                "task_id": str(completion.task_id),
                "title": completion.task.title,
                "difficulty": completion.task.ai_detected_difficulty,
                "earned_xp": completion.earned_xp,
                "completed_at": completion.completed_at,
            }
            for completion in completions
        ],
        key=lambda item: (DIFFICULTY_ORDER[item["difficulty"]], item["earned_xp"]),
        reverse=True,
    )[:5]

    return {
        "week_start": start,
        "week_end": end,
        "completed_tasks": completions.count(),
        "total_xp_earned": xp_transactions.aggregate(total=Sum("amount"))["total"] or 0,
        "tasks_completed_count": completions.count(),
        "category_breakdown": [
            {"category": row["task__activity__category"], "count": row["count"]} for row in category_breakdown
        ],
        "streak_performance": user.profile.streak_count,
        "wallet_rewards_earned": str(wallet_transactions.aggregate(total=Sum("amount"))["total"] or 0),
        "hardest_tasks": hardest,
        "daily_xp_chart": [
            {"date": row["day"], "xp": row["total_xp"]} for row in daily_xp
        ],
    }
