from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.notifications.models import PushSubscription, TaskReminder
from apps.tasks.models import Task

logger = logging.getLogger(__name__)


def get_push_configuration(*, user) -> dict:
    return {
        "vapid_public_key": getattr(settings, "VAPID_PUBLIC_KEY", "") or "",
        "is_configured": bool(getattr(settings, "VAPID_PUBLIC_KEY", "") and getattr(settings, "VAPID_PRIVATE_KEY", "")),
        "has_active_subscription": PushSubscription.objects.filter(user=user, is_active=True).exists(),
    }


@transaction.atomic
def save_push_subscription(*, user, endpoint: str, p256dh_key: str, auth_key: str, expiration_time: int | None, user_agent: str) -> PushSubscription:
    subscription, _ = PushSubscription.objects.update_or_create(
        endpoint=endpoint,
        defaults={
            "user": user,
            "p256dh_key": p256dh_key,
            "auth_key": auth_key,
            "expiration_time": expiration_time,
            "user_agent": user_agent,
            "is_active": True,
        },
    )
    return subscription


def deactivate_push_subscription(*, user, endpoint: str) -> int:
    return PushSubscription.objects.filter(user=user, endpoint=endpoint, is_active=True).update(is_active=False)


def mark_subscription_inactive(subscription: PushSubscription) -> None:
    PushSubscription.objects.filter(pk=subscription.pk).update(is_active=False)


def build_task_reminder_payload(task: Task) -> dict:
    planned_time = task.planned_start_time.strftime("%H:%M") if task.planned_start_time else "now"
    return {
        "title": f"It's time for {task.title}",
        "body": f"Your task is scheduled for {planned_time}. Estimated difficulty: {task.ai_detected_difficulty}.",
        "tag": f"task-reminder-{task.id}",
        "url": f"{settings.FRONTEND_URL.rstrip('/')}/",
        "task_id": str(task.id),
    }


def send_web_push_message(*, subscription: PushSubscription, payload: dict) -> bool:
    public_key = getattr(settings, "VAPID_PUBLIC_KEY", "")
    private_key = getattr(settings, "VAPID_PRIVATE_KEY", "")
    if not public_key or not private_key:
        logger.warning("Web push skipped because VAPID keys are not configured.")
        return False

    try:
        from pywebpush import WebPushException, webpush
    except ImportError:
        logger.exception("pywebpush is not installed, so push notifications cannot be sent.")
        return False

    try:
        webpush(
            subscription_info={
                "endpoint": subscription.endpoint,
                "keys": {
                    "p256dh": subscription.p256dh_key,
                    "auth": subscription.auth_key,
                },
            },
            data=json.dumps(payload),
            vapid_private_key=private_key,
            vapid_claims={"sub": f"mailto:{getattr(settings, 'VAPID_ADMIN_EMAIL', settings.DEFAULT_FROM_EMAIL)}"},
        )
        return True
    except WebPushException as exc:
        status_code = getattr(getattr(exc, "response", None), "status_code", None)
        if status_code in {404, 410}:
            mark_subscription_inactive(subscription)
        logger.warning("Web push delivery failed for subscription %s: %s", subscription.pk, exc)
        return False


def iter_due_tasks(*, current_time: datetime | None = None):
    now_local = timezone.localtime(current_time or timezone.now())
    lookback_seconds = 59
    lookahead_minutes = int(getattr(settings, "TASK_REMINDER_LOOKAHEAD_MINUTES", 0))
    window_start = now_local - timedelta(seconds=lookback_seconds)
    window_end = now_local + timedelta(minutes=lookahead_minutes, seconds=59)
    candidate_dates = sorted({window_start.date(), now_local.date(), window_end.date()})

    tasks = (
        Task.objects.filter(
            status=Task.Status.PENDING,
            planned_date__in=candidate_dates,
            planned_start_time__isnull=False,
        )
        .select_related("user")
        .prefetch_related("reminders")
    )
    for task in tasks:
        start_at = timezone.make_aware(datetime.combine(task.planned_date, task.planned_start_time), timezone.get_current_timezone())
        if window_start <= start_at <= window_end and not task.reminders.filter(
            reminder_type=TaskReminder.ReminderType.EXACT_START,
        ).exists():
            yield task, start_at


@transaction.atomic
def dispatch_due_task_reminders(*, current_time: datetime | None = None) -> int:
    return 0
