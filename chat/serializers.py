from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message, MessageStatus, TypingIndicator, ChatRoomMembership

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user information in chat context"""
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'email', 'first_name', 'last_name']


class MessageStatusSerializer(serializers.ModelSerializer):
    """Serializer for message status"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = MessageStatus
        fields = ['user', 'status', 'timestamp']
        read_only_fields = ['user', 'status', 'timestamp']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages"""
    sender = UserSerializer(read_only=True)
    statuses = MessageStatusSerializer(many=True, read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'content', 'message_type', 'file_url', 'sender', 
            'created_at', 'updated_at', 'is_edited', 'edited_at', 'statuses'
        ]
        read_only_fields = [
            'id', 'sender', 'created_at', 'updated_at', 'is_edited', 'edited_at', 'statuses'
        ]
    
    def create(self, validated_data):
        """Create a new message"""
        validated_data['sender'] = self.context['request'].user
        validated_data['room'] = self.context['room']
        return super().create(validated_data)


class ChatRoomMembershipSerializer(serializers.ModelSerializer):
    """Serializer for chat room membership"""
    user = UserSerializer(read_only=True)
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoomMembership
        fields = ['user', 'role', 'joined_at', 'unread_count']
        read_only_fields = ['user', 'role', 'joined_at', 'unread_count']
    
    def get_unread_count(self, obj):
        """Get unread message count for this membership"""
        return obj.get_unread_count()


class ChatRoomSerializer(serializers.ModelSerializer):
    """Serializer for chat rooms"""
    participants = UserSerializer(many=True, read_only=True)
    last_message = MessageSerializer(read_only=True)
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'room_type', 'participants', 'created_at', 
            'updated_at', 'last_message', 'unread_count'
        ]
        read_only_fields = [
            'id', 'participants', 'created_at', 'updated_at', 'last_message', 'unread_count'
        ]
    
    def get_unread_count(self, obj):
        """Get unread message count for current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                membership = obj.memberships.get(user=request.user)
                return membership.get_unread_count()
            except ChatRoomMembership.DoesNotExist: # type:ignore
                return 0
        return 0
    
    def get_last_message(self, obj):
        """Get the last message in this room"""
        last_message = obj.get_last_message()
        if last_message:
            return MessageSerializer(last_message).data
        return None


class CreatePrivateRoomSerializer(serializers.Serializer):
    """Serializer for creating private chat rooms"""
    participant_id = serializers.UUIDField()
    
    def validate_participant_id(self, value):
        """Validate that the participant exists and is not the current user"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required")
        
        if str(request.user.id) == str(value):
            raise serializers.ValidationError("Cannot create room with yourself")
        
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        
        return value
    
    def create(self, validated_data):
        """Create or get private room"""
        request = self.context.get('request')
        participant = User.objects.get(id=validated_data['participant_id'])
        
        room, created = ChatRoom.get_or_create_private_room(request.user, participant) # type:ignore
        
        # Create memberships if room was created
        if created:
            ChatRoomMembership.objects.create(room=room, user=request.user, role='member') # type:ignore
            ChatRoomMembership.objects.create(room=room, user=participant, role='member') # type:ignore
        
        return room


class CreateGroupRoomSerializer(serializers.Serializer):
    """Serializer for creating group chat rooms"""
    name = serializers.CharField(max_length=255)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=50
    )
    
    def validate_participant_ids(self, value):
        """Validate that all participants exist"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required")
        
        # Check if all users exist
        existing_users = User.objects.filter(id__in=value)
        if existing_users.count() != len(value):
            raise serializers.ValidationError("Some participants not found")
        
        # Add current user to participants if not already included
        if str(request.user.id) not in [str(uid) for uid in value]:
            value.append(request.user.id)
        
        return value
    
    def create(self, validated_data):
        """Create group room"""
        request = self.context.get('request')
        
        # Create the room
        room = ChatRoom.objects.create(
            name=validated_data['name'],
            room_type='group'
        )
        
        # Add participants
        participants = User.objects.filter(id__in=validated_data['participant_ids'])
        room.participants.set(participants)
        
        # Create memberships
        for participant in participants:
            role = 'owner' if participant == request.user else 'member' # type:ignore
            ChatRoomMembership.objects.create( # type:ignore
                room=room,
                user=participant,
                role=role
            )
        
        return room


class TypingIndicatorSerializer(serializers.ModelSerializer):
    """Serializer for typing indicators"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = TypingIndicator
        fields = ['user', 'is_typing', 'timestamp']
        read_only_fields = ['user', 'is_typing', 'timestamp']


class MessageEditSerializer(serializers.Serializer):
    """Serializer for editing messages"""
    content = serializers.CharField()
    
    def validate_content(self, value):
        """Validate message content"""
        if not value.strip():
            raise serializers.ValidationError("Message content cannot be empty")
        return value.strip()
    
    def update(self, instance, validated_data):
        """Update message content"""
        instance.content = validated_data['content']
        instance.mark_as_edited()
        return instance


class MarkAsReadSerializer(serializers.Serializer):
    """Serializer for marking messages as read"""
    message_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1
    )
    
    def validate_message_ids(self, value):
        """Validate that messages exist and belong to the room"""
        room = self.context.get('room')
        if not room:
            raise serializers.ValidationError("Room context required")
        
        messages = Message.objects.filter(id__in=value, room=room) # type:ignore
        if messages.count() != len(value):
            raise serializers.ValidationError("Some messages not found in this room")
        
        return value
    
    def create(self, validated_data):
        """Mark messages as read"""
        request = self.context.get('request')
        room = self.context.get('room')
        
        messages = Message.objects.filter(
            id__in=validated_data['message_ids'],
            room=room
        )
        
        statuses = []
        for message in messages:
            status, created = MessageStatus.objects.get_or_create(
                message=message,
                user=request.user,
                defaults={'status': 'read'}
            )
            if not created:
                status.status = 'read'
                status.save()
            statuses.append(status)
        
        # Update last read message in membership
        if messages.exists():
            last_message = messages.order_by('-created_at').first()
            try:
                membership = ChatRoomMembership.objects.get(room=room, user=request.user)
                membership.last_read_message = last_message
                membership.save()
            except ChatRoomMembership.DoesNotExist:
                pass
        
        return statuses
