# apps/training/models.py
# ============================================================================
# COMMIT 16: Agregados campos icon, color, order para menu visual
# ============================================================================

from django.db import models


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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "title"]
        verbose_name = "Módulo de capacitación"
        verbose_name_plural = "Módulos de capacitación"

    def __str__(self) -> str:
        return f"{self.title} ({self.slug})"
