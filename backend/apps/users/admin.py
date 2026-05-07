from django.contrib import admin

from .models import RewardClaim, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "reward_member_id", "total_xp", "level", "streak_count", "wallet_balance")
    search_fields = ("user__username", "user__email")


@admin.register(RewardClaim)
class RewardClaimAdmin(admin.ModelAdmin):
    list_display = ("user", "reward_preference", "reward_level", "partner_name", "created_at")
    search_fields = ("user__username", "user__email", "partner_name")
