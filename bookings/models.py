from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from rooms.models import Room


class BookingStatus(models.TextChoices):
	CONFIRMED = "confirmed", "Confirmed"
	CANCELED = "canceled", "Canceled"


class Booking(models.Model):
	room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")

	start_date = models.DateField()
	end_date = models.DateField()

	status = models.CharField(max_length=16, choices=BookingStatus.choices, default=BookingStatus.CONFIRMED)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		indexes = [
			models.Index(fields=["room", "start_date", "end_date", "status"]),
		]

	def clean(self):
		if self.start_date and self.end_date and self.start_date >= self.end_date:
			raise ValidationError("end_date must be after start_date")

		# Only confirmed bookings should block availability.
		if self.status != BookingStatus.CONFIRMED:
			return

		if not self.room_id or not self.start_date or not self.end_date:
			return

		overlaps = Booking.objects.filter(
			room_id=self.room_id,
			status=BookingStatus.CONFIRMED,
			start_date__lt=self.end_date,
			end_date__gt=self.start_date,
		).exclude(pk=self.pk)

		if overlaps.exists():
			raise ValidationError("Room is not available for this date range")

	def __str__(self) -> str:
		return f"{self.room} {self.start_date}→{self.end_date} ({self.status})"
