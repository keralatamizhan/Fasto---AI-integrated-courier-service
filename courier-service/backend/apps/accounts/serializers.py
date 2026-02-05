from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name", "phone", "address"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        # Username is required by AbstractUser; allow using email as fallback
        if not validated_data.get("username") and validated_data.get("email"):
            validated_data["username"] = validated_data["email"]
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        password = attrs.get("password")
        username = attrs.get("username") or ""
        email = attrs.get("email") or ""

        # Allow login by email or username
        if not username and email:
            try:
                username = User.objects.get(email__iexact=email).username
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid credentials.")

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        attrs["user"] = user
        return attrs
