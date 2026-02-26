from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from config.permissions import IsStaffOrSuperuser

from .filters import BookingFilter
from .models import Booking
from .models import BookingStatus
from .serializers import BookingSerializer

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
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookingFilter

    def get_permissions(self):
        if self.action in {"update", "partial_update", "destroy"}:
            return [IsStaffOrSuperuser()]
        return super().get_permissions()

    def get_queryset(self) -> QuerySet[Booking]:
        qs = Booking.objects.select_related("room", "user")
        user = self.request.user
        if user.is_staff or user.is_superuser:
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
