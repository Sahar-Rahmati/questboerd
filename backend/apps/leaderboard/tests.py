from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.leaderboard.services import get_all_time_leaderboard

User = get_user_model()


class LeaderboardTests(TestCase):
    def test_leaderboard_orders_by_total_xp(self):
        low = User.objects.create_user(username="low", password="strongpass123")
        high = User.objects.create_user(username="high", password="strongpass123")
        low.profile.total_xp = 100
        low.profile.save()
        high.profile.total_xp = 500
        high.profile.save()
        results = get_all_time_leaderboard(page=1, page_size=10)["results"]
        self.assertEqual(results[0]["username"], "high")
