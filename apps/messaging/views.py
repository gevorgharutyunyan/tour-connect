from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from.models import Conversation, Message, Notification
from.forms import MessageForm
from .utils import create_message_notification
from django.http import JsonResponse
from django.utils import timezone

@login_required
def conversation_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, pk=conversation_id)
    chat_messages = conversation.messages.all()
    other_user = conversation.participants.exclude(id=request.user.id).first()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            
            # Create notification for the new message
            create_message_notification(message)
            
            return redirect('messaging:conversation_view', conversation_id)
    else:
        form = MessageForm()

    return render(request, 'messaging/conversation.html', {
        'conversation': conversation,
        'chat_messages': chat_messages,
        'form': form,
        'other_user': other_user
    })



@login_required
def create_conversation(request, user_id):  # user_id of the other participant
    conversation = Conversation.objects.filter(participants=request.user).filter(participants=user_id).first()
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, user_id)
    return redirect('messaging:conversation_view', conversation.id)


@login_required
def inbox_view(request):
    conversations = Conversation.objects.filter(participants=request.user).order_by('-updated_at')
    conversation_data =[] # Prepare data for the template

    for conversation in conversations:
        other_user = conversation.participants.exclude(id=request.user.id).first()
        conversation_data.append({
            'conversation': conversation,
            'other_user_username': other_user.username if other_user else None,  # Handle potential None
            'last_message': conversation.last_message
        })

    return render(request, 'messaging/inbox.html', {'conversation_data': conversation_data})

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')
    
    return render(request, 'messaging/notifications.html', {
        'notifications': notifications
    })

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('messaging:notifications')

@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('messaging:notifications')

@login_required
def notification_count(request):
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    return JsonResponse({'count': count})
