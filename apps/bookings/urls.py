from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('create/<int:tour_date_id>/', views.create_booking, name='create_booking'),
    path('list/', views.booking_list, name='booking_list'),
    path('<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
]