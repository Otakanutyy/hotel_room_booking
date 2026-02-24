from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
	list_display = ("room", "user", "start_date", "end_date", "status", "created_at")
	list_filter = ("status", "room", "start_date", "end_date")
	search_fields = ("room__name", "user__username", "user__email")
	date_hierarchy = "start_date"
	ordering = ("-created_at",)
