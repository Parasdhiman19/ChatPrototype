import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from . models import Message
from .services import get_message_history , save_message_to_db , get_active_chat_users


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.me = self.scope['user']

        if self.me.is_anonymous :
            await self.close()
            return
        
        self.partner_id = int(self.scope['url_route']['kwargs']['partner_id'])
        sorted_ids = sorted([self.me.id, self.partner_id])
        self.room_group_name  = f"chat_{sorted_ids[0]}_{sorted_ids[1]}"

        await self.channel_layer.group_add(self.room_group_name , self.channel_name)
        await self.accept()


        old_messages = await get_message_history(self.me.id, self.partner_id)

        await self.send(text_data=json.dumps({
            'type': 'history',
            'messages': old_messages
        }))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_text = text_data_json["message"]

        # Call the external function from services.py
        await save_message_to_db(self.me, self.partner_id, message_text)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message_text,
                "sender": self.me.username
            },
        )
        await self.channel_layer.group_send(
        f"user_{self.partner_id}",
        {
         "type": "other_users",
        }
        )
    

    async def chat_message(self , event):
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message' : event['message'],
            'sender' : event['sender']
        }))


class HomeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']

        if self.user.is_anonymous :
            await self.close()
            return
        
        self.user_group = f'user_{self.user.id}'

        await self.channel_layer.group_add(
            self.user_group ,
            self.channel_name
        )

        await self.accept()

        users = await get_active_chat_users(self.user)
        await self.send(text_data=json.dumps({
        "type": "sidebar_update",
        "users": users,
    }))


        await self.channel_layer.group_add(
            self.user_group ,
            self.channel_name
        )
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group,
            self.channel_name
        )
    

    async def other_users(self, event):
     users = await get_active_chat_users(self.scope["user"])
 
     await self.send(text_data=json.dumps({
        "type": "sidebar_update",
        "users": users,
    }))
