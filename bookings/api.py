from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Booking
from .models import BookingStatus
from .serializers import BookingSerializer


class BookingViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Booking.objects.select_related("room", "user")
        user = self.request.user
        if user.is_staff:
            return qs
        return qs.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status != BookingStatus.CANCELED:
            booking.status = BookingStatus.CANCELED
            booking.save(update_fields=["status"])
        serializer = self.get_serializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)
