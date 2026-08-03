# 📋 ERGOSOLUTIONS - PLAN MAESTRO DE COMMITS

## Documento de Referencia para Implementación

**Proyecto:** ErgoSolutions  
**Estado actual:** Commit 8 completado  
**Commits planificados:** 9 - 28  
**Fecha de creación:** Febrero 2026

---

## 📑 ÍNDICE DE COMMITS

| Fase | Commits | Descripción |
|------|---------|-------------|
| **FASE 1** | 9-11 | Fundamentos (Modelo, Auth, URLs) |
| **FASE 2** | 12-14 | Landing y Auth Profesionales |
| **FASE 3** | 15-17 | Dashboard y Menú Capacitaciones |
| **FASE 4** | 18-21 | Modo Presencial |
| **FASE 5** | 22-25 | Modo Online (Sistema de Links) |
| **FASE 6** | 26-28 | Mejoras, Testing y Pulido |

---

# ═══════════════════════════════════════════════════════════════════════════════
# FASE 1: FUNDAMENTOS
# ═══════════════════════════════════════════════════════════════════════════════

## COMMIT 9: Refactorizar TraineeUser → CustomUser con user_type

### 📋 Descripción
Renombrar el modelo de usuario actual y agregar soporte para dos tipos de usuarios:
- `professional`: Profesionales de SySO (con password)
- `trainee`: Trabajadores (sin password, sistema actual)

### 🎯 Objetivos
- [ ] Renombrar `TraineeUser` → `CustomUser`
- [ ] Agregar campo `user_type` con choices
- [ ] Agregar campos específicos de profesional
- [ ] Preparar campos de suscripción (desactivados)
- [ ] Crear migración de datos
- [ ] Actualizar todas las referencias en el proyecto

### 📁 Archivos a modificar

#### 1. `apps/accounts/models.py` (REEMPLAZAR COMPLETO)

```python
# apps/accounts/models.py
# ============================================================================
# COMMIT 9: Refactorización TraineeUser → CustomUser con user_type
# ============================================================================

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.core.validators import RegexValidator


class CustomUserManager(BaseUserManager):
    """
    Manager personalizado para CustomUser.
    Soporta creación de ambos tipos de usuario: professional y trainee.
    """
    
    def create_user(self, email: str, user_type: str = 'trainee', password=None, **extra_fields):
        """
        Crea un usuario regular.
        - Profesionales: requieren password
        - Trainees: sin password (autenticación por CUIL+email)
        """
        if not email:
            raise ValueError("El email es requerido")
        
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        
        user = self.model(email=email, user_type=user_type, **extra_fields)
        
        if user_type == 'professional':
            if not password:
                raise ValueError("Los profesionales requieren contraseña")
            user.set_password(password)
        else:
            user.set_unusable_password()
        
        user.save(using=self._db)
        return user
    
    def create_trainee(self, cuil: str, email: str, **extra_fields):
        """Atajo para crear un trabajador (trainee) sin password."""
        if not cuil:
            raise ValueError("CUIL es requerido para trainees")
        extra_fields['cuil'] = cuil
        return self.create_user(email=email, user_type='trainee', **extra_fields)
    
    def create_professional(self, email: str, password: str, username: str, **extra_fields):
        """Atajo para crear un profesional con password."""
        if not username:
            raise ValueError("Username es requerido para profesionales")
        extra_fields['username'] = username
        return self.create_user(email=email, user_type='professional', password=password, **extra_fields)
    
    def create_superuser(self, email: str, password: str, **extra_fields):
        """Crea un superusuario (siempre es tipo professional)."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'professional')
        
        if not extra_fields.get('username'):
            # Usar parte del email como username si no se proporciona
            extra_fields['username'] = email.split('@')[0]
        
        return self.create_user(email=email, password=password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuario unificado para ErgoSolutions.
    Soporta dos tipos de usuarios con diferentes flujos de autenticación.
    """
    
    # =========================================================================
    # Tipos de Usuario
    # =========================================================================
    class UserType(models.TextChoices):
        PROFESSIONAL = 'professional', 'Profesional SySO'
        TRAINEE = 'trainee', 'Trabajador'
    
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.TRAINEE,
        verbose_name="Tipo de usuario"
    )
    
    # =========================================================================
    # Campos Comunes (ambos tipos)
    # =========================================================================
    email = models.EmailField(
        unique=True, 
        db_index=True,
        verbose_name="Email"
    )
    first_name = models.CharField(
        max_length=100, 
        blank=True, 
        default="",
        verbose_name="Nombre"
    )
    last_name = models.CharField(
        max_length=100, 
        blank=True, 
        default="",
        verbose_name="Apellido"
    )
    # Campo legacy para compatibilidad con código existente
    full_name = models.CharField(
        max_length=200, 
        blank=True, 
        default="",
        verbose_name="Nombre completo"
    )
    
    # =========================================================================
    # Campos de Profesional (opcionales para trainee)
    # =========================================================================
    username = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Usuario",
        help_text="Usuario para login de profesionales"
    )
    dni = models.CharField(
        max_length=15,
        blank=True,
        default="",
        verbose_name="DNI",
        validators=[RegexValidator(r'^\d{7,8}$', 'DNI inválido (7-8 dígitos)')]
    )
    profession = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Profesión",
        help_text="Ej: Lic. en Higiene y Seguridad, Médico Laboral, Ergónomo"
    )
    license_number = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="Matrícula profesional"
    )
    
    # =========================================================================
    # Campos de Trabajador/Trainee (opcionales para professional)
    # =========================================================================
    cuil = models.CharField(
        max_length=20, 
        unique=True, 
        null=True,
        blank=True,
        db_index=True,
        verbose_name="CUIL"
    )
    job_title = models.CharField(
        max_length=200, 
        blank=True, 
        default="",
        verbose_name="Puesto de trabajo"
    )
    company_name = models.CharField(
        max_length=200, 
        blank=True, 
        default="",
        verbose_name="Empresa"
    )
    employer_email = models.EmailField(
        blank=True,
        default="",
        verbose_name="Email del empleador"
    )
    safety_responsible_email = models.EmailField(
        blank=True,
        default="",
        verbose_name="Email del responsable SySO"
    )
    
    # =========================================================================
    # Campos de Suscripción (para futuro)
    # =========================================================================
    class SubscriptionTier(models.TextChoices):
        FREE = 'free', 'Gratuito'
        BASIC = 'basic', 'Básico'
        PREMIUM = 'premium', 'Premium'
    
    class SubscriptionStatus(models.TextChoices):
        NONE = 'none', 'Sin suscripción'
        ACTIVE = 'active', 'Activa'
        EXPIRED = 'expired', 'Vencida'
        CANCELLED = 'cancelled', 'Cancelada'
    
    subscription_tier = models.CharField(
        max_length=20,
        choices=SubscriptionTier.choices,
        default=SubscriptionTier.FREE,
        verbose_name="Plan de suscripción"
    )
    subscription_status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.NONE,
        verbose_name="Estado de suscripción"
    )
    subscription_expires = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Vencimiento de suscripción"
    )
    
    # =========================================================================
    # Campos de Control
    # =========================================================================
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    # =========================================================================
    # Configuración del modelo
    # =========================================================================
    objects = CustomUserManager()
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Email ya es el USERNAME_FIELD
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['-date_joined']
    
    def __str__(self):
        if self.full_name:
            return f"{self.full_name} ({self.email})"
        elif self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip() + f" ({self.email})"
        return self.email
    
    # =========================================================================
    # Propiedades útiles
    # =========================================================================
    @property
    def is_professional(self) -> bool:
        """Retorna True si es un profesional de SySO."""
        return self.user_type == self.UserType.PROFESSIONAL
    
    @property
    def is_trainee(self) -> bool:
        """Retorna True si es un trabajador/trainee."""
        return self.user_type == self.UserType.TRAINEE
    
    @property
    def display_name(self) -> str:
        """Retorna el nombre para mostrar."""
        if self.full_name:
            return self.full_name
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.email.split('@')[0]
    
    @property
    def has_active_subscription(self) -> bool:
        """Verifica si tiene suscripción activa (para futuro)."""
        if self.subscription_status != self.SubscriptionStatus.ACTIVE:
            return False
        if self.subscription_expires and self.subscription_expires < timezone.now():
            return False
        return True
    
    def save(self, *args, **kwargs):
        """Override save para mantener compatibilidad con full_name."""
        # Si se setean first_name/last_name pero no full_name, actualizar full_name
        if (self.first_name or self.last_name) and not self.full_name:
            self.full_name = f"{self.first_name} {self.last_name}".strip()
        # Si se setea full_name pero no first/last, intentar dividir
        elif self.full_name and not self.first_name and not self.last_name:
            parts = self.full_name.split(' ', 1)
            self.first_name = parts[0]
            self.last_name = parts[1] if len(parts) > 1 else ''
        super().save(*args, **kwargs)
```

