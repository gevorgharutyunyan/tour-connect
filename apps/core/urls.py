from django.urls import path
from. import views

urlpatterns = [
    path('', views.home, name='home'),  # Your landing page URL
    path('add_to_wishlist/<int:tour_id>/', views.add_to_wishlist, name='add_to_wishlist'),
]