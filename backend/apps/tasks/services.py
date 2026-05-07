from __future__ import annotations

import math
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.activities.models import Activity
from apps.ai_engine.services import (
    DIFFICULTY_COMPLETION_BONUS,
    DIFFICULTY_MULTIPLIERS,
    XP_CAPS,
    calculate_minutes_between,
    classify_task,
    estimate_xp,
)
from apps.gamification.services import award_xp
from apps.tasks.models import Task, TaskCompletion, TaskSession


def build_task_ai_fields(*, title: str, description: str = "", planned_start_time=None, planned_end_time=None) -> tuple:
    planned_duration_minutes = calculate_minutes_between(planned_start_time, planned_end_time)
    preview = classify_task(
        title=title,
        description=description,
        planned_duration_minutes=planned_duration_minutes,
    )
    return planned_duration_minutes, preview


def get_ai_preview(
    *,
    title: str,
    description: str = "",
    planned_start_time=None,
    planned_end_time=None,
) -> dict:
    _, preview = build_task_ai_fields(
        title=title,
        description=description,
        planned_start_time=planned_start_time,
        planned_end_time=planned_end_time,
    )
    return preview.to_dict()


@transaction.atomic
def create_task_with_ai(*, user, title: str, description: str, planned_date=None, planned_start_time=None, planned_end_time=None):
    _, preview = build_task_ai_fields(
        title=title,
        description=description,
        planned_start_time=planned_start_time,
        planned_end_time=planned_end_time,
    )
    planned_date = planned_date or timezone.localdate()
    activity, _ = Activity.objects.get_or_create(
        title=title,
        created_by=user,
        defaults={
            "description": description,
            "category": preview.detected_category,
            "difficulty": preview.detected_difficulty,
            "estimated_duration_minutes": preview.estimated_duration_minutes,
            "is_predefined": False,
        },
    )
    return Task.objects.create(
        user=user,
        activity=activity,
        title=title,
        description=description,
        planned_date=planned_date,
        planned_start_time=planned_start_time,
        planned_end_time=planned_end_time,
        ai_detected_category=preview.detected_category,
        ai_detected_difficulty=preview.detected_difficulty,
        ai_estimated_duration_minutes=preview.estimated_duration_minutes,
        ai_multiplier=Decimal(str(preview.ai_multiplier)),
        ai_explanation=preview.explanation,
        anomaly_flags=preview.anomaly_risk_rules,
    )


@transaction.atomic
def refresh_task_ai(*, task: Task) -> Task:
    _, preview = build_task_ai_fields(
        title=task.title,
        description=task.description,
        planned_start_time=task.planned_start_time,
        planned_end_time=task.planned_end_time,
    )
    if not task.activity.is_predefined:
        task.activity.category = preview.detected_category
        task.activity.difficulty = preview.detected_difficulty
        task.activity.estimated_duration_minutes = preview.estimated_duration_minutes
        task.activity.description = task.description
        task.activity.save(
            update_fields=[
                "category",
                "difficulty",
                "estimated_duration_minutes",
                "description",
            ]
        )
    task.ai_detected_category = preview.detected_category
    task.ai_detected_difficulty = preview.detected_difficulty
    task.ai_estimated_duration_minutes = preview.estimated_duration_minutes
    task.ai_multiplier = Decimal(str(preview.ai_multiplier))
    task.ai_explanation = preview.explanation
    task.anomaly_flags = preview.anomaly_risk_rules
    task.save(
        update_fields=[
            "ai_detected_category",
            "ai_detected_difficulty",
            "ai_estimated_duration_minutes",
            "ai_multiplier",
            "ai_explanation",
            "anomaly_flags",
            "updated_at",
        ]
    )
    return task


@transaction.atomic
def archive_task(*, task: Task) -> Task:
    task.is_archived = True
    task.archived_at = timezone.now()
    task.save(update_fields=["is_archived", "archived_at", "updated_at"])
    return task


def find_active_session(*, user, exclude_task_id=None) -> TaskSession | None:
    queryset = TaskSession.objects.select_related("task").filter(task__user=user, ended_at__isnull=True)
    if exclude_task_id:
        queryset = queryset.exclude(task_id=exclude_task_id)
    return queryset.first()


def tasks_have_overlapping_planned_windows(task: Task, other_task: Task) -> bool:
    if task.planned_date != other_task.planned_date:
        return False
    if not (task.planned_start_time and task.planned_end_time and other_task.planned_start_time and other_task.planned_end_time):
        return False
    return not (
        task.planned_end_time <= other_task.planned_start_time
        or task.planned_start_time >= other_task.planned_end_time
    )


def find_reward_overlap(task: Task) -> Task | None:
    if not (task.planned_start_time and task.planned_end_time):
        return None
    candidates = (
        Task.objects.filter(user=task.user, planned_date=task.planned_date)
        .exclude(id=task.id)
        .exclude(status=Task.Status.CANCELLED)
        .select_related("completion", "session")
    )
    for candidate in candidates:
        if not (hasattr(candidate, "completion") or hasattr(candidate, "session")):
            continue
        if tasks_have_overlapping_planned_windows(task, candidate):
            return candidate
    return None


