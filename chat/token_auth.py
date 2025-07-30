# chat/token_auth.py
from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token

@database_sync_to_async
def get_user(token_key):
    try:
        return Token.objects.select_related("user").get(key=token_key).user
    except Token.DoesNotExist:
        return None

class TokenAuthMiddleware:
    """
    Accepts ?token=<DRF_TOKEN> on the WS URL and sets scope['user'].
    """
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        token_key = parse_qs(query_string).get("token", [None])[0]
        if token_key:
            user = await get_user(token_key)
            scope["user"] = user or AnonymousUser()
        return await self.inner(scope, receive, send)

def TokenAuthMiddlewareStack(inner):
    # You can optionally wrap Django's AuthMiddlewareStack too
    return TokenAuthMiddleware(inner)
