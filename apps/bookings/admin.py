from django.contrib import admin

from apps.bookings.models import Booking, Payment

# Register your models here.
admin.site.register(Booking)
admin.site.register(Payment)
