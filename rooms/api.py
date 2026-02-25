from __future__ import annotations

from datetime import date
from typing import Any

from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema, extend_schema_view
from django.db.models import QuerySet
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from .models import Room
from .serializers import RoomSerializer
from bookings.models import BookingStatus


@extend_schema_view(
    list=extend_schema(
        auth=[],
        parameters=[
            OpenApiParameter(
                name="price_min",
                type=OpenApiTypes.DECIMAL,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Minimum price per night.",
            ),
            OpenApiParameter(
                name="price_max",
                type=OpenApiTypes.DECIMAL,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Maximum price per night.",
            ),
            OpenApiParameter(
                name="capacity_min",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Minimum capacity (number of guests).",
            ),
            OpenApiParameter(
                name="capacity_max",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Maximum capacity (number of guests).",
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "Sort results by a field. Allowed: name, price_per_night, capacity. "
                    "Prefix with '-' for descending (e.g. -price_per_night)."
                ),
            ),
        ],
    ),
    retrieve=extend_schema(auth=[]),
)
class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["price_per_night", "capacity", "name"]
    ordering = ["name"]

    def get_queryset(self) -> QuerySet[Room]:
        qs = super().get_queryset()
        params = self.request.query_params

        price_min = params.get("price_min")
        price_max = params.get("price_max")
        capacity_min = params.get("capacity_min")
        capacity_max = params.get("capacity_max")

        if price_min:
            qs = qs.filter(price_per_night__gte=price_min)
        if price_max:
            qs = qs.filter(price_per_night__lte=price_max)
        if capacity_min:
            qs = qs.filter(capacity__gte=capacity_min)
        if capacity_max:
            qs = qs.filter(capacity__lte=capacity_max)

        return qs

    def get_permissions(self):
        # Anyone can read rooms (including availability search);
        # only admin/staff can create/update/delete.
        if self.action in {"list", "retrieve", "available"}:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    @extend_schema(
        auth=[],
        parameters=[
            OpenApiParameter(
                name="start",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Start date (YYYY-MM-DD).",
            ),
            OpenApiParameter(
                name="end",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=True,
                description="End date (YYYY-MM-DD). Must be after start.",
            ),
        ],
        responses={200: RoomSerializer(many=True)},
    )
    @action(detail=False, methods=["get"], permission_classes=[permissions.AllowAny])
    def available(self, request, *args: Any, **kwargs: Any):
        start = request.query_params.get("start")
        end = request.query_params.get("end")

        try:
            start_date = date.fromisoformat(start) if start else None
            end_date = date.fromisoformat(end) if end else None
        except ValueError:
            return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        if not start_date or not end_date or start_date >= end_date:
            return Response({"detail": "Provide start/end with start < end."}, status=400)

        qs = (
            self.get_queryset()
            .exclude(
                bookings__status=BookingStatus.CONFIRMED,
                bookings__start_date__lt=end_date,
                bookings__end_date__gt=start_date,
            )
            .distinct()
        )

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