#### 2. `apps/accounts/admin.py` (REEMPLAZAR COMPLETO)

```python
# apps/accounts/admin.py
# ============================================================================
# COMMIT 9: Admin actualizado para CustomUser
# ============================================================================

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(DjangoUserAdmin):
    """Admin personalizado para CustomUser con soporte dual."""
    
    model = User
    
    # Columnas en la lista
    list_display = (
        "email", 
        "user_type",
        "display_name_admin",
        "company_name", 
        "is_staff", 
        "is_active",
        "date_joined",
    )
    
    # Filtros laterales
    list_filter = (
        "user_type",
        "is_staff", 
        "is_active", 
        "is_superuser",
        "subscription_tier",
        "subscription_status",
    )
    
    # Búsqueda
    search_fields = (
        "email", 
        "username",
        "cuil", 
        "full_name",
        "first_name",
        "last_name",
        "company_name",
        "dni",
    )
    
    ordering = ("-date_joined",)
    
    # Campos en el formulario de edición
    fieldsets = (
        ("Acceso", {
            "fields": ("email", "username", "password", "user_type")
        }),
        ("Datos Personales", {
            "fields": ("first_name", "last_name", "full_name")
        }),
        ("Datos de Profesional", {
            "fields": ("dni", "profession", "license_number"),
            "classes": ("collapse",),
            "description": "Solo para usuarios tipo Profesional"
        }),
        ("Datos de Trabajador", {
            "fields": ("cuil", "job_title", "company_name"),
            "classes": ("collapse",),
            "description": "Solo para usuarios tipo Trabajador"
        }),
        ("Emails de Notificación (Trabajadores)", {
            "fields": ("employer_email", "safety_responsible_email"),
            "classes": ("collapse",),
        }),
        ("Suscripción (Futuro)", {
            "fields": ("subscription_tier", "subscription_status", "subscription_expires"),
            "classes": ("collapse",),
        }),
        ("Permisos", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
            "classes": ("collapse",),
        }),
        ("Fechas", {
            "fields": ("last_login", "date_joined"),
            "classes": ("collapse",),
        }),
    )
    
    # Campos en el formulario de creación
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", 
                "user_type",
                "username",
                "password1", 
                "password2",
                "first_name",
                "last_name",
            ),
        }),
    )
    
    def display_name_admin(self, obj):
        """Nombre para mostrar en el admin."""
        return obj.display_name
    display_name_admin.short_description = "Nombre"
    display_name_admin.admin_order_field = "full_name"
```

#### 3. `config/settings.py` (MODIFICAR)

```python
# Buscar y cambiar:
AUTH_USER_MODEL = "accounts.TraineeUser"

# Por:
AUTH_USER_MODEL = "accounts.CustomUser"
```

#### 4. Migración de datos

```bash
# IMPORTANTE: Ejecutar en este orden

# 1. Crear migración para el nuevo modelo
python manage.py makemigrations accounts --name rename_traineeuser_to_customuser

# 2. Aplicar migración
python manage.py migrate

# 3. Si hay errores, puede ser necesario crear una migración manual
#    para renombrar la tabla (ver archivo de migración abajo)
```

#### 5. Migración manual si es necesaria: `apps/accounts/migrations/0003_rename_model.py`

```python
# apps/accounts/migrations/0003_rename_model.py
# Solo si makemigrations no maneja bien el rename

from django.db import migrations


class Migration(migrations.Migration):
    
    dependencies = [
        ('accounts', '0002_traineeuser_employer_email_and_more'),
    ]
    
    operations = [
        # Renombrar el modelo
        migrations.RenameModel(
            old_name='TraineeUser',
            new_name='CustomUser',
        ),
        
        # Agregar nuevos campos
        migrations.AddField(
            model_name='customuser',
            name='user_type',
            field=models.CharField(
                choices=[('professional', 'Profesional SySO'), ('trainee', 'Trabajador')],
                default='trainee',
                max_length=20,
                verbose_name='Tipo de usuario'
            ),
        ),
        migrations.AddField(
            model_name='customuser',
            name='username',
            field=models.CharField(
                blank=True,
                max_length=50,
                null=True,
                unique=True,
                verbose_name='Usuario'
            ),
        ),
        migrations.AddField(
            model_name='customuser',
            name='dni',
            field=models.CharField(blank=True, default='', max_length=15, verbose_name='DNI'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='profession',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Profesión'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='license_number',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='Matrícula profesional'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Nombre'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='last_name',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Apellido'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='subscription_tier',
            field=models.CharField(
                choices=[('free', 'Gratuito'), ('basic', 'Básico'), ('premium', 'Premium')],
                default='free',
                max_length=20,
                verbose_name='Plan de suscripción'
            ),
        ),
        migrations.AddField(
            model_name='customuser',
            name='subscription_status',
            field=models.CharField(
                choices=[('none', 'Sin suscripción'), ('active', 'Activa'), ('expired', 'Vencida'), ('cancelled', 'Cancelada')],
                default='none',
                max_length=20,
                verbose_name='Estado de suscripción'
            ),
        ),
        migrations.AddField(
            model_name='customuser',
            name='subscription_expires',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Vencimiento de suscripción'),
        ),
        
        # Modificar cuil para que sea nullable (profesionales no lo tienen)
        migrations.AlterField(
            model_name='customuser',
            name='cuil',
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=20,
                null=True,
                unique=True,
                verbose_name='CUIL'
            ),
        ),
    ]
```

### ✅ Verificación del Commit 9
- [ ] El modelo CustomUser está funcionando
- [ ] Los usuarios existentes siguen funcionando (tipo trainee por defecto)
- [ ] Se puede crear un superuser con `python manage.py createsuperuser`
- [ ] El admin muestra correctamente los nuevos campos
- [ ] Las capacitaciones existentes siguen funcionando

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 9: Refactorizar TraineeUser → CustomUser con user_type

- Renombrado modelo TraineeUser a CustomUser
- Agregado campo user_type: 'professional' | 'trainee'
- Agregados campos de profesional: username, dni, profession, license_number
- Agregados campos first_name, last_name (manteniendo full_name por compatibilidad)
- Preparados campos de suscripción (subscription_tier, status, expires)
- CUIL ahora es nullable (profesionales no lo requieren)
- Actualizado CustomUserManager con métodos create_trainee y create_professional
- Admin actualizado con fieldsets organizados por tipo de usuario
- Usuarios existentes migrados como tipo 'trainee' automáticamente"
```

---

## COMMIT 10: Configurar sistema de autenticación dual

### 📋 Descripción
Configurar Django para soportar dos backends de autenticación:
- `ModelBackend`: Para profesionales (email/username + password)
- `CuilEmailBackend`: Para trabajadores (CUIL + email, sin password)

### 🎯 Objetivos
- [ ] Actualizar `CuilEmailBackend` para trabajar con CustomUser
- [ ] Crear backend para profesionales si es necesario
- [ ] Configurar `AUTHENTICATION_BACKENDS` en settings
- [ ] Crear decoradores de permisos por tipo de usuario
- [ ] Crear mixins para vistas basadas en clase

### 📁 Archivos a modificar/crear

#### 1. `apps/accounts/backends.py` (ACTUALIZAR)

```python
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
```

#### 2. `apps/accounts/decorators.py` (CREAR NUEVO)

```python
# apps/accounts/decorators.py
# ============================================================================
# COMMIT 10: Decoradores de permisos por tipo de usuario
# ============================================================================

