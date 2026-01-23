# apps/accounts/backends.py
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async

User = get_user_model()


class CuilEmailBackend:
    """
    Autentica SIN password comparando cuil + email.
    Compatible con vistas síncronas (WSGI) y asíncronas (ASGI).
    """

    # ─────────────────────────────────────────────────────────────
    # Métodos SÍNCRONOS (usados por vistas normales / WSGI)
    # ─────────────────────────────────────────────────────────────
    def authenticate(self, request, cuil=None, email=None, **kwargs):
        if not cuil or not email:
            return None
        try:
            user = User.objects.get(cuil=cuil, email__iexact=email)
        except User.DoesNotExist:
            return None
        return user if getattr(user, "is_active", True) else None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    # ─────────────────────────────────────────────────────────────
    # Métodos ASÍNCRONOS (usados por vistas async / ASGI / SSE)
    # ─────────────────────────────────────────────────────────────
    async def aauthenticate(self, request, cuil=None, email=None, **kwargs):
        """Versión asíncrona de authenticate()."""
        if not cuil or not email:
            return None
        try:
            user = await User.objects.aget(cuil=cuil, email__iexact=email)
        except User.DoesNotExist:
            return None
        return user if getattr(user, "is_active", True) else None

    async def aget_user(self, user_id):
        """Versión asíncrona de get_user() - requerida por Django ASGI."""
        try:
            return await User.objects.aget(pk=user_id)
        except User.DoesNotExist:
            return None