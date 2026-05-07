from django.contrib import admin

from .models import Task, TaskCompletion, TaskSession


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "planned_date", "status", "is_archived", "ai_detected_difficulty")
    list_filter = ("status", "is_archived", "ai_detected_category", "ai_detected_difficulty")
    search_fields = ("title", "description", "user__username")


@admin.register(TaskCompletion)
class TaskCompletionAdmin(admin.ModelAdmin):
    list_display = ("task", "earned_xp", "actual_duration_minutes", "completed_at")


@admin.register(TaskSession)
class TaskSessionAdmin(admin.ModelAdmin):
    list_display = ("task", "started_at", "paused_at", "ended_at", "accumulated_seconds", "tracked_duration_minutes")
