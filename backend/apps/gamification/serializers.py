from rest_framework import serializers

from apps.gamification.models import LevelHistory, StreakLog, WalletTransaction, XPTransaction
from apps.gamification.services import get_user_weekly_xp
from apps.users.serializers import UserProfileSerializer


class XPTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = XPTransaction
        fields = ["id", "amount", "transaction_type", "description", "created_at"]


class LevelHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelHistory
        fields = ["id", "old_level", "new_level", "reward_granted", "created_at"]


class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = ["id", "amount", "reason", "related_level", "created_at"]


class StreakLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreakLog
        fields = ["id", "date", "completed_all_tasks", "streak_after_evaluation", "bonus_xp_awarded", "created_at"]


class XPSummarySerializer(serializers.Serializer):
    profile = UserProfileSerializer()
    weekly_xp = serializers.IntegerField()

    @staticmethod
    def from_user(user):
        return {
            "profile": user.profile,
            "weekly_xp": get_user_weekly_xp(user),
        }
