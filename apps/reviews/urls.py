from django.urls import path
from. import views

app_name = 'reviews'

urlpatterns = [
    path('create/<int:booking_id>/', views.create_review, name='create_review'),
    path('update/<int:review_id>/', views.update_review, name='update_review'),
    path('detail/<int:review_id>/', views.review_detail, name='review_detail'),
]