from functools import wraps
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseForbidden


def professional_required(function=None, redirect_url=None, login_url=None):
    """
    Decorador que requiere que el usuario sea un profesional autenticado.
    
    Uso:
        @professional_required
        def my_view(request):
            ...
        
        @professional_required(redirect_url='landing')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                # Redirigir a login de profesionales
                url = login_url or reverse('professional_login')
                return redirect(f"{url}?next={request.path}")
            
            if not request.user.is_professional:
                # Usuario autenticado pero no es profesional
                if redirect_url:
                    return redirect(redirect_url)
                return HttpResponseForbidden(
                    "Acceso denegado. Esta sección es solo para profesionales."
                )
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    
    if function:
        return decorator(function)
    return decorator


def trainee_required(function=None, redirect_url=None, login_url=None):
    """
    Decorador que requiere que el usuario sea un trabajador (trainee) autenticado.
    
    Uso:
        @trainee_required
        def training_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                # Redirigir a login de trainees (capacitación)
                url = login_url or reverse('landing')
                return redirect(f"{url}?next={request.path}")
            
            if not request.user.is_trainee:
                # Usuario autenticado pero no es trainee
                if redirect_url:
                    return redirect(redirect_url)
                return HttpResponseForbidden(
                    "Acceso denegado. Esta sección es solo para trabajadores en capacitación."
                )
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    
    if function:
        return decorator(function)
    return decorator


def subscription_required(tier='basic', redirect_url=None):
    """
    Decorador que requiere una suscripción activa de cierto nivel.
    Para uso futuro cuando se implemente el sistema de suscripciones.
    
    Uso:
        @subscription_required(tier='premium')
        def premium_feature(request):
            ...
    """
    tier_levels = {'free': 0, 'basic': 1, 'premium': 2}
    required_level = tier_levels.get(tier, 0)
    
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('professional_login')
            
            if not request.user.is_professional:
                return HttpResponseForbidden("Solo para profesionales.")
            
            # Verificar nivel de suscripción
            user_level = tier_levels.get(request.user.subscription_tier, 0)
            
            if not request.user.has_active_subscription or user_level < required_level:
                if redirect_url:
                    return redirect(redirect_url)
                # TODO: Redirigir a página de upgrade
                return HttpResponseForbidden(
                    f"Esta función requiere suscripción {tier}."
                )
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
```

#### 3. `apps/accounts/mixins.py` (CREAR NUEVO)

```python
# apps/accounts/mixins.py
# ============================================================================
# COMMIT 10: Mixins para vistas basadas en clase
# ============================================================================

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse


class ProfessionalRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin para vistas basadas en clase que requieren un profesional.
    
    Uso:
        class MyView(ProfessionalRequiredMixin, TemplateView):
            template_name = 'my_template.html'
    """
    login_url = None  # Se define en get_login_url()
    
    def get_login_url(self):
        return reverse('professional_login')
    
    def test_func(self):
        return self.request.user.is_professional
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            # Usuario logueado pero no es profesional
            return redirect('dashboard')  # O donde corresponda
        return super().handle_no_permission()


class TraineeRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin para vistas que requieren un trabajador (trainee).
    
    Uso:
        class TrainingView(TraineeRequiredMixin, TemplateView):
            template_name = 'training.html'
    """
    login_url = None
    
    def get_login_url(self):
        return reverse('landing')
    
    def test_func(self):
        return self.request.user.is_trainee


class SubscriptionRequiredMixin(ProfessionalRequiredMixin):
    """
    Mixin que requiere suscripción activa (para futuro).
    
    Uso:
        class PremiumView(SubscriptionRequiredMixin, TemplateView):
            required_tier = 'premium'
            template_name = 'premium_feature.html'
    """
    required_tier = 'basic'
    
    def test_func(self):
        if not super().test_func():
            return False
        
        tier_levels = {'free': 0, 'basic': 1, 'premium': 2}
        required_level = tier_levels.get(self.required_tier, 0)
        user_level = tier_levels.get(self.request.user.subscription_tier, 0)
        
        return (
            self.request.user.has_active_subscription and 
            user_level >= required_level
        )
```

#### 4. `config/settings.py` (AGREGAR)

```python
# ============================================================================
# Authentication Backends (COMMIT 10)
# ============================================================================

AUTHENTICATION_BACKENDS = [
    # Backend para profesionales (email/username + password)
    'apps.accounts.backends.ProfessionalBackend',
    # Backend para trabajadores (CUIL + email, sin password)
    'apps.accounts.backends.CuilEmailBackend',
]

# URLs de login por defecto
LOGIN_URL = 'landing'  # Para trainees
LOGIN_REDIRECT_URL = 'training_home'

# URL de login para profesionales (usado por decoradores)
PROFESSIONAL_LOGIN_URL = 'professional_login'
PROFESSIONAL_LOGIN_REDIRECT_URL = 'dashboard'
```

### ✅ Verificación del Commit 10
- [ ] Trainees pueden loguearse con CUIL + email (sin password)
- [ ] Profesionales pueden loguearse con email/username + password
- [ ] Los decoradores `@professional_required` y `@trainee_required` funcionan
- [ ] Un trainee no puede acceder a vistas de profesional y viceversa
- [ ] El superuser puede acceder a todo

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 10: Sistema de autenticación dual para profesionales y trainees

- CuilEmailBackend actualizado para solo autenticar trainees
- Nuevo ProfessionalBackend para autenticar profesionales con password
- Configurado AUTHENTICATION_BACKENDS con ambos backends
- Decoradores @professional_required y @trainee_required
- Mixins ProfessionalRequiredMixin y TraineeRequiredMixin para CBV
- Decorador @subscription_required preparado para futuro
- Settings actualizados con URLs de login diferenciadas"
```

---

## COMMIT 11: Reorganizar estructura de URLs

### 📋 Descripción
Reorganizar las URLs del proyecto para separar claramente:
- URLs públicas (landing)
- URLs de profesionales (dashboard, gestión)
- URLs de trabajadores (capacitación)
- URLs de API

### 🎯 Objetivos
- [ ] Crear nueva app `landing` para la página principal
- [ ] Crear nueva app `dashboard` para el área de profesionales
- [ ] Reorganizar `config/urls.py` con prefijos claros
- [ ] Mantener compatibilidad con URLs existentes

### 📁 Archivos a crear/modificar

#### 1. Crear app `landing`

```bash
cd apps
python ../manage.py startapp landing
```

#### 2. `apps/landing/__init__.py`
```python
# (vacío)
```

#### 3. `apps/landing/views.py`

```python
# apps/landing/views.py
# ============================================================================
# COMMIT 11: Vista placeholder para landing (se completa en Commit 12)
# ============================================================================

from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET


@require_GET
def home(request):
    """
    Landing page principal de ErgoSolutions.
    Si el usuario ya está logueado, redirige al área correspondiente.
    """
    if request.user.is_authenticated:
        if request.user.is_professional:
            return redirect('dashboard')
        else:
            return redirect('training_home')
    
    # Por ahora, redirigimos al landing actual de capacitaciones
    # En Commit 12 se crea el landing real
    return redirect('landing')  # accounts landing
```

#### 4. `apps/landing/urls.py`

```python
# apps/landing/urls.py
# ============================================================================
# COMMIT 11: URLs del landing principal
# ============================================================================

from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    path('', views.home, name='home'),
]
```

#### 5. Crear app `dashboard`

```bash
cd apps
python ../manage.py startapp dashboard
```

#### 6. `apps/dashboard/views.py`

```python
# apps/dashboard/views.py
# ============================================================================
# COMMIT 11: Vistas placeholder para dashboard (se completan en Fase 3)
# ============================================================================

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import professional_required


@login_required
@professional_required
def home(request):
    """
    Dashboard principal del profesional.
    Muestra selector de Evaluaciones / Capacitaciones.
    """
    # Placeholder - se completa en Commit 15
    return render(request, 'dashboard/home.html', {
        'user': request.user,
    })


@login_required
@professional_required
def profile(request):
    """Perfil del profesional."""
    # Placeholder - se completa en Commit 26
    return render(request, 'dashboard/profile.html', {
        'user': request.user,
    })
```

