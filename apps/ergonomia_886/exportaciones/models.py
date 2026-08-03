"""Persistencia de documentos generados y auditoría de descargas."""

from __future__ import annotations

import hashlib
import json

from django.conf import settings
from django.db import models

from apps.ergonomia_886.planillas.models import Evaluacion


class TipoDocumento(models.TextChoices):
    PLANILLA_OFICIAL = "planilla_oficial", "Planilla oficial (PDF SRT)"
    PROTOCOLO_COMPLETO = "protocolo_completo", "Protocolo completo (PDF SRT)"
    DETALLE_FACTOR = "detalle_factor", "Detalle técnico de un factor"
    INFORME_FACTOR = "informe_factor", "Informe profesional de un factor"
    INFORME_EVALUACION = "informe_evaluacion", "Informe profesional consolidado"
    PAQUETE_ZIP = "paquete_zip", "Paquete documental (ZIP)"
    EXCEL_EDITABLE = "excel_editable", "Copia de trabajo editable (XLS)"


class EstadoInforme(models.TextChoices):
    PENDIENTE = "pendiente", "Pendiente"
    EN_PROCESO = "en_proceso", "En proceso"
    LISTO = "listo", "Listo"
    ERROR = "error", "Error"
    OBSOLETO = "obsoleto", "Obsoleto (los datos cambiaron)"


def payload_fingerprint(payload: dict) -> str:
    """Huella estable del payload que alimentó al modelo."""
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class GeneratedReport(models.Model):
    """Informe profesional redactado por el LLM, persistido y versionado."""

    evaluacion = models.ForeignKey(
        Evaluacion,
        on_delete=models.CASCADE,
        related_name="informes_generados",
    )
    tipo = models.CharField(max_length=32, choices=TipoDocumento.choices)
    factor_slug = models.SlugField(blank=True, default="")

    estado = models.CharField(
        max_length=16,
        choices=EstadoInforme.choices,
        default=EstadoInforme.PENDIENTE,
    )

    payload_json = models.JSONField(
        default=dict,
        blank=True,
        help_text="Payload exacto que se envió al modelo. Es la evidencia.",
    )
    inputs_hash = models.CharField(max_length=64, db_index=True)
    contenido_markdown = models.TextField(blank=True, default="")

    modelo_llm = models.CharField(max_length=64, blank=True, default="")
    prompt_version = models.CharField(max_length=16, blank=True, default="")
    schema_version = models.CharField(max_length=16, default="1.0.0")
    tokens_prompt = models.PositiveIntegerField(null=True, blank=True)
    tokens_respuesta = models.PositiveIntegerField(null=True, blank=True)
    duracion_ms = models.PositiveIntegerField(null=True, blank=True)
    error_detalle = models.TextField(blank=True, default="")

    generado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Informe generado"
        verbose_name_plural = "Informes generados"
        ordering = ["-creado_en"]
        indexes = [
            models.Index(fields=["evaluacion", "tipo", "factor_slug"]),
            models.Index(fields=["inputs_hash"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["evaluacion", "tipo", "factor_slug", "inputs_hash"],
                name="uniq_informe_por_huella",
            )
        ]

    def __str__(self) -> str:
        return f"{self.get_tipo_display()} · evaluación {self.evaluacion_id}"

    @property
    def vigente(self) -> bool:
        return self.estado == EstadoInforme.LISTO


class ExportAudit(models.Model):
    """Registro de cada descarga. Nunca guarda el contenido del documento."""

    evaluacion = models.ForeignKey(
        Evaluacion,
        on_delete=models.CASCADE,
        related_name="descargas",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    tipo = models.CharField(max_length=32, choices=TipoDocumento.choices)
    detalle = models.CharField(
        max_length=120,
        blank=True,
        default="",
        help_text="Slug de planilla o factor. Nunca datos personales.",
    )
    bytes_entregados = models.PositiveIntegerField(default=0)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Descarga de export"
        verbose_name_plural = "Descargas de export"
        ordering = ["-creado_en"]
        indexes = [models.Index(fields=["evaluacion", "creado_en"])]
