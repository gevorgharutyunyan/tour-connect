from django.urls import path
from .views import *

app_name = "tours"

urlpatterns = [
    path('', TourListView.as_view(), name='tour-list'),
    path('<int:pk>/', TourDetailView.as_view(), name='tour-detail'),
    path('create/', TourCreateView.as_view(), name='create_tour'),
    path('<int:pk>/edit/', TourUpdateView.as_view(), name='tour-edit'),
    path('<int:pk>/delete/', TourDeleteView.as_view(), name='tour-delete'),

    path('tours/<int:tour_id>/dates/add/', TourDateCreateView.as_view(), name='tourdate-add'),
    path('dates/<int:pk>/edit/', TourDateUpdateView.as_view(), name='tourdate-edit'),
    path('dates/<int:pk>/delete/', TourDateDeleteView.as_view(), name='tourdate-delete'),

    path('tours/<int:tour_id>/images/add/', TourImageCreateView.as_view(), name='tourimage-add'),
    path('images/<int:pk>/edit/', TourImageUpdateView.as_view(), name='tourimage-edit'),
    path('images/<int:pk>/delete/', TourImageDeleteView.as_view(), name='tourimage-delete'),
]
