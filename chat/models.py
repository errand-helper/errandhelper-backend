from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class ChatRoom(models.Model):
    """Represents a chat room that can be private or group"""
    ROOM_TYPE_CHOICES = [
        ('private', 'Private'),
        ('group', 'Group'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)  # For group chats
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES, default='private')
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # For private chats, we'll store the room name as user1_id-user2_id
    # For group chats, we'll use a custom name
    
    class Meta:
        ordering = ['-updated_at']
        
    def __str__(self):
        if self.room_type == 'private':
            participants = self.participants.all()
            if participants.count() == 2:
                return f"Private chat: {participants[0].email} - {participants[1].email}"
            return f"Private chat: {self.id}"
        return self.name or f"Group chat: {self.id}"
    
    @classmethod
    def get_or_create_private_room(cls, user1, user2):
        """Get or create a private chat room between two users"""
        # Sort users by ID to ensure consistent room identification
        users = sorted([user1, user2], key=lambda u: str(u.id))
        
        # Try to find existing room
        existing_room = cls.objects.filter(
            room_type='private',
            participants=users[0]
        ).filter(participants=users[1]).first()
        
        if existing_room:
            return existing_room, False
        
        # Create new room
        room = cls.objects.create(room_type='private')
        room.participants.set(users)
        return room, True
    
    def get_room_name(self):
        """Get the WebSocket room name for this chat room"""
        return f"chat_{self.id}"
    
    def get_last_message(self):
        """Get the last message in this room"""
        return self.messages.order_by('-created_at').first()


class Message(models.Model):
    """Represents a message in a chat room"""
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default='text')
    file_url = models.URLField(blank=True, null=True)  # For file/image messages
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Message status tracking
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['created_at']
        
    def __str__(self):
        return f"{self.sender.email}: {self.content[:50]}..."
    
    def mark_as_edited(self):
        """Mark this message as edited"""
        from django.utils import timezone
        self.is_edited = True
        self.edited_at = timezone.now()
        self.save()


class MessageStatus(models.Model):
    """Tracks delivery and read status of messages for each user"""
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
    ]
    
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='statuses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['message', 'user']
        
    def __str__(self):
        return f"{self.message.id} - {self.user.email}: {self.status}"


class TypingIndicator(models.Model):
    """Tracks who is currently typing in a room"""
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='typing_indicators')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_typing = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['room', 'user']
        
    def __str__(self):
        return f"{self.user.email} typing in {self.room.get_room_name()}"


class ChatRoomMembership(models.Model):
    """Tracks user membership in chat rooms with additional metadata"""
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('admin', 'Admin'),
        ('owner', 'Owner'),
    ]
    
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='room_memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    last_read_message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        unique_together = ['room', 'user']
        
    def __str__(self):
        return f"{self.user.email} - {self.room} ({self.role})"
    
    def get_unread_count(self):
        """Get the number of unread messages for this user in this room"""
        if not self.last_read_message:
            return self.room.messages.count()
        
        return self.room.messages.filter(
            created_at__gt=self.last_read_message.created_at
        ).count()
