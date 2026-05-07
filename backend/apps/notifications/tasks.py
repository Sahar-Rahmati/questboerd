from celery import shared_task

from apps.notifications.services import dispatch_due_task_reminders


@shared_task
def send_due_task_reminders():
    return dispatch_due_task_reminders()