#### 7. `apps/dashboard/urls.py`

```python
# apps/dashboard/urls.py
# ============================================================================
# COMMIT 11: URLs del dashboard de profesionales
# ============================================================================

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('perfil/', views.profile, name='profile'),
]
```

#### 8. `config/urls.py` (REEMPLAZAR COMPLETO)

```python
# config/urls.py
# ============================================================================
# COMMIT 11: URLs reorganizadas para ErgoSolutions
# ============================================================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # =========================================================================
    # Admin
    # =========================================================================
    path('admin/', admin.site.urls),
    
    # =========================================================================
    # Landing Principal (ErgoSolutions)
    # =========================================================================
    # path('', include('apps.landing.urls')),  # Descomentar en Commit 12
    
    # =========================================================================
    # Autenticación de Profesionales
    # =========================================================================
    # path('auth/', include('apps.accounts.urls_professional')),  # Commit 13-14
    
    # =========================================================================
    # Dashboard de Profesionales (requiere login)
    # =========================================================================
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    
    # =========================================================================
    # Área de Capacitaciones - TRABAJADORES (sistema actual)
    # La raíz '/' va al landing de capacitaciones (registro/login trainees)
    # =========================================================================
    path('', include('apps.accounts.urls')),  # Landing actual de trainees
    path('capacitacion/', include('apps.training.urls')),  # Páginas de capacitación
    path('quiz/', include('apps.quiz.urls')),  # Quiz
    path('certificados/', include('apps.certificates.urls')),  # Certificados
    path('ai/', include('apps.ergobot_ai.urls')),  # Chatbot
    
    # =========================================================================
    # Área de Capacitaciones - ACCESO VÍA LINK (Commit 22-25)
    # URL corta para links compartibles: /c/<slug>/
    # =========================================================================
    # path('c/', include('apps.training.urls_public')),  # Commit 25
    
    # =========================================================================
    # Gestión de Capacitaciones - PROFESIONALES (Commit 16-21)
    # =========================================================================
    # path('capacitaciones/', include('apps.dashboard.urls_capacitaciones')),
    
    # =========================================================================
    # Evaluaciones - PROFESIONALES (Futuro)
    # =========================================================================
    # path('evaluaciones/', include('apps.evaluaciones.urls')),
]

# Servir archivos de media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

#### 9. Templates placeholder

**`templates/dashboard/home.html`**
```html
{% extends "base.html" %}

{% block content %}
<div class="container py-5">
    <h1>Dashboard del Profesional</h1>
    <p>Bienvenido, {{ user.display_name }}</p>
    
    <div class="alert alert-info">
        <strong>En construcción.</strong> Este dashboard se completará en los próximos commits.
    </div>
    
    <div class="row g-4 mt-4">
        <div class="col-md-6">
            <div class="card bg-secondary text-light">
                <div class="card-body text-center py-5">
                    <h3>📋 Evaluaciones</h3>
                    <p class="text-muted">Próximamente</p>
                    <button class="btn btn-outline-light" disabled>Acceder</button>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card bg-secondary text-light">
                <div class="card-body text-center py-5">
                    <h3>🎓 Capacitaciones</h3>
                    <p class="text-muted">Próximamente</p>
                    <button class="btn btn-outline-light" disabled>Acceder</button>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

**`templates/dashboard/profile.html`**
```html
{% extends "base.html" %}

{% block content %}
<div class="container py-5">
    <h1>Mi Perfil</h1>
    
    <div class="card bg-dark text-light">
        <div class="card-body">
            <p><strong>Nombre:</strong> {{ user.display_name }}</p>
            <p><strong>Email:</strong> {{ user.email }}</p>
            <p><strong>Profesión:</strong> {{ user.profession|default:"No especificada" }}</p>
            <p><strong>Matrícula:</strong> {{ user.license_number|default:"No especificada" }}</p>
        </div>
    </div>
    
    <a href="{% url 'dashboard:home' %}" class="btn btn-secondary mt-3">Volver al Dashboard</a>
</div>
{% endblock %}
```

#### 10. `config/settings.py` (AGREGAR apps)

```python
INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'django_bootstrap5',
    
    # Local apps
    'apps.accounts',
    'apps.landing',      # NUEVO - Commit 11
    'apps.dashboard',    # NUEVO - Commit 11
    'apps.training',
    'apps.quiz',
    'apps.certificates',
    'apps.ergobot_ai',
]
```

### ✅ Verificación del Commit 11
- [ ] Las apps `landing` y `dashboard` están creadas
- [ ] El sistema actual de capacitaciones sigue funcionando en `/`
- [ ] `/dashboard/` muestra el placeholder (requiere login)
- [ ] La estructura de URLs está preparada para los siguientes commits

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 11: Reorganizar estructura de URLs para ErgoSolutions

- Nueva app 'landing' para página principal (placeholder)
- Nueva app 'dashboard' para área de profesionales (placeholder)
- config/urls.py reorganizado con prefijos claros:
  * /dashboard/ - Área de profesionales
  * / - Capacitaciones (sistema actual de trainees)
  * /c/ - Preparado para links públicos (futuro)
- Templates placeholder para dashboard
- INSTALLED_APPS actualizado con nuevas apps
- Compatibilidad mantenida con sistema actual"
```

---

# ═══════════════════════════════════════════════════════════════════════════════
# FASE 2: LANDING Y AUTH PROFESIONALES
# ═══════════════════════════════════════════════════════════════════════════════

## COMMIT 12: Landing Page principal de ErgoSolutions

### 📋 Descripción
Crear la landing page principal, moderna y profesional, que presente ErgoSolutions
como plataforma para profesionales de Seguridad e Higiene.

### 🎯 Objetivos
- [ ] Diseñar landing page atractiva y profesional
- [ ] Secciones: Hero, Features, CTA
- [ ] Botones de Registro y Login para profesionales
- [ ] Responsive design (mobile-first)
- [ ] Colores y estilo corporativo

### 📁 Archivos a crear/modificar

#### 1. `templates/landing/home.html`

```html
{% extends "base_landing.html" %}
{% load static %}

{% block title %}ErgoSolutions - Plataforma para Profesionales de Seguridad e Higiene{% endblock %}

{% block content %}
<!-- HERO SECTION -->
<section class="hero-section">
    <div class="container">
        <div class="row align-items-center min-vh-100 py-5">
            <div class="col-lg-6">
                <h1 class="display-4 fw-bold text-white mb-4">
                    Potencia tu práctica profesional con 
                    <span class="text-primary">Inteligencia Artificial</span>
                </h1>
                <p class="lead text-light mb-4">
                    ErgoSolutions es la plataforma integral para profesionales de 
                    <strong>Seguridad e Higiene</strong>, <strong>Salud Ocupacional</strong> 
                    y <strong>Ergonomía</strong>. Cumple con la normativa vigente y 
                    garantiza puestos de trabajo seguros y saludables.
                </p>
                <div class="d-flex gap-3 flex-wrap">
                    <a href="{% url 'professional_register' %}" class="btn btn-primary btn-lg px-4">
                        <i class="bi bi-person-plus me-2"></i>Registrarse
                    </a>
                    <a href="{% url 'professional_login' %}" class="btn btn-outline-light btn-lg px-4">
                        <i class="bi bi-box-arrow-in-right me-2"></i>Ingresar
                    </a>
                </div>
            </div>
            <div class="col-lg-6 d-none d-lg-block">
                <div class="hero-image text-center">
                    <!-- Imagen o ilustración -->
                    <i class="bi bi-shield-check display-1 text-primary"></i>
                </div>
            </div>
        </div>
    </div>
</section>

