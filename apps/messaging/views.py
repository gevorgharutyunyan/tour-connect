from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from.models import Conversation, Message
from.forms import MessageForm

@login_required
def conversation_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, pk=conversation_id)
    messages = conversation.messages.all()
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            return redirect('messaging:conversation_view', conversation_id)
    else:
        form = MessageForm()
    return render(request, 'messaging/conversation.html', {'conversation': conversation, 'messages': messages, 'form': form})

@login_required
def create_conversation(request, user_id):  # user_id of the other participant
    try:
        conversation = Conversation.objects.get(participants=request.user, id=user_id)
    except Conversation.DoesNotExist:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, id=user_id)
        conversation.save()
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
