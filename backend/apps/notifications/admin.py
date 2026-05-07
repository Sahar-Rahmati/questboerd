from django.contrib import admin

from apps.notifications.models import PushSubscription, TaskReminder


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "endpoint", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("user__username", "endpoint")


@admin.register(TaskReminder)
class TaskReminderAdmin(admin.ModelAdmin):
    list_display = ("task", "reminder_type", "scheduled_for", "delivery_count", "sent_at")
    list_filter = ("reminder_type",)
    search_fields = ("task__title", "task__user__username")

