from django.contrib import admin

from apps.tours.models import Tour, TourDate, TourImage, TourCategory

# Register your models here.
admin.site.register(Tour)
admin.site.register(TourDate)
admin.site.register(TourImage)
admin.site.register(TourCategory)