from celery import shared_task

from apps.gamification.services import evaluate_previous_day_for_all_users


@shared_task
def evaluate_previous_day_streaks():
    evaluate_previous_day_for_all_users()
