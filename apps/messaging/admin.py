from django.contrib import admin
from apps.messaging.models import Message, Conversation, Notification
# Register your models here.
admin.site.register(Message)
admin.site.register(Conversation)
admin.site.register(Notification)