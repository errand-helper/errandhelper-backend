from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from django.conf import settings
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from urllib.parse import parse_qs

User = get_user_model()


@database_sync_to_async
def get_user(token_key):
    try:
        # Validate token
        UntypedToken(token_key)
        
        # Decode token to get user_id
        decoded_data = jwt_decode(token_key, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_data.get('user_id')
        
        if user_id:
            user = User.objects.get(id=user_id)
            return user
        else:
            return AnonymousUser()
    except (InvalidToken, TokenError, User.DoesNotExist):
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """Custom JWT authentication middleware for WebSockets"""
    
    async def __call__(self, scope, receive, send):
        # Get the token from query parameters
        query_params = parse_qs(scope['query_string'].decode())
        token = query_params.get('token')
        
        if token and len(token) > 0:
            token_key = token[0]
            scope['user'] = await get_user(token_key)
        else:
            scope['user'] = AnonymousUser()
        
        return await super().__call__(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    """JWT authentication middleware stack"""
    return JWTAuthMiddleware(inner)
