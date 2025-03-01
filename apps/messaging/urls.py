from django.urls import path
from. import views

app_name = 'messaging'

urlpatterns = [
    path('conversation/<int:conversation_id>/', views.conversation_view, name='conversation_view'),
    path('create/<int:user_id>/', views.create_conversation, name='create_conversation'),
    path('inbox/', views.inbox_view, name='inbox'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/count/', views.notification_count, name='notification_count'),
]