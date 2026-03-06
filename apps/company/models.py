# apps/company/models.py
# ============================================================================
# COMMIT 30: Modelo CompanyProfile para datos específicos de empresa
# ============================================================================

from django.conf import settings
from django.db import models


class CompanyProfile(models.Model):
    """
    Perfil extendido para usuarios de tipo 'company'.
    Almacena datos empresariales que no corresponden al modelo genérico CustomUser.
    Relación OneToOne con CustomUser(user_type='company').
    """

    class AccountStatus(models.TextChoices):
        ACTIVE = 'active', 'Activa'
        PENDING = 'pending_validation', 'Pendiente de validación'
        SUSPENDED = 'suspended', 'Suspendida'
        INACTIVE = 'inactive', 'Inactiva'

    # =========================================================================
    # Relación con el usuario
    # =========================================================================
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='company_profile',
        verbose_name='Usuario de acceso',
        limit_choices_to={'user_type': 'company'},
    )

    # =========================================================================
    # Datos de la empresa
    # =========================================================================
    razon_social = models.CharField(
        max_length=300,
        verbose_name='Razón social',
    )
    nombre_comercial = models.CharField(
        max_length=300,
        blank=True,
        default='',
        verbose_name='Nombre comercial',
        help_text='Nombre comercial o fantasía (opcional).',
    )
    cuit = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='CUIT',
        help_text='CUIT de la empresa (formato: XX-XXXXXXXX-X o solo dígitos).',
    )
    rubro = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name='Rubro / Actividad',
    )
    cantidad_trabajadores = models.PositiveIntegerField(
        default=0,
        verbose_name='Cantidad aproximada de trabajadores',
    )

    # =========================================================================
    # Contacto principal
    # =========================================================================
    contacto_nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre del contacto principal',
    )
    contacto_cargo = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name='Cargo del contacto',
    )
    contacto_telefono = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='Teléfono de contacto',
    )

    # =========================================================================
    # Ubicación
    # =========================================================================
    domicilio = models.CharField(
        max_length=400,
        blank=True,
        default='',
        verbose_name='Domicilio / Ubicación principal',
    )
    localidad = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name='Localidad',
    )
    provincia = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Provincia',
    )

    # =========================================================================
    # Estado de cuenta
    # =========================================================================
    account_status = models.CharField(
        max_length=30,
        choices=AccountStatus.choices,
        default=AccountStatus.ACTIVE,
        verbose_name='Estado de cuenta',
    )

    # =========================================================================
    # Logo (opcional, para futuro)
    # =========================================================================
    logo = models.ImageField(
        upload_to='company_logos/',
        blank=True,
        null=True,
        verbose_name='Logo de la empresa',
    )

    # =========================================================================
    # Metadatos
    # =========================================================================
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil de Empresa'
        verbose_name_plural = 'Perfiles de Empresas'
        ordering = ['razon_social']

    def __str__(self):
        nombre = self.nombre_comercial or self.razon_social
        return f"{nombre} (CUIT: {self.cuit})"

    @property
    def display_name(self):
        """Nombre corto para mostrar en la UI."""
        return self.nombre_comercial or self.razon_social


class CompanyWorker(models.Model):
    """Relación formal entre una empresa y un trabajador (trainee)."""

    company = models.ForeignKey(
        CompanyProfile, on_delete=models.CASCADE,
        related_name='workers', verbose_name='Empresa',
    )
    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='company_assignments', verbose_name='Trabajador',
        limit_choices_to={'user_type': 'trainee'},
    )
    employee_code = models.CharField(
        max_length=50, blank=True, default='',
        verbose_name='Legajo',
    )
    department = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name='Sector',
    )
    position = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name='Puesto',
    )
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    start_date = models.DateField(
        null=True, blank=True,
        verbose_name='Fecha inicio',
    )
    end_date = models.DateField(
        null=True, blank=True,
        verbose_name='Fecha baja',
    )
    notes = models.TextField(
        blank=True, default='',
        verbose_name='Notas',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Trabajador de empresa'
        verbose_name_plural = 'Trabajadores de empresa'
        ordering = ['company', 'worker__last_name', 'worker__first_name']
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'worker'],
                name='uq_company_worker',
            ),
        ]

    def __str__(self):
        return f"{self.worker.display_name} → {self.company.display_name}"


class AgendaEvent(models.Model):
    """Evento genérico de agenda para empresas."""

    class EventType(models.TextChoices):
        TRAINING_DUE = 'training_due', 'Vencimiento de capacitación'
        CERTIFICATE_EXPIRY = 'certificate_expiry', 'Vencimiento de certificado'
        PROFESSIONAL_VISIT = 'professional_visit', 'Visita de profesional'
        EVALUATION_DUE = 'evaluation_due', 'Evaluación pendiente'
        REMINDER = 'reminder', 'Recordatorio'
        OTHER = 'other', 'Otro'

    class EventStatus(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        COMPLETED = 'completed', 'Completado'
        OVERDUE = 'overdue', 'Vencido'
        CANCELLED = 'cancelled', 'Cancelado'

    class Priority(models.TextChoices):
        LOW = 'low', 'Baja'
        MEDIUM = 'medium', 'Media'
        HIGH = 'high', 'Alta'
        URGENT = 'urgent', 'Urgente'

    company = models.ForeignKey(
        CompanyProfile, on_delete=models.CASCADE,
        related_name='agenda_events', verbose_name='Empresa',
    )
    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='agenda_events',
        verbose_name='Trabajador relacionado',
    )
    title = models.CharField(max_length=300, verbose_name='Título')
    description = models.TextField(blank=True, default='', verbose_name='Descripción')
    event_type = models.CharField(
        max_length=30, choices=EventType.choices,
        default=EventType.REMINDER, verbose_name='Tipo de evento',
    )
    status = models.CharField(
        max_length=20, choices=EventStatus.choices,
        default=EventStatus.PENDING, verbose_name='Estado',
    )
    priority = models.CharField(
        max_length=10, choices=Priority.choices,
        default=Priority.MEDIUM, verbose_name='Prioridad',
    )
    start_at = models.DateTimeField(
        null=True, blank=True, verbose_name='Fecha/hora de inicio',
    )
    due_at = models.DateTimeField(verbose_name='Fecha/hora límite')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='created_agenda_events',
        verbose_name='Creado por',
    )
    assigned_professional = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_agenda_events',
        verbose_name='Profesional asignado',
    )
    related_object_type = models.CharField(
        max_length=50, blank=True, default='',
        verbose_name='Tipo de objeto relacionado',
        help_text='Ej: certificate, training_module',
    )
    related_object_id = models.CharField(
        max_length=100, blank=True, default='',
        verbose_name='ID del objeto relacionado',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Evento de agenda'
        verbose_name_plural = 'Eventos de agenda'
        ordering = ['due_at', '-priority']
        indexes = [
            models.Index(fields=['company', 'status', 'due_at']),
            models.Index(fields=['company', 'event_type', 'due_at']),
        ]

    def __str__(self):
        return f"[{self.get_event_type_display()}] {self.title}"

    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.status == self.EventStatus.PENDING and self.due_at < timezone.now()