<!-- FEATURES SECTION -->
<section class="features-section py-5 bg-dark">
    <div class="container">
        <h2 class="text-center text-white mb-5">¿Qué ofrecemos?</h2>
        
        <div class="row g-4">
            <!-- Feature 1: Evaluaciones -->
            <div class="col-md-6 col-lg-3">
                <div class="card bg-black border-secondary h-100">
                    <div class="card-body text-center">
                        <div class="feature-icon mb-3">
                            <i class="bi bi-clipboard-check display-4 text-primary"></i>
                        </div>
                        <h5 class="card-title text-white">Evaluaciones</h5>
                        <p class="card-text text-secondary">
                            Evaluaciones de riesgos ergonómicos, iluminación, ruido y más. 
                            Todo según normativa vigente.
                        </p>
                        <span class="badge bg-warning text-dark">Próximamente</span>
                    </div>
                </div>
            </div>
            
            <!-- Feature 2: Capacitaciones -->
            <div class="col-md-6 col-lg-3">
                <div class="card bg-black border-primary h-100">
                    <div class="card-body text-center">
                        <div class="feature-icon mb-3">
                            <i class="bi bi-mortarboard display-4 text-success"></i>
                        </div>
                        <h5 class="card-title text-white">Capacitaciones</h5>
                        <p class="card-text text-secondary">
                            Capacitaciones online y presenciales con certificación automática. 
                            Gestiona la formación de tus trabajadores.
                        </p>
                        <span class="badge bg-success">Disponible</span>
                    </div>
                </div>
            </div>
            
            <!-- Feature 3: IA -->
            <div class="col-md-6 col-lg-3">
                <div class="card bg-black border-secondary h-100">
                    <div class="card-body text-center">
                        <div class="feature-icon mb-3">
                            <i class="bi bi-robot display-4 text-info"></i>
                        </div>
                        <h5 class="card-title text-white">Asistente IA</h5>
                        <p class="card-text text-secondary">
                            Ergobot, nuestro asistente con IA, responde consultas 
                            y guía a los trabajadores durante las capacitaciones.
                        </p>
                        <span class="badge bg-success">Disponible</span>
                    </div>
                </div>
            </div>
            
            <!-- Feature 4: Certificados -->
            <div class="col-md-6 col-lg-3">
                <div class="card bg-black border-secondary h-100">
                    <div class="card-body text-center">
                        <div class="feature-icon mb-3">
                            <i class="bi bi-award display-4 text-warning"></i>
                        </div>
                        <h5 class="card-title text-white">Certificados</h5>
                        <p class="card-text text-secondary">
                            Certificados PDF automáticos con validez de 1 año. 
                            Envío a trabajador, empleador y responsable SySO.
                        </p>
                        <span class="badge bg-success">Disponible</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<!-- CTA SECTION -->
<section class="cta-section py-5">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-lg-8 text-center">
                <h2 class="text-white mb-4">¿Sos profesional de Seguridad e Higiene?</h2>
                <p class="lead text-light mb-4">
                    Registrate gratis y comenzá a usar la plataforma hoy mismo.
                </p>
                <a href="{% url 'professional_register' %}" class="btn btn-primary btn-lg px-5">
                    Crear cuenta gratuita
                </a>
                <p class="text-secondary mt-3 small">
                    ¿Ya tenés cuenta? 
                    <a href="{% url 'professional_login' %}" class="text-primary">Ingresá aquí</a>
                </p>
            </div>
        </div>
    </div>
</section>

<!-- TRAINEE ACCESS -->
<section class="trainee-section py-4 bg-secondary">
    <div class="container">
        <div class="row align-items-center">
            <div class="col-md-8">
                <p class="mb-md-0 text-dark">
                    <strong>¿Sos trabajador y recibiste un link de capacitación?</strong>
                    Ingresá directamente desde el link que te enviaron.
                </p>
            </div>
            <div class="col-md-4 text-md-end">
                <a href="{% url 'landing' %}" class="btn btn-dark btn-sm">
                    Ir a Capacitaciones
                </a>
            </div>
        </div>
    </div>
</section>
{% endblock %}
```

#### 2. `templates/base_landing.html` (CREAR)

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}ErgoSolutions{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    
    <style>
        :root {
            --primary-color: #0d6efd;
            --dark-bg: #1a1a2e;
            --darker-bg: #16213e;
        }
        
        body {
            background: linear-gradient(135deg, var(--dark-bg) 0%, var(--darker-bg) 100%);
            min-height: 100vh;
        }
        
        .hero-section {
            background: linear-gradient(135deg, #1a1a2e 0%, #0f0f23 100%);
        }
        
        .navbar {
            background: rgba(0, 0, 0, 0.8) !important;
            backdrop-filter: blur(10px);
        }
        
        .card {
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        
        .feature-icon i {
            transition: transform 0.3s;
        }
        
        .card:hover .feature-icon i {
            transform: scale(1.1);
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #0d6efd 0%, #0056b3 100%);
            border: none;
        }
        
        .btn-primary:hover {
            background: linear-gradient(135deg, #0056b3 0%, #003d80 100%);
        }
    </style>
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark fixed-top">
        <div class="container">
            <a class="navbar-brand fw-bold" href="{% url 'landing:home' %}">
                <i class="bi bi-shield-check me-2"></i>ErgoSolutions
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="#features">Características</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link btn btn-outline-primary ms-2 px-3" href="{% url 'professional_login' %}">
                            Ingresar
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link btn btn-primary ms-2 px-3 text-white" href="{% url 'professional_register' %}">
                            Registrarse
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    
    <!-- Messages -->
    {% if messages %}
    <div class="container mt-5 pt-5">
        {% for message in messages %}
        <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
            {{ message }}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
        {% endfor %}
    </div>
    {% endif %}
    
    <!-- Content -->
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <!-- Footer -->
    <footer class="py-4 bg-black text-secondary">
        <div class="container text-center">
            <p class="mb-0">
                © 2026 ErgoSolutions. Desarrollado por 
                <strong class="text-white">Lic. Pablo Aguirre</strong> - MN 10.027
            </p>
        </div>
    </footer>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

#### 3. `apps/landing/views.py` (ACTUALIZAR)

```python
# apps/landing/views.py
# ============================================================================
# COMMIT 12: Landing page completa
# ============================================================================

from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET


@require_GET
def home(request):
    """
    Landing page principal de ErgoSolutions.
    Redirige usuarios autenticados a su área correspondiente.
    """
    if request.user.is_authenticated:
        if request.user.is_professional:
            return redirect('dashboard:home')
        else:
            return redirect('training_home')
    
    return render(request, 'landing/home.html')
```

#### 4. `config/urls.py` (ACTIVAR landing)

```python
# Descomentar la línea del landing:
path('', include('apps.landing.urls', namespace='landing')),
```

### ✅ Verificación del Commit 12
- [ ] Landing page se muestra en `/` (raíz)
- [ ] Diseño responsive y profesional
- [ ] Botones de Registro y Login visibles
- [ ] Usuarios ya logueados son redirigidos automáticamente
- [ ] Link a capacitaciones para trabajadores funciona

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 12: Landing page principal de ErgoSolutions

- Diseño moderno y profesional con Bootstrap 5
- Hero section con CTA para registro/login
- Features section mostrando capacidades de la plataforma
- Sección para acceso de trabajadores a capacitaciones
- Template base separado (base_landing.html) para páginas públicas
- Responsive design mobile-first
- Colores corporativos y estilo dark theme"
```

---

## COMMIT 13: Registro de profesionales

### 📋 Descripción
Implementar el formulario de registro completo para profesionales con todos los campos requeridos.

### 🎯 Objetivos
- [ ] Formulario de registro con validaciones
- [ ] Campos: nombre, apellido, DNI, email, profesión, matrícula, usuario, contraseña
- [ ] Validación de usuario y email únicos
- [ ] Creación del usuario tipo 'professional'
- [ ] Template de registro profesional

### 📁 Archivos a crear/modificar

#### 1. `apps/accounts/forms.py` (AGREGAR al final)

