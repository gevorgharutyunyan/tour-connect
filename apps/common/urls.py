from django.urls import path
from .views import add_language, add_location

app_name = "common"

urlpatterns = [
    path('add-language/', add_language, name='add_language'),
    path('add-location/', add_location, name='add_location'),
]
