from django.urls import path

from .views import AllTimeLeaderboardView, CurrentUserRankView, WeeklyLeaderboardView

urlpatterns = [
    path("all-time/", AllTimeLeaderboardView.as_view(), name="all-time-leaderboard"),
    path("weekly/", WeeklyLeaderboardView.as_view(), name="weekly-leaderboard"),
    path("me/", CurrentUserRankView.as_view(), name="current-user-rank"),
]