```python
# ============================================================================
# COMMIT 13: Formularios para profesionales
# ============================================================================

class ProfessionalRegisterForm(forms.Form):
    """Formulario de registro para profesionales de SySO."""
    
    first_name = forms.CharField(
        label="Nombre",
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Juan'})
    )
    last_name = forms.CharField(
        label="Apellido",
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Pérez'})
    )
    dni = forms.CharField(
        label="DNI",
        max_length=15,
        validators=[RegexValidator(r'^\d{7,8}$', 'DNI inválido (7-8 dígitos)')],
        widget=forms.TextInput(attrs={'placeholder': '12345678'}),
        help_text="Solo números, sin puntos"
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'placeholder': 'juan.perez@ejemplo.com'})
    )
    profession = forms.CharField(
        label="Profesión",
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Lic. en Higiene y Seguridad'}),
        help_text="Ej: Lic. en Higiene y Seguridad, Médico Laboral, Ergónomo"
    )
    license_number = forms.CharField(
        label="Matrícula profesional",
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'MN 12345'}),
        required=False,
        help_text="Opcional"
    )
    username = forms.CharField(
        label="Usuario",
        max_length=50,
        validators=[
            RegexValidator(
                r'^[\w.@+-]+$',
                'Usuario inválido. Solo letras, números y @/./+/-/_'
            )
        ],
        widget=forms.TextInput(attrs={'placeholder': 'jperez'}),
        help_text="Para iniciar sesión"
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}),
        min_length=8,
        help_text="Mínimo 8 caracteres"
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'})
    )
    
    def clean_dni(self):
        dni = re.sub(r'\D', '', self.cleaned_data.get('dni', ''))
        if len(dni) < 7 or len(dni) > 8:
            raise forms.ValidationError('DNI inválido')
        return dni
    
    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este email ya está registrado')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip().lower()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Este usuario ya está en uso')
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Las contraseñas no coinciden')
        
        return cleaned_data


class ProfessionalLoginForm(forms.Form):
    """Formulario de login para profesionales."""
    
    username = forms.CharField(
        label="Usuario o Email",
        widget=forms.TextInput(attrs={'placeholder': 'usuario o email@ejemplo.com'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'})
    )
```

#### 2. `apps/accounts/views_professional.py` (CREAR NUEVO)

```python
# apps/accounts/views_professional.py
# ============================================================================
# COMMIT 13-14: Vistas de autenticación para profesionales
# ============================================================================

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from .forms import ProfessionalRegisterForm, ProfessionalLoginForm

User = get_user_model()


@require_http_methods(["GET", "POST"])
def register(request):
    """Registro de profesionales."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = ProfessionalRegisterForm(request.POST)
        if form.is_valid():
            # Crear el usuario profesional
            user = User.objects.create_professional(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                username=form.cleaned_data['username'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                dni=form.cleaned_data['dni'],
                profession=form.cleaned_data['profession'],
                license_number=form.cleaned_data.get('license_number', ''),
            )
            
            # Login automático
            login(request, user, backend='apps.accounts.backends.ProfessionalBackend')
            
            messages.success(request, f'¡Bienvenido {user.first_name}! Tu cuenta ha sido creada.')
            return redirect('dashboard:home')
    else:
        form = ProfessionalRegisterForm()
    
    return render(request, 'accounts/professional/register.html', {'form': form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    """Login de profesionales."""
    if request.user.is_authenticated:
        if request.user.is_professional:
            return redirect('dashboard:home')
        else:
            return redirect('training_home')
    
    next_url = request.GET.get('next', '')
    
    if request.method == 'POST':
        form = ProfessionalLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Hola {user.display_name}!')
                
                # Redirigir al next o al dashboard
                if next_url and next_url.startswith('/'):
                    return redirect(next_url)
                return redirect('dashboard:home')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = ProfessionalLoginForm()
    
    return render(request, 'accounts/professional/login.html', {
        'form': form,
        'next': next_url,
    })


@require_POST
def logout_view(request):
    """Logout de profesionales."""
    logout(request)
    messages.info(request, 'Has cerrado sesión.')
    return redirect('landing:home')
```

#### 3. `apps/accounts/urls_professional.py` (CREAR NUEVO)

```python
# apps/accounts/urls_professional.py
# ============================================================================
# COMMIT 13-14: URLs de autenticación para profesionales
# ============================================================================

from django.urls import path
from . import views_professional

urlpatterns = [
    path('registro/', views_professional.register, name='professional_register'),
    path('login/', views_professional.login_view, name='professional_login'),
    path('logout/', views_professional.logout_view, name='professional_logout'),
]
```

#### 4. `templates/accounts/professional/register.html`

```html
{% extends "base_landing.html" %}
{% load django_bootstrap5 %}

{% block title %}Registro de Profesional - ErgoSolutions{% endblock %}

{% block content %}
<div class="container py-5 mt-5">
    <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
            
            <div class="card bg-dark border-secondary shadow-lg">
                <div class="card-header bg-black border-secondary text-center py-3">
                    <h4 class="mb-0 text-white">
                        <i class="bi bi-person-plus me-2"></i>Registro de Profesional
                    </h4>
                </div>
                <div class="card-body p-4">
                    <form method="post" novalidate>
                        {% csrf_token %}
                        
                        <div class="row">
                            <div class="col-md-6">
                                {% bootstrap_field form.first_name %}
                            </div>
                            <div class="col-md-6">
                                {% bootstrap_field form.last_name %}
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                {% bootstrap_field form.dni %}
                            </div>
                            <div class="col-md-6">
                                {% bootstrap_field form.email %}
                            </div>
                        </div>
                        
                        {% bootstrap_field form.profession %}
                        {% bootstrap_field form.license_number %}
                        
                        <hr class="border-secondary my-4">
                        
                        {% bootstrap_field form.username %}
                        
                        <div class="row">
                            <div class="col-md-6">
                                {% bootstrap_field form.password1 %}
                            </div>
                            <div class="col-md-6">
                                {% bootstrap_field form.password2 %}
                            </div>
                        </div>
                        
                        <div class="d-grid mt-4">
                            <button type="submit" class="btn btn-primary btn-lg">
                                <i class="bi bi-check-lg me-2"></i>Crear cuenta
                            </button>
                        </div>
                    </form>
                    
                    <p class="text-center text-secondary mt-4 mb-0">
                        ¿Ya tenés cuenta? 
                        <a href="{% url 'professional_login' %}" class="text-primary">Ingresá aquí</a>
                    </p>
                </div>
            </div>
            
        </div>
    </div>
</div>
{% endblock %}
```

#### 5. `config/urls.py` (ACTIVAR)

```python
# Descomentar:
path('auth/', include('apps.accounts.urls_professional')),
```

### ✅ Verificación del Commit 13
- [ ] Formulario de registro se muestra en `/auth/registro/`
- [ ] Validaciones funcionan (email único, username único, passwords coinciden)
- [ ] Usuario profesional se crea correctamente
- [ ] Login automático después del registro
- [ ] Redirección al dashboard

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 13: Registro de profesionales

- Formulario ProfessionalRegisterForm con todos los campos
- Validaciones: email único, username único, contraseñas coinciden
- Vista de registro con creación de usuario tipo 'professional'
- Login automático post-registro
- Template de registro profesional
- URLs en /auth/registro/"
```

---

## COMMIT 14: Login/Logout de profesionales

### 📋 Descripción
Completar el sistema de login y logout para profesionales.

### 🎯 Objetivos
- [ ] Página de login con formulario
- [ ] Soporte para login con email o username
- [ ] Manejo de "recordar sesión" (opcional)
- [ ] Logout con redirección
- [ ] Mensajes de feedback

### 📁 Archivos a crear

#### 1. `templates/accounts/professional/login.html`

```html
{% extends "base_landing.html" %}
{% load django_bootstrap5 %}

{% block title %}Ingresar - ErgoSolutions{% endblock %}