@transaction.atomic
def start_task_session(*, task: Task) -> TaskSession:
    if task.status == Task.Status.COMPLETED:
        raise ValueError("This task is already completed.")
    if hasattr(task, "session") and task.session.ended_at is None:
        if task.session.paused_at is not None:
            raise ValueError("This task is paused. Resume it instead.")
        raise ValueError("This task is already running.")
    active_session = find_active_session(user=task.user, exclude_task_id=task.id)
    if active_session is not None:
        raise ValueError(f"Finish '{active_session.task.title}' before starting another task.")
    overlapping_task = find_reward_overlap(task)
    if overlapping_task is not None:
        raise ValueError(f"This task overlaps with '{overlapping_task.title}', so it cannot start as a reward-earning session.")
    if hasattr(task, "session") and task.session.ended_at is not None:
        raise ValueError("This task already has a finished session.")
    return TaskSession.objects.create(task=task, started_at=timezone.now())


def calculate_session_elapsed_seconds(session: TaskSession, *, reference_time=None) -> int:
    total_seconds = session.accumulated_seconds
    if session.ended_at is not None or session.paused_at is not None:
        return total_seconds
    reference_time = reference_time or timezone.now()
    return total_seconds + max(0, math.floor((reference_time - session.started_at).total_seconds()))


@transaction.atomic
def pause_task_session(*, task: Task) -> TaskSession:
    if not hasattr(task, "session") or task.session.ended_at is not None:
        raise ValueError("Start this task before you pause it.")
    session = task.session
    if session.paused_at is not None:
        raise ValueError("This task is already paused.")
    paused_at = timezone.now()
    session.accumulated_seconds = calculate_session_elapsed_seconds(session, reference_time=paused_at)
    session.paused_at = paused_at
    session.save(update_fields=["accumulated_seconds", "paused_at"])
    return session


@transaction.atomic
def resume_task_session(*, task: Task) -> TaskSession:
    if not hasattr(task, "session") or task.session.ended_at is not None:
        raise ValueError("Start this task before you resume it.")
    session = task.session
    if session.paused_at is None:
        raise ValueError("This task is already running.")
    session.started_at = timezone.now()
    session.paused_at = None
    session.save(update_fields=["started_at", "paused_at"])
    return session


@transaction.atomic
def finish_task_session(*, task: Task) -> TaskCompletion:
    if not hasattr(task, "session") or task.session.ended_at is not None:
        raise ValueError("Start this task before you finish it.")
    session = task.session
    ended_at = timezone.now()
    elapsed_seconds = max(60, calculate_session_elapsed_seconds(session, reference_time=ended_at))
    actual_duration_minutes = max(1, math.floor(elapsed_seconds / 60))
    session.ended_at = ended_at
    session.paused_at = None
    session.accumulated_seconds = elapsed_seconds
    session.tracked_duration_minutes = actual_duration_minutes
    session.save(update_fields=["ended_at", "paused_at", "accumulated_seconds", "tracked_duration_minutes"])
    return complete_task(task=task, actual_duration_minutes=actual_duration_minutes)


def detect_anomalies(*, task: Task, actual_duration_minutes: int) -> list[str]:
    flags = []
    estimated = task.ai_estimated_duration_minutes or 1
    if actual_duration_minutes > estimated * 3:
        flags.append("suspicious_duration_over_3x_estimate")
    if actual_duration_minutes < max(1, estimated // 4):
        flags.append("suspicious_duration_under_quarter_estimate")
    return flags


def apply_xp_cap(*, difficulty: str, xp: int, anomaly_flags: list[str]) -> tuple[int, bool]:
    cap = XP_CAPS[difficulty]
    should_cap = xp > cap or bool(anomaly_flags)
    return (min(xp, cap), should_cap)


@transaction.atomic
def complete_task(*, task: Task, actual_duration_minutes: int) -> TaskCompletion:
    if task.status == Task.Status.COMPLETED:
        raise ValueError("Task already completed.")
    anomaly_flags = detect_anomalies(task=task, actual_duration_minutes=actual_duration_minutes)
    raw_xp = estimate_xp(
        actual_duration_minutes=actual_duration_minutes,
        detected_difficulty=task.ai_detected_difficulty,
        ai_multiplier=float(task.ai_multiplier),
    )
    final_xp, was_capped = apply_xp_cap(
        difficulty=task.ai_detected_difficulty,
        xp=raw_xp,
        anomaly_flags=anomaly_flags,
    )
    difficulty_multiplier = float(DIFFICULTY_MULTIPLIERS[task.ai_detected_difficulty])
    completion_bonus = DIFFICULTY_COMPLETION_BONUS[task.ai_detected_difficulty]
    time_xp = round((actual_duration_minutes / 3) * difficulty_multiplier)
    breakdown = {
        "actual_duration_minutes": actual_duration_minutes,
        "base_xp": time_xp,
        "time_xp": time_xp,
        "completion_bonus": completion_bonus,
        "detected_difficulty": task.ai_detected_difficulty,
        "difficulty_multiplier": difficulty_multiplier,
        "ai_multiplier": float(task.ai_multiplier),
        "final_xp": final_xp,
        "raw_xp": raw_xp,
        "anomaly_flags": anomaly_flags,
        "xp_capped": was_capped,
        "xp_cap": XP_CAPS[task.ai_detected_difficulty],
    }
    task.status = Task.Status.COMPLETED
    task.anomaly_flags = {
        **(task.anomaly_flags or {}),
        "completion_flags": anomaly_flags,
    }
    task.save(update_fields=["status", "anomaly_flags", "updated_at"])
    completion = TaskCompletion.objects.create(
        task=task,
        actual_duration_minutes=actual_duration_minutes,
        earned_xp=final_xp,
        xp_breakdown=breakdown,
    )
    award_xp(
        user=task.user,
        amount=final_xp,
        transaction_type="task_completion",
        description=f"XP awarded for completing task '{task.title}'",
        task_completion=completion,
    )
    return completion
