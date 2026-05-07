from django.contrib import admin

from .models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "difficulty", "estimated_duration_minutes", "is_predefined")
    list_filter = ("category", "difficulty", "is_predefined")
    search_fields = ("title",)
