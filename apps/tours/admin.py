from django.contrib import admin

from apps.tours.models import Tour, TourDate, TourImage

# Register your models here.
admin.site.register(Tour)
admin.site.register(TourDate)
admin.site.register(TourImage)
