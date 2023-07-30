from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import ChatsView, ChatView, open_image_message


urlpatterns = [
    path('', login_required(ChatsView.as_view()), name='chats'),
    path('<int:pk>', login_required(ChatView.as_view()), name='chat'),
    path('open_image_message/<int:message_id>/', open_image_message, name='open_image_message'),
]
