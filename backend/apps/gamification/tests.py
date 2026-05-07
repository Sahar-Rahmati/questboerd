from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.activities.models import Activity
from apps.gamification.models import LevelHistory, StreakLog, WalletTransaction, XPTransaction
from apps.gamification.services import award_xp, calculate_level, evaluate_user_streak
from apps.tasks.models import Task

User = get_user_model()


class GamificationServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="gamer", password="strongpass123", email="gamer@example.com")
        self.activity = Activity.objects.create(
            title="Workout",
            description="",
            category="workout",
            difficulty="medium",
            estimated_duration_minutes=30,
            is_predefined=True,
        )

    def test_level_calculation(self):
        self.assertEqual(calculate_level(0), 1)
        self.assertEqual(calculate_level(500), 2)
        self.assertEqual(calculate_level(999), 2)

    def test_wallet_rewards_are_disabled(self):
        award_xp(user=self.user, amount=20000, transaction_type=XPTransaction.TransactionType.ADJUSTMENT, description="Admin adjustment")
        self.user.refresh_from_db()
        self.assertFalse(WalletTransaction.objects.filter(user=self.user).exists())
        self.assertEqual(self.user.profile.wallet_balance, 0)

    def test_level_history_prevents_duplicates(self):
        award_xp(user=self.user, amount=500, transaction_type=XPTransaction.TransactionType.ADJUSTMENT, description="Level up")
        award_xp(user=self.user, amount=0, transaction_type=XPTransaction.TransactionType.ADJUSTMENT, description="Duplicate check")
        self.assertEqual(LevelHistory.objects.filter(user=self.user, new_level=2).count(), 1)

    def test_streak_evaluation_is_disabled(self):
        Task.objects.create(
            user=self.user,
            activity=self.activity,
            title="Daily workout",
            description="",
            planned_date=date.today(),
            status=Task.Status.COMPLETED,
            ai_detected_category="workout",
            ai_detected_difficulty="medium",
            ai_estimated_duration_minutes=30,
            ai_multiplier=1.4,
        )
        log = evaluate_user_streak(user=self.user, target_date=date.today())
        self.assertIsNone(log)
        self.assertEqual(StreakLog.objects.filter(user=self.user).count(), 0)
