from django.contrib import admin

from apps.reviews.models import Review, ReviewPhoto, Wishlist

admin.site.register(Review)
admin.site.register(ReviewPhoto)
admin.site.register(Wishlist)