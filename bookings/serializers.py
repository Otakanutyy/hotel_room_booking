from rest_framework import serializers

from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["id", "room", "user", "start_date", "end_date", "status", "created_at"]
        read_only_fields = ["user", "status", "created_at"]

    def validate(self, attrs):
        request = self.context.get("request")

        instance = Booking(
            room=attrs.get("room"),
            user=getattr(request, "user", None),
            start_date=attrs.get("start_date"),
            end_date=attrs.get("end_date"),
        )

        # Runs model-level validation (date order + overlap check)
        instance.full_clean()
        return attrs
