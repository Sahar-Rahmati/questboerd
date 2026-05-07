from rest_framework.views import APIView
from rest_framework.response import Response

from .services import get_weekly_report


class WeeklyReportView(APIView):
    def get(self, request):
        report = get_weekly_report(user=request.user)
        return Response(report)


class WeeklyXPChartView(APIView):
    def get(self, request):
        report = get_weekly_report(user=request.user)
        return Response(report["daily_xp_chart"])


class CategoryBreakdownView(APIView):
    def get(self, request):
        report = get_weekly_report(user=request.user)
        return Response(report["category_breakdown"])
