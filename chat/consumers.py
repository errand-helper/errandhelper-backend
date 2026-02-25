import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone

# Defer model imports to avoid Django app loading issues
def get_models():
    from .models import ChatRoom, Message, MessageStatus, TypingIndicator
    return ChatRoom, Message, MessageStatus, TypingIndicator

def get_user_model_instance():
    return get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # Get user from scope
        self.user = self.scope["user"]
        
        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Check if user has access to this room
        if not await self.user_has_access_to_room(self.user, self.room_id):
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(# type:ignore
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send user online status
        await self.channel_layer.group_send(# type:ignore
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': str(self.user.id),
                'status': 'online'
            }
        )
    
    async def disconnect(self, close_code):
        # Remove typing indicator if exists
        if hasattr(self, 'user') and self.user.is_authenticated:
            await self.remove_typing_indicator(self.user, self.room_id)
            
            # Send user offline status
            await self.channel_layer.group_send(# type:ignore
                self.room_group_name,
                {
                    'type': 'user_status',
                    'user_id': str(self.user.id),
                    'status': 'offline'
                }
            )
        
        # Leave room group
        await self.channel_layer.group_discard(# type:ignore
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'chat_message':
            await self.handle_chat_message(text_data_json)
        elif message_type == 'typing_start':
            await self.handle_typing_start()
        elif message_type == 'typing_stop':
            await self.handle_typing_stop()
        elif message_type == 'mark_as_read':
            await self.handle_mark_as_read(text_data_json)
        elif message_type == 'edit_message':
            await self.handle_edit_message(text_data_json)
    
    async def handle_chat_message(self, data):
        message_content = data['message']
        message_type = data.get('message_type', 'text')
        file_url = data.get('file_url')
        
        # Save message to database
        message = await self.save_message(
            self.user, 
            self.room_id, 
            message_content, 
            message_type, 
            file_url
        )
        
        # Create message status for all participants
        await self.create_message_statuses(message)
        
        # Send message to room group
        await self.channel_layer.group_send(# type:ignore
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': str(message.id),
                    'content': message.content,
                    'message_type': message.message_type,
                    'file_url': message.file_url,
                    'sender': {
                        'id': str(message.sender.id),
                        'email': message.sender.email,
                        'first_name': message.sender.first_name,
                        'last_name': message.sender.last_name
                    },
                    'created_at': message.created_at.isoformat(),
                    'is_edited': message.is_edited,
                    'edited_at': message.edited_at.isoformat() if message.edited_at else None
                }
            }
        )
        
        # Update room's last activity
        await self.update_room_activity(self.room_id)
    
    async def handle_typing_start(self):
        await self.set_typing_indicator(self.user, self.room_id, True)
        
        # Send typing indicator to room group (except sender)
        await self.channel_layer.group_send(# type:ignore
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': str(self.user.id),
                'user_email': self.user.email,
                'is_typing': True
            }
        )
    
    async def handle_typing_stop(self):
        await self.set_typing_indicator(self.user, self.room_id, False)
        
        # Send typing indicator to room group (except sender)
        await self.channel_layer.group_send(# type:ignore
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': str(self.user.id),
                'user_email': self.user.email,
                'is_typing': False
            }
        )
    
    async def handle_mark_as_read(self, data):
        message_id = data.get('message_id')
        if message_id:
            await self.mark_message_as_read(message_id, self.user)
            
            # Send read receipt to room group
            await self.channel_layer.group_send(# type:ignore
                self.room_group_name,
                {
                    'type': 'read_receipt',
                    'message_id': message_id,
                    'user_id': str(self.user.id),
                    'user_email': self.user.email
                }
            )
    
    async def handle_edit_message(self, data):
        message_id = data.get('message_id')
        new_content = data.get('new_content')
        
        if message_id and new_content:
            message = await self.edit_message(message_id, new_content, self.user)
            if message:
                # Send edited message to room group
                await self.channel_layer.group_send(# type:ignore
                    self.room_group_name,
                    {
                        'type': 'message_edited',
                        'message': {
                            'id': str(message.id),
                            'content': message.content,
                            'is_edited': message.is_edited,
                            'edited_at': message.edited_at.isoformat() if message.edited_at else None
                        }
                    }
                )
    
    # WebSocket message handlers
    async def chat_message(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message
        }))
    
    async def typing_indicator(self, event):
        # Don't send typing indicator to the sender
        if event['user_id'] != str(self.user.id):
            await self.send(text_data=json.dumps({
                'type': 'typing_indicator',
                'user_id': event['user_id'],
                'user_email': event['user_email'],
                'is_typing': event['is_typing']
            }))
    
    async def read_receipt(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'user_email': event['user_email']
        }))
    
    async def message_edited(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_edited',
            'message': event['message']
        }))
    
    async def user_status(self, event):
        # Don't send user status to the user themselves
        if event['user_id'] != str(self.user.id):
            await self.send(text_data=json.dumps({
                'type': 'user_status',
                'user_id': event['user_id'],
                'status': event['status']
            }))
    
    # Database operations
    @database_sync_to_async
    def user_has_access_to_room(self, user, room_id):
        try:
            ChatRoom, _, _, _ = get_models()
            room = ChatRoom.objects.get(id=room_id)# type:ignore
            return room.participants.filter(id=user.id).exists()
        except ChatRoom.DoesNotExist:# type:ignore
            return False
    
    @database_sync_to_async
    def save_message(self, user, room_id, content, message_type, file_url):
        ChatRoom, Message, _, _ = get_models()
        room = ChatRoom.objects.get(id=room_id)# type:ignore
        message = Message.objects.create(# type:ignore
            room=room,
            sender=user,
            content=content,
            message_type=message_type,
            file_url=file_url
        )
        return message
    
    @database_sync_to_async
    def create_message_statuses(self, message):
        _, _, MessageStatus, _ = get_models()
        # Create status for all participants except sender
        participants = message.room.participants.exclude(id=message.sender.id)
        statuses = []
        for participant in participants:
            status = MessageStatus.objects.create(# type:ignore
                message=message,
                user=participant,
                status='delivered'
            )
            statuses.append(status)
        return statuses
    
    @database_sync_to_async
    def set_typing_indicator(self, user, room_id, is_typing):
        ChatRoom, _, _, TypingIndicator = get_models()
        room = ChatRoom.objects.get(id=room_id)# type:ignore
        indicator, created = TypingIndicator.objects.get_or_create(# type:ignore
            room=room,
            user=user,
            defaults={'is_typing': is_typing}
        )
        indicator.is_typing = is_typing
        indicator.save()
        return indicator
    
    @database_sync_to_async
    def remove_typing_indicator(self, user, room_id):
        try:
            ChatRoom, _, _, TypingIndicator = get_models()
            room = ChatRoom.objects.get(id=room_id)# type:ignore
            TypingIndicator.objects.filter(room=room, user=user).delete()# type:ignore
        except ChatRoom.DoesNotExist:# type:ignore
            pass
    
    @database_sync_to_async
    def mark_message_as_read(self, message_id, user):
        try:
            _, Message, MessageStatus, _ = get_models()
            message = Message.objects.get(id=message_id)# type:ignore
            status, created = MessageStatus.objects.get_or_create(# type:ignore
                message=message,
                user=user,
                defaults={'status': 'read'}
            )
            if not created:
                status.status = 'read'
                status.save()
            return status
        except Message.DoesNotExist:# type:ignore
            return None
    
    @database_sync_to_async
    def edit_message(self, message_id, new_content, user):
        try:
            _, Message, _, _ = get_models()
            message = Message.objects.get(id=message_id, sender=user)# type:ignore
            message.content = new_content
            message.mark_as_edited()
            return message
        except Message.DoesNotExist:# type:ignore
            return None
    
    @database_sync_to_async
    def update_room_activity(self, room_id):
        try:
            ChatRoom, _, _, _ = get_models()
            room = ChatRoom.objects.get(id=room_id)# type:ignore
            room.updated_at = timezone.now()
            room.save()
        except ChatRoom.DoesNotExist:# type:ignore
            pass
