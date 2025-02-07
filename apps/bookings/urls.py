from django.urls import path
from. import views

app_name = 'bookings'

urlpatterns = [
    path('create/<int:tour_date_id>/', views.create_booking, name='create_booking'),
    path('detail/<int:booking_id>/', views.booking_detail, name='booking_detail'),

]