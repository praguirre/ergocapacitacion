from django.db import models

class TrainingModule(models.Model):
    slug = models.SlugField(unique=True, help_text="Identificador único para la URL.")
    title = models.CharField(max_length=200, verbose_name="Título del módulo")
    youtube_id = models.CharField(
        max_length=32,
        help_text="Solo el ID del video (ej: IIgZp_NbsAE), no la URL completa."
    )

    # Contenido en formato Markdown para la IA y el Front
    intro_md = models.TextField(blank=True, default="", verbose_name="Introducción (Markdown)")
    material_md = models.TextField(blank=True, default="", verbose_name="Material de lectura")
    transcript_md = models.TextField(blank=True, default="", verbose_name="Transcripción del video")

    is_active = models.BooleanField(default=False, verbose_name="¿Está activo?")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_active", "-updated_at"]
        verbose_name = "Módulo de capacitación"
        verbose_name_plural = "Módulos de capacitación"

    def __str__(self) -> str:
        return f"{self.title} ({self.slug})"