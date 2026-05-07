from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.gamification.models import LevelHistory, StreakLog, WalletTransaction, XPTransaction
from apps.users.models import UserProfile

User = get_user_model()
XP_PER_LEVEL = 500
LEVEL_REWARD_INTERVAL = 5
LEVEL_REWARD_AMOUNT = Decimal("5.00")
STREAK_BONUS_XP = 50


def calculate_level(total_xp: int) -> int:
    return (total_xp // XP_PER_LEVEL) + 1


@transaction.atomic
def award_wallet_reward(*, user, level: int) -> bool:
    return False


@transaction.atomic
def update_level_and_rewards(*, user) -> dict:
    profile = UserProfile.objects.select_for_update().get(user=user)
    previous_level = profile.level
    new_level = calculate_level(profile.total_xp)
    reward_granted = False
    if new_level != previous_level:
        profile.level = new_level
        profile.save(update_fields=["level", "updated_at"])
        LevelHistory.objects.get_or_create(
            user=user,
            new_level=new_level,
            defaults={
                "old_level": previous_level,
                "reward_granted": False,
            },
        )
        reward_granted = award_wallet_reward(user=user, level=new_level)
        if reward_granted:
            LevelHistory.objects.filter(user=user, new_level=new_level).update(reward_granted=True)
    return {"old_level": previous_level, "new_level": new_level, "reward_granted": reward_granted}


@transaction.atomic
def award_xp(*, user, amount: int, transaction_type: str, description: str, task_completion=None):
    profile = UserProfile.objects.select_for_update().get(user=user)
    XPTransaction.objects.create(
        user=user,
        task_completion=task_completion,
        amount=amount,
        transaction_type=transaction_type,
        description=description,
    )
    profile.total_xp += amount
    profile.save(update_fields=["total_xp", "updated_at"])
    return update_level_and_rewards(user=user)


@transaction.atomic
def evaluate_user_streak(*, user, target_date):
    return None


def evaluate_previous_day_for_all_users():
    return None


def get_user_weekly_xp(user) -> int:
    now = timezone.localtime()
    week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    value = user.xp_transactions.filter(created_at__gte=week_start).aggregate(total=Sum("amount"))["total"]
    return value or 0
