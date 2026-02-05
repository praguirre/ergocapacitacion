# apps/accounts/backends.py
# ============================================================================
# COMMIT 10: Backends de autenticación dual
# ============================================================================

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class CuilEmailBackend:
    """
    Backend de autenticación para TRABAJADORES (trainees).
    Autentica usando CUIL + Email, SIN password.
    
    Uso:
        user = authenticate(request, cuil='20123456789', email='user@example.com')
    """
    
    def authenticate(self, request, cuil=None, email=None, **kwargs):
        """Autenticación síncrona para vistas normales."""
        if not cuil or not email:
            return None
        
        try:
            user = User.objects.get(
                cuil=cuil, 
                email__iexact=email,
                user_type='trainee'  # Solo trainees pueden usar este backend
            )
        except User.DoesNotExist:
            return None
        
        return user if user.is_active else None
    
    def get_user(self, user_id):
        """Obtiene usuario por ID (requerido por Django)."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
    
    # Métodos asíncronos para vistas async (SSE, etc.)
    async def aauthenticate(self, request, cuil=None, email=None, **kwargs):
        """Autenticación asíncrona."""
        if not cuil or not email:
            return None
        
        try:
            user = await User.objects.aget(
                cuil=cuil, 
                email__iexact=email,
                user_type='trainee'
            )
        except User.DoesNotExist:
            return None
        
        return user if user.is_active else None
    
    async def aget_user(self, user_id):
        """Obtiene usuario por ID (async)."""
        try:
            return await User.objects.aget(pk=user_id)
        except User.DoesNotExist:
            return None


class ProfessionalBackend(ModelBackend):
    """
    Backend de autenticación para PROFESIONALES.
    Extiende ModelBackend para autenticar con email/username + password.
    Solo permite autenticación de usuarios tipo 'professional'.
    
    Uso:
        user = authenticate(request, username='user@example.com', password='pass123')
        # o
        user = authenticate(request, username='miusuario', password='pass123')
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Autentica un profesional por email o username + password.
        """
        if username is None or password is None:
            return None
        
        # Intentar buscar por email primero, luego por username
        user = None
        try:
            # Buscar por email
            user = User.objects.get(email__iexact=username, user_type='professional')
        except User.DoesNotExist:
            try:
                # Buscar por username
                user = User.objects.get(username__iexact=username, user_type='professional')
            except User.DoesNotExist:
                # Ejecutar el hasher para evitar timing attacks
                User().set_password(password)
                return None
        
        # Verificar password
        if user and user.check_password(password) and user.is_active:
            return user
        
        return None
    
    def get_user(self, user_id):
        """Obtiene usuario por ID."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
