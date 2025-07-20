from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django.db.models import Q, Prefetch
from .models import ChatRoom, Message, MessageStatus, TypingIndicator, ChatRoomMembership
from .serializers import (
    ChatRoomSerializer, MessageSerializer, CreatePrivateRoomSerializer,
    CreateGroupRoomSerializer, MessageEditSerializer, MarkAsReadSerializer,
    TypingIndicatorSerializer, UserSerializer
)

User = get_user_model()


class MessagePagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class ChatRoomListView(generics.ListAPIView):
    """List all chat rooms for the authenticated user"""
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatRoom.objects.filter( # type:ignore
            participants=self.request.user
        ).prefetch_related(
            'participants',
            'messages',
            'memberships'
        ).order_by('-updated_at')


class ChatRoomDetailView(generics.RetrieveAPIView):
    """Get details of a specific chat room"""
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatRoom.objects.filter(
            participants=self.request.user
        ).prefetch_related(
            'participants',
            'messages',
            'memberships'
        )


class CreatePrivateRoomView(generics.CreateAPIView):
    """Create or get a private chat room"""
    serializer_class = CreatePrivateRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        room = serializer.save()
        
        # Return the room details
        room_serializer = ChatRoomSerializer(room, context={'request': request})
        return Response(room_serializer.data, status=status.HTTP_201_CREATED)


class CreateGroupRoomView(generics.CreateAPIView):
    """Create a group chat room"""
    serializer_class = CreateGroupRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        room = serializer.save()
        
        # Return the room details
        room_serializer = ChatRoomSerializer(room, context={'request': request})
        return Response(room_serializer.data, status=status.HTTP_201_CREATED)


class MessageListView(generics.ListCreateAPIView):
    """List messages in a chat room and create new messages"""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MessagePagination
    
    def get_queryset(self):
        room_id = self.kwargs['room_id']
        room = get_object_or_404(ChatRoom, id=room_id, participants=self.request.user)
        
        return Message.objects.filter( # type:ignore
            room=room
        ).select_related('sender').prefetch_related(
            'statuses__user'
        ).order_by('-created_at')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        room_id = self.kwargs['room_id']
        room = get_object_or_404(ChatRoom, id=room_id, participants=self.request.user)
        context['room'] = room
        return context
    
    def perform_create(self, serializer):
        room_id = self.kwargs['room_id']
        room = get_object_or_404(ChatRoom, id=room_id, participants=self.request.user)
        
        # Create the message
        message = serializer.save(room=room, sender=self.request.user)
        
        # Create message statuses for all participants except sender
        participants = room.participants.exclude(id=self.request.user.id)
        for participant in participants:
            MessageStatus.objects.create(
                message=message,
                user=participant,
                status='delivered'
            )
        
        # Update room's last activity
        room.updated_at = message.created_at
        room.save()


class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a specific message"""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        room_id = self.kwargs['room_id']
        room = get_object_or_404(ChatRoom, id=room_id, participants=self.request.user)
        
        return Message.objects.filter(
            room=room
        ).select_related('sender').prefetch_related(
            'statuses__user'
        )
    
    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return MessageEditSerializer
        return MessageSerializer
    
    def perform_update(self, serializer):
        # Only allow message owner to edit
        if serializer.instance.sender != self.request.user:
            raise permissions.PermissionDenied("You can only edit your own messages")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        # Only allow message owner to delete
        if instance.sender != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own messages")
        
        instance.delete()


class MarkMessagesAsReadView(generics.CreateAPIView):
    """Mark messages as read"""
    serializer_class = MarkAsReadSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        room_id = self.kwargs['room_id']
        room = get_object_or_404(ChatRoom, id=room_id, participants=self.request.user)
        context['room'] = room
        return context
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        statuses = serializer.save()
        
        return Response(
            {'message': f'Marked {len(statuses)} messages as read'},
            status=status.HTTP_200_OK
        )


class TypingIndicatorView(generics.CreateAPIView):
    """Handle typing indicators"""
    serializer_class = TypingIndicatorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        room_id = self.kwargs['room_id']
        room = get_object_or_404(ChatRoom, id=room_id, participants=self.request.user)
        
        is_typing = request.data.get('is_typing', False)
        
        if is_typing:
            # Set typing indicator
            indicator, created = TypingIndicator.objects.get_or_create(
                room=room,
                user=request.user,
                defaults={'is_typing': True}
            )
            indicator.is_typing = True
            indicator.save()
        else:
            # Remove typing indicator
            TypingIndicator.objects.filter(room=room, user=request.user).delete()
        
        return Response(
            {'message': 'Typing indicator updated'},
            status=status.HTTP_200_OK
        )


class SearchUsersView(generics.ListAPIView):
    """Search for users to start a chat with"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if not query:
            return User.objects.none()
        
        return User.objects.filter(
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(id=self.request.user.id)[:10]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_room_participants(request, room_id):
    """Get all participants in a room"""
    room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
    participants = room.participants.all()
    serializer = UserSerializer(participants, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_participant_to_room(request, room_id):
    """Add a participant to a group room"""
    room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
    
    # Only allow adding participants to group rooms
    if room.room_type != 'group':
        return Response(
            {'error': 'Can only add participants to group rooms'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if user has admin/owner permissions
    try:
        membership = ChatRoomMembership.objects.get(room=room, user=request.user)
        if membership.role not in ['admin', 'owner']:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
    except ChatRoomMembership.DoesNotExist:
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    participant_id = request.data.get('participant_id')
    if not participant_id:
        return Response(
            {'error': 'participant_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        participant = User.objects.get(id=participant_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if user is already a participant
    if room.participants.filter(id=participant.id).exists():
        return Response(
            {'error': 'User is already a participant'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Add participant
    room.participants.add(participant)
    ChatRoomMembership.objects.create(
        room=room,
        user=participant,
        role='member'
    )
    
    return Response(
        {'message': 'Participant added successfully'},
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_participant_from_room(request, room_id, participant_id):
    """Remove a participant from a group room"""
    room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
    
    # Only allow removing participants from group rooms
    if room.room_type != 'group':
        return Response(
            {'error': 'Can only remove participants from group rooms'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if user has admin/owner permissions
    try:
        membership = ChatRoomMembership.objects.get(room=room, user=request.user)
        if membership.role not in ['admin', 'owner']:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
    except ChatRoomMembership.DoesNotExist:
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        participant = User.objects.get(id=participant_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Remove participant
    room.participants.remove(participant)
    ChatRoomMembership.objects.filter(room=room, user=participant).delete()
    
    return Response(
        {'message': 'Participant removed successfully'},
        status=status.HTTP_200_OK
    )
