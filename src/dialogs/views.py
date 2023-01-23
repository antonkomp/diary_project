from django.shortcuts import render, redirect
from accounts.models import PageView, Profile
from .models import Message, Chat
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User


def entrance_url(url):
    entrance = PageView.objects.filter(url=url)
    entrance.update(views=F('views') + 1)


@login_required
def chats(request):
    """
    Show user chats.
    """
    PageView.objects.get_or_create(url='chats')
    entrance_url('chats')
    profile_image = Profile.objects.filter(user_id=request.user.id).first()
    my_chats = Chat.objects.filter(members__in=[request.user.id])
    return render(request, 'chats.html', {'profile': profile_image, 'chats': my_chats})


@login_required
def chat(request, slug):
    my_chat = Chat.objects.get(slug=slug)
    my_chats = Chat.objects.filter(members__in=[request.user.id])
    profile_image = Profile.objects.filter(user_id=request.user.id).first()
    my_messages = Message.objects.filter(chat=my_chat)[0:25]
    return render(request, 'chat.html', {
        'profile': profile_image,
        'chat': my_chat,
        'chats': my_chats,
        'messages': my_messages
    })


@login_required
def open_image_message(request, message_id):
    mess = Message.objects.filter(id=message_id).first()
    if mess.recipient != str(request.user):
        context = {'form': AuthenticationForm()}
        return render(request, 'login.html', context)
    context = {'message': mess}
    return render(request, 'open_image_message.html', context)


@login_required
def delete_message(request, message_id):
    mess = Message.objects.filter(id=message_id).first()
    if mess.recipient != str(request.user):
        context = {'form': AuthenticationForm()}
        return render(request, 'login.html', context)
    if request.method == 'POST':
        mess = Message.objects.filter(id=message_id).first()
        mess.delete()
        messages.success(request, 'Message deleted.')
        return redirect('my_messages')
