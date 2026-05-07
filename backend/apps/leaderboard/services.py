from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.users.models import UserProfile

User = get_user_model()


def _paginate(*, items, page: int, page_size: int):
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end], len(items)


def get_all_time_leaderboard(*, page: int = 1, page_size: int = 10):
    cache_key = f"leaderboard:all-time:{page}:{page_size}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    profiles = list(UserProfile.objects.select_related("user").order_by("-total_xp", "user__username"))
    rows = [
        {
            "rank": index + 1,
            "user_id": str(profile.user_id),
            "username": profile.user.username,
            "total_xp": profile.total_xp,
            "level": profile.level,
        }
        for index, profile in enumerate(profiles)
    ]
    results, count = _paginate(items=rows, page=page, page_size=page_size)
    payload = {"count": count, "results": results, "page": page, "page_size": page_size}
    cache.set(cache_key, payload, 120)
    return payload


def get_weekly_leaderboard(*, page: int = 1, page_size: int = 10):
    cache_key = f"leaderboard:weekly:{page}:{page_size}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    now = timezone.localtime()
    week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    users = (
        User.objects.select_related("profile")
        .annotate(weekly_xp=Coalesce(Sum("xp_transactions__amount", filter=Q(xp_transactions__created_at__gte=week_start)), 0))
        .order_by("-weekly_xp", "username")
    )
    rows = [
        {
            "rank": index + 1,
            "user_id": str(user.id),
            "username": user.username,
            "weekly_xp": user.weekly_xp or 0,
            "level": user.profile.level,
        }
        for index, user in enumerate(users)
    ]
    results, count = _paginate(items=rows, page=page, page_size=page_size)
    payload = {"count": count, "results": results, "page": page, "page_size": page_size}
    cache.set(cache_key, payload, 120)
    return payload


def get_current_user_rank(*, user):
    all_time_profiles = list(UserProfile.objects.order_by("-total_xp", "user__username").values_list("user_id", flat=True))
    weekly_rows = get_weekly_leaderboard(page=1, page_size=max(1, User.objects.count()))["results"]
    return {
        "all_time_rank": all_time_profiles.index(user.id) + 1 if user.id in all_time_profiles else None,
        "weekly_rank": next((row["rank"] for row in weekly_rows if row["user_id"] == str(user.id)), None),
    }
