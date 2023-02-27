from django.contrib.auth.decorators import login_required
from django.urls import path
from django.conf.urls import url
from .views import ChatsView, ChatView, MessageDelete, delete_message, open_image_message


urlpatterns = [
    path('', login_required(ChatsView.as_view()), name='chats'),
    path('<int:pk>', login_required(ChatView.as_view()), name='chat'),
    path('delete_message/<int:pk>/', login_required(MessageDelete.as_view()), name='delete_message'),
    path('open_image_message/<int:message_id>/', open_image_message, name='open_image_message'),
]


