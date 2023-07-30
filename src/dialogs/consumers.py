import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from .models import Message, Chat

def format_datetime(dt):
    month_name = dt.strftime('%B')
    day = dt.strftime('%d')
    year = dt.strftime('%Y')
    hours = dt.strftime('%I')
    minutes = dt.strftime('%M')
    meridiem = dt.strftime('%p').lower()
    
    formatted_date = f"{month_name} {day}, {year}, {hours}:{minutes} {meridiem}."
    
    return formatted_date


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_name = self.scope['url_route']['kwargs']['chat_name']
        self.chat_group_name = 'char_%s' % self.chat_name

        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        action = data.get('action')
        message_id = data.get('message_id')
        message = data.get('message')
        username = data.get('username')
        chat = data.get('chat')
        message_date = data.get('message_date')

        if action == 'create':
            message_pk, message_date = await self.save_message(username, chat, message)

            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'chat_message',
                    'action': 'create',
                    'message': message,
                    'username': username,
                    'chat': chat,
                    'message_id': message_pk,
                    'message_date': format_datetime(message_date)
                }
            )
        
        elif action == 'update':
            await self.update_message(message_id, message)
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'chat_message',
                    'action': 'update',
                    'message_id': message_id,
                    'message': message,
                    'username': username,
                    'message_date': message_date
                }
            )

        elif action == 'delete':
            await self.delete_message(message_id)
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'chat_message',
                    'action': 'delete',
                    'message_id': message_id
                }
            )

    async def chat_message(self, event):
        action = event.get('action')
        message = event.get('message')
        username = event.get('username')
        chat = event.get('chat')
        message_id = event.get('message_id')
        message_date = event.get('message_date')

        await self.send(text_data=json.dumps({
            'action': action,
            'message_id': message_id,
            'message': message,
            'username': username,
            'chat': chat,
            'message_date': message_date
        }))

    @sync_to_async
    def save_message(self, username, chat, message):
        user = User.objects.get(username=username)
        chat = Chat.objects.get(pk=chat)
        new_message = Message.objects.create(user=user, chat=chat, text=message)
        chat.last_message = new_message
        chat.save()
        return new_message.pk, new_message.date

    @sync_to_async
    def update_message(self, message_id, message):
        message_obj = Message.objects.get(pk=message_id)
        message_obj.text = message
        message_obj.is_edited = True
        message_obj.save()

    @sync_to_async
    def delete_message(self, message_id):
        Message.objects.filter(pk=message_id).delete()
