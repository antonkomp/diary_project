from django.urls import path
from django.conf.urls import url
from .views import chats, chat, delete_message, open_image_message


urlpatterns = [
    path('', chats, name='chats'),
    path('<slug:slug>', chat, name='chat'),
    path('delete_message/<int:message_id>/', delete_message, name='delete_message'),
    path('open_image_message/<int:message_id>/', open_image_message, name='open_image_message'),
]


