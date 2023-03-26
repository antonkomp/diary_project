from django.shortcuts import render, redirect
from accounts.models import PageView, Profile
from django.views import View
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from .models import Message, Chat
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User


def entrance_url(url):
    entrance = PageView.objects.filter(url=url)
    entrance.update(views=F('views') + 1)


class ChatsView(View):
    """
    Show user chats.
    """
    def get(self, request):
        PageView.objects.get_or_create(url='chats')
        entrance_url('chats')
        profile_image = Profile.objects.filter(user_id=request.user.id).first()
        my_chats = Chat.objects.filter(members__in=[request.user.id])
        return render(request, 'chats.html', {
            'profile': profile_image,
            'user_profile': request.user,
            'chats': my_chats
        })


class ChatView(View):
    def get(self, request, pk):
        my_chat = Chat.objects.get(pk=pk)
        profile_image = Profile.objects.filter(user_id=request.user.id).first()
        my_messages = Message.objects.filter(chat=my_chat)
        return render(request, 'chat.html', {
            'profile': profile_image,
            'chat': my_chat,
            'messages': my_messages
        })


class MessageDelete(DeleteView):
    model = Message

    # Не лучшее решение, в будущем лучше работать с формой и JS
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('chat', kwargs={'pk': self.object.chat.pk})


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
