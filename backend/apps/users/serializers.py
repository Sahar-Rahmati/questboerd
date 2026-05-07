from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from rest_framework import exceptions
from rest_framework import serializers
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import UserProfile
from .services import get_reward_progress, register_user, reset_password, send_password_reset_email

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    wallet_card_masked = serializers.SerializerMethodField()
    reward_preference_label = serializers.CharField(source="get_reward_preference_display", read_only=True)
    reward_claims_count = serializers.SerializerMethodField()
    reward_current_target_level = serializers.SerializerMethodField()
    reward_current_target_xp = serializers.SerializerMethodField()
    reward_xp_remaining = serializers.SerializerMethodField()
    reward_levels_remaining = serializers.SerializerMethodField()
    reward_can_claim = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "total_xp",
            "level",
            "streak_count",
            "wallet_balance",
            "wallet_cardholder_name",
            "wallet_card_brand",
            "wallet_card_last4",
            "wallet_card_masked",
            "wallet_card_expiry_month",
            "wallet_card_expiry_year",
            "apple_pay_enabled",
            "samsung_pay_enabled",
            "wallet_permissions_granted",
            "reward_preference",
            "reward_preference_label",
            "reward_member_id",
            "reward_claims_count",
            "reward_current_target_level",
            "reward_current_target_xp",
            "reward_xp_remaining",
            "reward_levels_remaining",
            "reward_can_claim",
            "created_at",
            "updated_at",
        ]

    def get_wallet_card_masked(self, obj):
        if not obj.wallet_card_last4:
            return ""
        return f"**** **** **** {obj.wallet_card_last4}"

    def _get_reward_progress(self, obj):
        if not hasattr(obj, "_reward_progress_cache"):
            obj._reward_progress_cache = get_reward_progress(profile=obj)
        return obj._reward_progress_cache

    def get_reward_claims_count(self, obj):
        return self._get_reward_progress(obj)["reward_claims_count"]

    def get_reward_current_target_level(self, obj):
        return self._get_reward_progress(obj)["reward_current_target_level"]

    def get_reward_current_target_xp(self, obj):
        return self._get_reward_progress(obj)["reward_current_target_xp"]

    def get_reward_xp_remaining(self, obj):
        return self._get_reward_progress(obj)["reward_xp_remaining"]

    def get_reward_levels_remaining(self, obj):
        return self._get_reward_progress(obj)["reward_levels_remaining"]

    def get_reward_can_claim(self, obj):
        return self._get_reward_progress(obj)["reward_can_claim"]


class WalletSettingsSerializer(serializers.ModelSerializer):
    wallet_card_number = serializers.CharField(write_only=True, required=False, allow_blank=True, max_length=32)

    class Meta:
        model = UserProfile
        fields = [
            "wallet_cardholder_name",
            "wallet_card_number",
            "wallet_card_expiry_month",
            "wallet_card_expiry_year",
            "apple_pay_enabled",
            "samsung_pay_enabled",
            "wallet_permissions_granted",
            "reward_preference",
        ]

    def validate_wallet_card_number(self, value: str) -> str:
        digits = "".join(character for character in value if character.isdigit())
        if value and len(digits) < 12:
            raise serializers.ValidationError("Enter a valid card number.")
        return digits

    def validate_wallet_card_expiry_month(self, value: int | None) -> int | None:
        if value is not None and not 1 <= value <= 12:
            raise serializers.ValidationError("Expiry month must be between 1 and 12.")
        return value

    def detect_card_brand(self, digits: str) -> str:
        if digits.startswith("4"):
            return "Visa"
        if digits[:2] in {"51", "52", "53", "54", "55"} or 2221 <= int(digits[:4] or 0) <= 2720:
            return "Mastercard"
        if digits[:2] in {"34", "37"}:
            return "American Express"
        return "Card"

    def update(self, instance, validated_data):
        card_number = validated_data.pop("wallet_card_number", "")
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if card_number:
            instance.wallet_card_last4 = card_number[-4:]
            instance.wallet_card_brand = self.detect_card_brand(card_number)
        instance.save()
        return instance


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value

    def validate_username(self, value: str) -> str:
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username is already registered.")
        return value

    def create(self, validated_data):
        return register_user(**validated_data)


class RewardClaimSerializer(serializers.Serializer):
    reward_level = serializers.IntegerField()
    reward_title = serializers.CharField()
    partner_name = serializers.CharField()
    instructions = serializers.CharField()
    reward_member_id = serializers.CharField()


class LoginSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

    default_error_messages = {
        "invalid_credentials": "Invalid email or password.",
        "missing_email": "Enter the email address for your account.",
    }

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        return token

    def validate(self, attrs):
        email = (attrs.get("email") or "").strip().lower()
        password = attrs.get("password") or ""

        if not email:
            raise exceptions.AuthenticationFailed(self.error_messages["missing_email"], code="missing_email")

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed(
                self.error_messages["invalid_credentials"],
                code="invalid_credentials",
            ) from exc

        if not user.check_password(password) or not user.is_active:
            raise exceptions.AuthenticationFailed(
                self.error_messages["invalid_credentials"],
                code="invalid_credentials",
            )

        refresh = self.get_token(user)
        data = {"refresh": str(refresh), "access": str(refresh.access_token)}

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, user)

        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def save(self, **kwargs):
        try:
            user = User.objects.get(email__iexact=self.validated_data["email"])
        except User.DoesNotExist:
            return
        send_password_reset_email(user=user)


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)

    def save(self, **kwargs):
        try:
            return reset_password(**self.validated_data)
        except (User.DoesNotExist, ValueError) as exc:
            raise serializers.ValidationError({"token": str(exc)}) from exc


class CredentialsSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            user = User.objects.get(email__iexact=attrs["email"])
        except User.DoesNotExist as exc:
            raise serializers.ValidationError("Invalid credentials.") from exc
        if not user.check_password(attrs["password"]):
            raise serializers.ValidationError("Invalid credentials.")
        attrs["user"] = user
        return attrs
