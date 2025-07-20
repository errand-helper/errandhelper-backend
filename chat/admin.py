from django.contrib import admin
from .models import ChatRoom, Message, MessageStatus, TypingIndicator, ChatRoomMembership


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'room_type', 'created_at', 'updated_at']
    list_filter = ['room_type', 'created_at']
    search_fields = ['name', 'participants__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    filter_horizontal = ['participants']
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('participants')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'room', 'sender', 'content_preview', 'message_type', 'created_at', 'is_edited']
    list_filter = ['message_type', 'created_at', 'is_edited']
    search_fields = ['content', 'sender__email', 'room__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('room', 'sender')


@admin.register(MessageStatus)
class MessageStatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'message', 'user', 'status', 'timestamp']
    list_filter = ['status', 'timestamp']
    search_fields = ['user__email', 'message__content']
    readonly_fields = ['id', 'timestamp']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('message', 'user')


@admin.register(ChatRoomMembership)
class ChatRoomMembershipAdmin(admin.ModelAdmin):
    list_display = ['id', 'room', 'user', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['user__email', 'room__name']
    readonly_fields = ['id', 'joined_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('room', 'user')


@admin.register(TypingIndicator)
class TypingIndicatorAdmin(admin.ModelAdmin):
    list_display = ['id', 'room', 'user', 'is_typing', 'timestamp']
    list_filter = ['is_typing', 'timestamp']
    search_fields = ['user__email', 'room__name']
    readonly_fields = ['id', 'timestamp']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('room', 'user')
