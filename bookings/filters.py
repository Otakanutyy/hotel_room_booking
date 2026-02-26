from __future__ import annotations

from django_filters import rest_framework as filters

from .models import Booking


class BookingFilter(filters.FilterSet):
    user_id = filters.NumberFilter(field_name="user_id")
    username = filters.CharFilter(field_name="user__username", lookup_expr="exact")

    class Meta:
        model = Booking
        fields: list[str] = []
