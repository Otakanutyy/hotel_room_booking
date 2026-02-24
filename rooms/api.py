from rest_framework import permissions, viewsets
from rest_framework.filters import OrderingFilter

from .models import Room
from .serializers import RoomSerializer


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["price_per_night", "capacity", "name"]
    ordering = ["name"]

    def get_permissions(self):
        # Anyone can read rooms; only admin/staff can create/update/delete.
        if self.action in {"list", "retrieve"}:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
