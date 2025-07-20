from django.urls import path
from . import views

urlpatterns = [
    # Chat room management
    path('rooms/', views.ChatRoomListView.as_view(), name='chat-room-list'),
    path('rooms/<uuid:pk>/', views.ChatRoomDetailView.as_view(), name='chat-room-detail'),
    path('rooms/private/', views.CreatePrivateRoomView.as_view(), name='create-private-room'),
    path('rooms/create/group/', views.CreateGroupRoomView.as_view(), name='create-group-room'),
    
    # Messages
    path('rooms/<uuid:room_id>/messages/', views.MessageListView.as_view(), name='message-list'),
    path('rooms/<uuid:room_id>/messages/<uuid:pk>/', views.MessageDetailView.as_view(), name='message-detail'),
    path('rooms/<uuid:room_id>/messages/mark-read/', views.MarkMessagesAsReadView.as_view(), name='mark-messages-read'),
    
    # Typing indicators
    path('rooms/<uuid:room_id>/typing/', views.TypingIndicatorView.as_view(), name='typing-indicator'),
    
    # Participants
    path('rooms/<uuid:room_id>/participants/', views.get_room_participants, name='room-participants'),
    path('rooms/<uuid:room_id>/participants/add/', views.add_participant_to_room, name='add-participant'),
    path('rooms/<uuid:room_id>/participants/<uuid:participant_id>/remove/', views.remove_participant_from_room, name='remove-participant'),
    
    # User search
    path('users/search/', views.SearchUsersView.as_view(), name='search-users'),
]
