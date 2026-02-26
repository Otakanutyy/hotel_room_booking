from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import status
from rest_framework import serializers
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    def validate_username(self, value: str) -> str:
        username = value.strip()
        if not username:
            raise serializers.ValidationError("username and password are required")

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("username already exists")

        return username

    def create(self, validated_data: dict[str, Any]):
        User = get_user_model()
        try:
            with transaction.atomic():
                return User.objects.create_user(
                    username=validated_data["username"],
                    email=(validated_data.get("email") or "").strip(),
                    password=validated_data["password"],
                )
        except IntegrityError:
            raise serializers.ValidationError({"username": "username already exists"})


class RegisterView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @extend_schema(
        auth=[],
        request=RegisterSerializer,
        responses={
            201: inline_serializer(
                name="RegisterResponse",
                fields={
                    "id": serializers.IntegerField(),
                    "username": serializers.CharField(),
                    "access": serializers.CharField(),
                    "refresh": serializers.CharField(),
                },
            )
        },
    )
    def post(self, request, *args: Any, **kwargs: Any):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )
