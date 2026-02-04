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
        