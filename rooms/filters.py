from __future__ import annotations

from django_filters import rest_framework as filters

from .models import Room


class RoomFilter(filters.FilterSet):
    price_min = filters.NumberFilter(field_name="price_per_night", lookup_expr="gte")
    price_max = filters.NumberFilter(field_name="price_per_night", lookup_expr="lte")
    capacity_min = filters.NumberFilter(field_name="capacity", lookup_expr="gte")
    capacity_max = filters.NumberFilter(field_name="capacity", lookup_expr="lte")

    class Meta:
        model = Room
        fields: list[str] = []
