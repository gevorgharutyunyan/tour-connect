from django.urls import path
from. import views

app_name = 'messaging'

urlpatterns = [
    path('conversation/<int:conversation_id>/', views.conversation_view, name='conversation_view'),
    path('create/<int:user_id>/', views.create_conversation, name='create_conversation'),
    path('inbox/', views.inbox_view, name='inbox'),
]