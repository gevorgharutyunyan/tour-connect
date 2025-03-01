from django.urls import path
from. import views

app_name = 'bookings'

urlpatterns = [
    path('create/<int:tour_date_id>/', views.create_booking, name='create_booking'),
    path('detail/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('<int:booking_id>/confirm/', views.confirm_booking, name='confirm_booking'),
    path('<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('<int:booking_id>/complete/', views.complete_booking, name='complete_booking'),
    path('my_bookings/', views.BookingListView.as_view(), name='booking_list'),
    path('requests/', views.booking_requests, name='booking_requests'),
]