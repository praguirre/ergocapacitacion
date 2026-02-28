# apps/training/models.py
# ============================================================================
# COMMIT 16: Agregados campos icon, color, order para menu visual
# ============================================================================

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class TrainingModule(models.Model):
    slug = models.SlugField(unique=True, help_text="Identificador único para la URL.")
    title = models.CharField(max_length=200, verbose_name="Título del módulo")
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Descripción corta",
        help_text="Descripción breve para mostrar en el menú de capacitaciones.",
    )
    youtube_id = models.CharField(
        max_length=32,
        help_text="Solo el ID del video (ej: IIgZp_NbsAE), no la URL completa.",
    )

    # Contenido en formato Markdown para la IA y el Front
    intro_md = models.TextField(blank=True, default="", verbose_name="Introducción (Markdown)")
    material_md = models.TextField(blank=True, default="", verbose_name="Material de lectura")
    transcript_md = models.TextField(blank=True, default="", verbose_name="Transcripción del video")

    # =========================================================================
    # COMMIT 16: Campos para menu visual
    # =========================================================================
    icon = models.CharField(
        max_length=50,
        default="bi-book",
        help_text="Clase de Bootstrap Icons (ej: bi-body-text, bi-lightning-charge)",
    )
    color = models.CharField(
        max_length=20,
        default="#28a745",
        help_text="Color hex para el card (ej: #28a745)",
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Orden de aparición en el menú (menor = primero)",
    )

    is_active = models.BooleanField(default=False, verbose_name="¿Está activo?")

    is_personalized = models.BooleanField(
        default=False,
        verbose_name="¿Es personalizada?",
        help_text="Si es True, solo los profesionales asignados pueden ver esta capacitación.",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_trainings",
        verbose_name="Solicitada por",
        help_text="Profesional que solicitó esta capacitación personalizada.",
    )
    assigned_professionals = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="personalized_trainings",
        verbose_name="Profesionales asignados",
        help_text="Profesionales que pueden ver y acceder a esta capacitación.",
    )
    company_name_custom = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Empresa/Cliente",
        help_text="Nombre de la empresa o cliente para esta capacitación personalizada.",
    )
    custom_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notas internas",
        help_text="Notas internas sobre esta capacitación (no visibles para los usuarios).",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "title"]
        verbose_name = "Módulo de capacitación"
        verbose_name_plural = "Módulos de capacitación"

    def __str__(self) -> str:
        return f"{self.title} ({self.slug})"

    @classmethod
    def get_general_modules(cls):
        return cls.objects.filter(is_personalized=False)

    @classmethod
    def get_personalized_for_user(cls, user):
        if not getattr(user, "is_authenticated", False):
            return cls.objects.none()
        return cls.objects.filter(is_personalized=True, assigned_professionals=user)

    @classmethod
    def get_all_for_user(cls, user):
        if not getattr(user, "is_authenticated", False):
            return cls.get_general_modules()
        return cls.objects.filter(
            models.Q(is_personalized=False)
            | models.Q(is_personalized=True, assigned_professionals=user)
        ).distinct()


class CapacitacionLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(
        TrainingModule,
        on_delete=models.CASCADE,
        related_name="capacitacion_links",
        verbose_name="Módulo de capacitación",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="capacitacion_links",
        verbose_name="Creado por",
    )
    label = models.CharField(
        max_length=120,
        blank=True,
        default="",
        verbose_name="Etiqueta",
        help_text="Nombre interno para identificar el link (ej: Planta Norte - Turno Mañana).",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Vence el",
        help_text="Opcional. Si se define, el link deja de ser usable después de esta fecha/hora.",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    access_count = models.PositiveIntegerField(default=0, verbose_name="Cantidad de accesos")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Link de capacitación"
        verbose_name_plural = "Links de capacitación"

    def __str__(self):
        return f"{self.module.title} - {self.id}"

    @property
    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    @property
    def is_usable(self) -> bool:
        return self.is_active and not self.is_expired

    def get_absolute_url(self) -> str:
        return f"/c/{self.module.slug}/?ref={self.id}"


class LinkShareLog(models.Model):
    """Registro de envíos de links por email."""

    link = models.ForeignKey(
        CapacitacionLink,
        on_delete=models.CASCADE,
        related_name="share_logs",
        verbose_name="Link",
    )
    shared_to_email = models.EmailField(verbose_name="Email destinatario")
    shared_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-shared_at"]
        verbose_name = "Envío de link"
        verbose_name_plural = "Envíos de links"

    def __str__(self):
        return f"{self.link} → {self.shared_to_email}"
