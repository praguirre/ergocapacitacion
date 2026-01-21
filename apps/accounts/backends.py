# apps/accounts/backends.py
from django.contrib.auth import get_user_model

User = get_user_model()

class CuilEmailBackend:
    """
    Autentica SIN password comparando cuil + email.
    """
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
