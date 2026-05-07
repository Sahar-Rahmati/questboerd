from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import (
    LoginSerializer,
    LogoutSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    RewardClaimSerializer,
    UserProfileSerializer,
    WalletSettingsSerializer,
)
from .services import claim_current_reward


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "auth"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserProfileSerializer(user.profile).data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer
    throttle_scope = "auth"
    throttle_classes = [ScopedRateThrottle]


class RefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = RefreshToken(serializer.validated_data["refresh"])
        token.blacklist()
        return Response(status=status.HTTP_205_RESET_CONTENT)


class ProfileView(APIView):
    def get(self, request):
        return Response(UserProfileSerializer(request.user.profile).data)

    def patch(self, request):
        serializer = WalletSettingsSerializer(request.user.profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        return Response(UserProfileSerializer(profile).data)


class RewardClaimView(APIView):
    def post(self, request):
        try:
            claim = claim_current_reward(user=request.user)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        payload = RewardClaimSerializer(
            {
                "reward_level": claim.reward_level,
                "reward_title": claim.reward_title,
                "partner_name": claim.partner_name,
                "instructions": claim.instructions,
                "reward_member_id": request.user.profile.reward_member_id,
            }
        ).data
        return Response(payload, status=status.HTTP_201_CREATED)


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "auth"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "If the account exists, a reset email was sent."})


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password reset successfully."})