{% block content %}
<div class="container py-5 mt-5">
    <div class="row justify-content-center">
        <div class="col-md-6 col-lg-4">
            
            <div class="card bg-dark border-secondary shadow-lg">
                <div class="card-header bg-black border-secondary text-center py-3">
                    <h4 class="mb-0 text-white">
                        <i class="bi bi-box-arrow-in-right me-2"></i>Ingresar
                    </h4>
                </div>
                <div class="card-body p-4">
                    <form method="post" novalidate>
                        {% csrf_token %}
                        {% if next %}<input type="hidden" name="next" value="{{ next }}">{% endif %}
                        
                        {% bootstrap_form form %}
                        
                        <div class="d-grid mt-4">
                            <button type="submit" class="btn btn-primary btn-lg">
                                <i class="bi bi-door-open me-2"></i>Ingresar
                            </button>
                        </div>
                    </form>
                    
                    <hr class="border-secondary my-4">
                    
                    <p class="text-center text-secondary mb-2">
                        ¿No tenés cuenta? 
                        <a href="{% url 'professional_register' %}" class="text-primary">Registrate</a>
                    </p>
                    
                    <p class="text-center text-secondary small mb-0">
                        <a href="#" class="text-muted">¿Olvidaste tu contraseña?</a>
                    </p>
                </div>
            </div>
            
            <!-- Link a capacitaciones -->
            <div class="card bg-secondary mt-4">
                <div class="card-body py-3 text-center">
                    <small class="text-dark">
                        ¿Sos trabajador? 
                        <a href="{% url 'landing' %}" class="text-dark fw-bold">
                            Ingresá a Capacitaciones
                        </a>
                    </small>
                </div>
            </div>
            
        </div>
    </div>
</div>
{% endblock %}
```

### ✅ Verificación del Commit 14
- [ ] Login funciona en `/auth/login/`
- [ ] Se puede ingresar con email o username
- [ ] Mensaje de error si credenciales son incorrectas
- [ ] Logout funciona y redirige al landing
- [ ] Parámetro `next` funciona para redirección

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 14: Login/Logout de profesionales

- Página de login con formulario
- Soporte para login con email o username
- Manejo del parámetro 'next' para redirección
- Logout con mensaje de confirmación
- Link a registro y a capacitaciones de trabajadores
- Sistema de autenticación de profesionales completo"
```

---

# ═══════════════════════════════════════════════════════════════════════════════
# FASE 3: DASHBOARD Y MENÚ CAPACITACIONES
# ═══════════════════════════════════════════════════════════════════════════════

## COMMIT 15: Dashboard con selector Evaluaciones/Capacitaciones

### 📋 Descripción
Crear el dashboard principal del profesional con las dos opciones principales:
Evaluaciones (desactivado) y Capacitaciones (activo).

### 🎯 Objetivos
- [ ] Dashboard con cards de selección
- [ ] Card de Evaluaciones con badge "Próximamente"
- [ ] Card de Capacitaciones activa
- [ ] Navbar para área de profesionales
- [ ] Sidebar o menú lateral (opcional)

### 📁 Archivos a modificar

#### 1. `templates/base_dashboard.html` (CREAR)

Template base para el área de profesionales con navbar y estructura.

#### 2. `templates/dashboard/home.html` (ACTUALIZAR)

Dashboard con cards interactivas.

#### 3. `apps/dashboard/views.py` (ACTUALIZAR)

Vista completa del dashboard.

### 📝 Mensaje de Commit
```bash
git commit -m "Commit 15: Dashboard principal con selector Evaluaciones/Capacitaciones

- Template base para área de profesionales (base_dashboard.html)
- Dashboard con cards de Evaluaciones y Capacitaciones
- Evaluaciones desactivado con badge 'Próximamente'
- Capacitaciones activo con link al menú
- Navbar para navegación en área profesional
- Información del usuario logueado"
```

---

## COMMIT 16: Menú de capacitaciones con íconos

### 📋 Descripción
Crear el menú visual de capacitaciones disponibles, con íconos y estados.

### 🎯 Objetivos
- [ ] Agregar campos `icon`, `color`, `order` al modelo TrainingModule
- [ ] Grid de capacitaciones con cards
- [ ] Íconos de Bootstrap Icons
- [ ] Indicador de activo/próximamente
- [ ] Click lleva al selector de modalidad

### 📁 Archivos a modificar

#### 1. `apps/training/models.py` (AGREGAR campos)

```python
# Agregar a TrainingModule:
icon = models.CharField(
    max_length=50, 
    default='bi-book',
    help_text='Clase de Bootstrap Icons (ej: bi-body-text)'
)
color = models.CharField(
    max_length=20, 
    default='#28a745',
    help_text='Color hex para el card'
)
order = models.PositiveIntegerField(
    default=0,
    help_text='Orden en el menú'
)

class Meta:
    ordering = ['order', 'title']
```

### 📝 Mensaje de Commit
```bash
git commit -m "Commit 16: Menú de capacitaciones con íconos

- Campos icon, color, order agregados a TrainingModule
- Migración de base de datos
- Vista de menú de capacitaciones
- Grid responsive con cards
- Íconos de Bootstrap Icons
- Estados activo/próximamente
- Link al selector de modalidad"
```

---

## COMMIT 17: Selector de modalidad (Presencial/Online)

### 📋 Descripción
Pantalla para elegir entre capacitación presencial u online.

### 🎯 Objetivos
- [ ] Página de selección de modalidad
- [ ] Descripción de cada modalidad
- [ ] Botones para ir a presencial o generar link online

### 📝 Mensaje de Commit
```bash
git commit -m "Commit 17: Selector de modalidad Presencial/Online

- Página de selección al clickear una capacitación
- Descripción de modalidad presencial
- Descripción de modalidad online
- Botones de navegación a cada modalidad
- Diseño consistente con el resto del dashboard"
```

---

# ═══════════════════════════════════════════════════════════════════════════════
# FASE 4: MODO PRESENCIAL
# ═══════════════════════════════════════════════════════════════════════════════

## COMMIT 18: Página de capacitación presencial

### 📋 Descripción
Crear la página de capacitación para uso presencial por el profesional.

### 🎯 Objetivos
- [ ] Video de capacitación embebido
- [ ] Chat con Ergobot
- [ ] Sin registro de trabajadores
- [ ] Diseño limpio para proyección

### 📝 Mensaje de Commit
```bash
git commit -m "Commit 18: Página de capacitación presencial

- Video embebido de YouTube
- Chat con Ergobot integrado
- Diseño optimizado para proyección
- Sin formularios de registro (uso presencial)"
```

---

## COMMIT 19: Quiz simplificado para modo presencial

### 📋 Descripción
Modificar el quiz para modo presencial: mostrar solo el resultado final.

### 🎯 Objetivos
- [ ] Quiz con las mismas preguntas
- [ ] Al finalizar, mostrar SOLO el resultado (score)
- [ ] Sin certificado, sin intentos, sin bloqueos
- [ ] Botón "Generar Planilla" y "Volver"

### 📝 Mensaje de Commit
```bash
git commit -m "Commit 19: Quiz simplificado para modo presencial

- Mismo quiz pero sin reglas de intentos/bloqueo
- Resultado muestra solo el score
- Sin generación de certificado individual
- Botón 'Generar Planilla de Certificado'
- Botón 'Volver a la Capacitación'"
```

---

## COMMIT 20: Generador de planilla PDF grupal

### 📋 Descripción
Crear el PDF de planilla para capacitaciones presenciales grupales.

### 🎯 Objetivos
- [ ] Template PDF con ReportLab
- [ ] Campos: nombre capacitación, responsable, fecha
- [ ] Listado de participantes con líneas para firmar
- [ ] Descarga inmediata del PDF

### 📁 Archivos a crear

```python
# apps/presencial/pdf.py
def build_planilla_presencial_pdf(module, professional, session_date=None):
    """
    Genera una planilla PDF para capacitación presencial.
    
    Incluye:
    - Nombre de la capacitación
    - Datos del responsable (profesional)
    - Fecha
    - Listado con líneas para nombres y firmas
    """
    # ... implementación con ReportLab
```

### 📝 Mensaje de Commit
```bash
git commit -m "Commit 20: Generador de planilla PDF para capacitaciones presenciales

- Template PDF profesional con ReportLab
- Encabezado con nombre de capacitación
- Datos del responsable (profesional)
- Campo de fecha
- Listado de participantes con líneas para:
  * Nombre completo
  * DNI
  * Firma
- Descarga inmediata al presionar botón"
```

---

## COMMIT 21: Modelo PresencialSession e historial

### 📋 Descripción
Crear modelo para registrar sesiones presenciales y mostrar historial.

### 🎯 Objetivos
- [ ] Modelo PresencialSession
- [ ] Registro automático al generar planilla
- [ ] Vista de historial para el profesional

