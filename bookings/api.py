from __future__ import annotations

from typing import Any

from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema, extend_schema_view
from django.db.models import QuerySet
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from .models import Booking
from .models import BookingStatus
from .serializers import BookingSerializer


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="(staff only) Filter bookings by user id.",
            ),
            OpenApiParameter(
                name="username",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="(staff only) Filter bookings by username (exact match).",
            ),
        ]
    )
)
class BookingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in {"update", "partial_update", "destroy"}:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self) -> QuerySet[Booking]:
        qs = Booking.objects.select_related("room", "user")
        user = self.request.user
        if user.is_staff:
            params = self.request.query_params
            user_id = params.get("user_id")
            username = params.get("username")

            if user_id:
                qs = qs.filter(user_id=user_id)
            if username:
                qs = qs.filter(user__username=username)

            return qs

        if user.id is None:
            return qs.none()
        return qs.filter(user_id=int(user.id))

    def perform_create(self, serializer: BaseSerializer) -> None:
        serializer.save(user=self.request.user)

    @extend_schema(
        request=None,
        responses={200: BookingSerializer},
        summary="Cancel booking",
        description="Cancels the booking. No request body is required.",
    )
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk: str | None = None, *args: Any, **kwargs: Any):
        booking = self.get_object()
        if booking.status != BookingStatus.CANCELED:
            booking.status = BookingStatus.CANCELED
            booking.save(update_fields=["status"])
        serializer = self.get_serializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)
