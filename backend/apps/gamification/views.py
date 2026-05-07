from rest_framework.views import APIView
from rest_framework.response import Response

from apps.gamification.models import LevelHistory, StreakLog, WalletTransaction, XPTransaction
from apps.gamification.services import get_user_weekly_xp
from apps.gamification.serializers import (
    LevelHistorySerializer,
    StreakLogSerializer,
    WalletTransactionSerializer,
    XPTransactionSerializer,
)
from apps.users.serializers import UserProfileSerializer


class XPSummaryView(APIView):
    def get(self, request):
        return Response(
            {
                "profile": UserProfileSerializer(request.user.profile).data,
                "weekly_xp": get_user_weekly_xp(request.user),
            }
        )


class XPTransactionHistoryView(APIView):
    def get(self, request):
        qs = XPTransaction.objects.filter(user=request.user)
        return Response(XPTransactionSerializer(qs[:50], many=True).data)


class LevelHistoryView(APIView):
    def get(self, request):
        qs = LevelHistory.objects.filter(user=request.user)
        return Response(LevelHistorySerializer(qs[:50], many=True).data)


class WalletTransactionView(APIView):
    def get(self, request):
        qs = WalletTransaction.objects.filter(user=request.user)
        return Response(WalletTransactionSerializer(qs[:50], many=True).data)


class StreakStatusView(APIView):
    def get(self, request):
        qs = StreakLog.objects.filter(user=request.user)
        return Response(StreakLogSerializer(qs[:30], many=True).data)
