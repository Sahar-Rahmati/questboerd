from rest_framework.views import APIView
from rest_framework.response import Response

from .services import get_all_time_leaderboard, get_current_user_rank, get_weekly_leaderboard


class AllTimeLeaderboardView(APIView):
    def get(self, request):
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        return Response(get_all_time_leaderboard(page=page, page_size=page_size))


class WeeklyLeaderboardView(APIView):
    def get(self, request):
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        return Response(get_weekly_leaderboard(page=page, page_size=page_size))


class CurrentUserRankView(APIView):
    def get(self, request):
        return Response(get_current_user_rank(user=request.user))