### 📁 Modelo

```python
class PresencialSession(models.Model):
    """Registro de sesiones de capacitación presencial."""
    
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE)
    professional = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    session_date = models.DateField()
    location = models.CharField(max_length=200, blank=True)
    quiz_score = models.PositiveIntegerField(null=True, blank=True)
    quiz_passed = models.BooleanField(default=False)
    planilla_pdf = models.FileField(upload_to='planillas/', null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### 📝 Mensaje de Commit
```bash
git commit -m "Commit 21: Modelo PresencialSession e historial

- Modelo PresencialSession para registro de sesiones
- Campos: module, professional, fecha, ubicación, score, PDF
- Registro automático al generar planilla
- Vista de historial de sesiones presenciales
- Integración con dashboard del profesional"
```

---

# ═══════════════════════════════════════════════════════════════════════════════
# FASE 5: MODO ONLINE (SISTEMA DE LINKS)
# ═══════════════════════════════════════════════════════════════════════════════

## COMMIT 22: Modelo CapacitacionLink

### 📋 Descripción
Crear el modelo para gestionar links únicos de capacitaciones.

### 🎯 Objetivos
- [ ] Modelo CapacitacionLink con UUID
- [ ] Asociación con profesional creador
- [ ] Campo de expiración (opcional)
- [ ] Contador de accesos

### 📁 Modelo

```python
class CapacitacionLink(models.Model):
    """Link único para compartir una capacitación."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    access_count = models.PositiveIntegerField(default=0)
    
    def get_absolute_url(self):
        return f"/c/{self.module.slug}/?ref={self.id}"
```

### 📝 Mensaje de Commit
```bash
git commit -m "Commit 22: Modelo CapacitacionLink para links compartibles

- Modelo CapacitacionLink con UUID único
- Asociación con módulo y profesional creador
- Campo de expiración opcional
- Contador de accesos para estadísticas
- Método get_absolute_url() para generar URL"
```

---

## COMMIT 23: Generación y copia de links

### 📋 Descripción
Interfaz para generar y copiar links de capacitaciones.

### 🎯 Objetivos
- [ ] Botón "Generar Link"
- [ ] Mostrar link generado
- [ ] Botón "Copiar" que copia al portapapeles
- [ ] Feedback visual de copiado

### 📝 Mensaje de Commit
```bash
git commit -m "Commit 23: Generación y copia de links de capacitaciones

- Vista para generar nuevo CapacitacionLink
- UI mostrando el link generado
- Botón 'Copiar' con JavaScript clipboard API
- Feedback visual al copiar
- Historial de links generados"
```

---

## COMMIT 24: Compartir links por email

### 📋 Descripción
Funcionalidad para enviar links de capacitación por email a múltiples destinatarios.

### 🎯 Objetivos
- [ ] Modal o formulario para ingresar emails
- [ ] Soporte para múltiples emails (separados por coma)
- [ ] Envío de email con el link
- [ ] Registro de envíos (LinkShareLog)

### 📁 Modelo adicional

```python
class LinkShareLog(models.Model):
    """Registro de envíos de links por email."""
    
    link = models.ForeignKey(CapacitacionLink, on_delete=models.CASCADE)
    shared_to_email = models.EmailField()
    shared_at = models.DateTimeField(auto_now_add=True)
    opened = models.BooleanField(default=False)  # Para tracking futuro
```

### 📝 Mensaje de Commit
```bash
git commit -m "Commit 24: Compartir links de capacitación por email

- Modal para ingresar emails destinatarios
- Soporte para múltiples emails separados por coma
- Envío de email con link y descripción
- Modelo LinkShareLog para registro
- Validación de emails"
```

---

## COMMIT 25: Rutas públicas /c/<slug>/ para trabajadores

### 📋 Descripción
Crear las rutas de acceso público para trabajadores vía links compartidos.

### 🎯 Objetivos
- [ ] URL /c/<slug>/ para landing de capacitación
- [ ] Mantener lógica actual de registro/login trainees
- [ ] Tracking de acceso vía parámetro ref
- [ ] Incrementar contador de accesos

### 📁 Archivos

```python
# apps/training/urls_public.py
urlpatterns = [
    path('<slug:module_slug>/', views.public_landing, name='training_public'),
]
```

### 📝 Mensaje de Commit
```bash
git commit -m "Commit 25: Rutas públicas /c/<slug>/ para trabajadores

- URL corta /c/<slug>/ para acceso vía link
- Landing de capacitación con registro/login
- Tracking de parámetro ref (CapacitacionLink)
- Incremento de contador de accesos
- Toda la lógica de capacitación existente funcional"
```

---

# ═══════════════════════════════════════════════════════════════════════════════
# FASE 6: MEJORAS, TESTING Y PULIDO
# ═══════════════════════════════════════════════════════════════════════════════

## COMMIT 26: Panel de perfil del profesional

### 📋 Descripción
Completar el panel de perfil del profesional con edición de datos y estadísticas.

### 🎯 Objetivos
- [ ] Vista de perfil con todos los datos
- [ ] Formulario de edición
- [ ] Cambio de contraseña
- [ ] Estadísticas básicas (capacitaciones realizadas, links generados)

### 📝 Mensaje de Commit
```bash
git commit -m "Commit 26: Panel de perfil del profesional

- Vista de perfil completa
- Edición de datos personales
- Cambio de contraseña
- Estadísticas: capacitaciones, links, sesiones presenciales
- Información de suscripción (preparado para futuro)"
```

---

## COMMIT 27: Agregar capacitaciones adicionales (datos)

### 📋 Descripción
Crear fixtures o migrations de datos para más capacitaciones.

### 🎯 Objetivos
- [ ] Capacitación de Riesgo Eléctrico (placeholder)
- [ ] Capacitación de Trabajo en Altura (placeholder)
- [ ] Capacitación de Prevención de Incendios (placeholder)
- [ ] Íconos y colores para cada una

### 📝 Mensaje de Commit
```bash
git commit -m "Commit 27: Datos de capacitaciones adicionales (placeholders)

- Módulo Riesgo Eléctrico (is_active=False)
- Módulo Trabajo en Altura (is_active=False)
- Módulo Prevención de Incendios (is_active=False)
- Íconos y colores configurados
- Fixture para cargar datos"
```

---

## COMMIT 28: Testing, documentación y correcciones finales

### 📋 Descripción
Tests, documentación y correcciones finales para el MVP.

### 🎯 Objetivos
- [ ] Tests de flujos principales
- [ ] Documentación de uso
- [ ] README actualizado
- [ ] Corrección de bugs encontrados
- [ ] Optimizaciones de rendimiento

### 📝 Mensaje de Commit
```bash
git commit -m "Commit 28: Testing, documentación y correcciones - MVP completo

- Tests de autenticación dual
- Tests de flujo de capacitaciones
- Tests de generación de links
- README actualizado con instrucciones
- Documentación de API interna
- Correcciones de bugs menores
- MVP de ErgoSolutions completo"
```

---

# ═══════════════════════════════════════════════════════════════════════════════
# RESUMEN FINAL
# ═══════════════════════════════════════════════════════════════════════════════

## Progreso Total

| Fase | Commits | Estado |
|------|---------|--------|
| **1. Fundamentos** | 9-11 | ⬜ Pendiente |
| **2. Landing + Auth** | 12-14 | ⬜ Pendiente |
| **3. Dashboard + Menú** | 15-17 | ⬜ Pendiente |
| **4. Modo Presencial** | 18-21 | ⬜ Pendiente |
| **5. Modo Online** | 22-25 | ⬜ Pendiente |
| **6. Mejoras + Testing** | 26-28 | ⬜ Pendiente |

## Commits Totales: 20 (del 9 al 28)

## Tiempo Estimado: 8-12 semanas

---

## ¿Listo para comenzar?

El próximo paso es el **Commit 9: Refactorizar TraineeUser → CustomUser**.

Este commit es fundamental porque todos los demás dependen de tener el modelo de usuario correctamente configurado con soporte para ambos tipos de usuarios.

---

*Documento generado para ErgoSolutions*  
*Fecha: Febrero 2026*
