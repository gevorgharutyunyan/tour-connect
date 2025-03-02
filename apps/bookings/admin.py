from django.contrib import admin
from apps.bookings.models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'tourist', 'tour_date', 'number_of_participants', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('tourist__email', 'tour_date__tour__title')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('tourist', 'tour_date')
