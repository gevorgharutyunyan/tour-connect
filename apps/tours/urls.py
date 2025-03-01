from django.urls import path
from . import views

app_name = "tours"

urlpatterns = [
    path('', views.TourListView.as_view(), name='tour-list'),
    path('search/', views.advanced_search, name='advanced-search'),
    path('create/', views.TourCreateView.as_view(), name='create-tour'),
    path('<int:pk>/', views.TourDetailView.as_view(), name='tour-detail'),
    path('<int:pk>/update/', views.TourUpdateView.as_view(), name='tour-update'),
    path('<int:pk>/delete/', views.TourDeleteView.as_view(), name='tour-delete'),
    path('<int:pk>/add-date/', views.TourDateCreateView.as_view(), name='add-date'),
    path('date/<int:pk>/update/', views.TourDateUpdateView.as_view(), name='update-date'),
    path('date/<int:pk>/delete/', views.TourDateDeleteView.as_view(), name='delete-date'),
    path('<int:pk>/add-image/', views.TourImageCreateView.as_view(), name='add-image'),
    path('image/<int:pk>/delete/', views.TourImageDeleteView.as_view(), name='delete-image'),
    
    # Advanced search related URLs
    path('save-filters/', views.save_search_filters, name='save-filters'),
    path('saved-filters/', views.get_saved_filters, name='saved-filters'),
    path('saved-filters/<int:filter_id>/delete/', views.delete_saved_filter, name='delete-saved-filter'),
    path('<int:tour_id>/toggle-favorite/', views.toggle_favorite, name='toggle-favorite'),
]
