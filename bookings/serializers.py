from __future__ import annotations

from datetime import date
from typing import Any

from django.db import transaction
from rest_framework import serializers

from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["id", "room", "user", "start_date", "end_date", "status", "created_at"]
        read_only_fields = ["user", "created_at"]

    def get_fields(self) -> dict[str, serializers.Field]:
        fields = super().get_fields()
        request = self.context.get("request")
        user = getattr(request, "user", None)

        # Only staff can change booking status via PUT/PATCH.
        is_admin = bool(
            getattr(user, "is_staff", False) or getattr(user, "is_superuser", False)
        )
        if not is_admin:
            fields["status"].read_only = True

        return fields

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        request = self.context.get("request")

        existing = self.instance

        room = attrs.get("room", getattr(existing, "room", None))
        start_date = attrs.get("start_date", getattr(existing, "start_date", None))
        end_date = attrs.get("end_date", getattr(existing, "end_date", None))
        status = attrs.get("status", getattr(existing, "status", None))

        # For creates, force the booking user to be the requester.
        booking_user = getattr(existing, "user", None) or getattr(request, "user", None)

        if room is None or start_date is None or end_date is None or booking_user is None:
            raise serializers.ValidationError("room, start_date, end_date are required")

        # Narrow types for mypy/django-stubs.
        if not isinstance(start_date, date) or not isinstance(end_date, date):
            raise serializers.ValidationError("Invalid date format")

        instance = Booking(
            pk=getattr(existing, "pk", None),
            room=room,
            user=booking_user,
            start_date=start_date,
            end_date=end_date,
            status=status or Booking._meta.get_field("status").default,
        )

        # Runs model-level validation (date order check).
        # Overlap check is deferred to create/update inside a transaction.
        # Use clean() instead of full_clean() to avoid false unique-id
        # errors on updates when validating a temporary instance.
        instance.clean()
        return attrs

    def create(self, validated_data: dict[str, Any]) -> Booking:
        """Create booking inside a transaction with row-level locking."""
        with transaction.atomic():
            instance = Booking(**validated_data)
            instance.check_overlap()
            instance.save()
        return instance

    def update(self, instance: Booking, validated_data: dict[str, Any]) -> Booking:
        """Update booking inside a transaction with row-level locking."""
        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.check_overlap()
            instance.save()
        return instance
