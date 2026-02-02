# apps/certificates/emailer.py
"""
Envío de certificados por email.

Configuración requerida en settings.py:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Para desarrollo
    # O para producción:
    # EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    # EMAIL_HOST = 'smtp.gmail.com'
    # EMAIL_PORT = 587
    # EMAIL_USE_TLS = True
    # EMAIL_HOST_USER = 'tu_email@gmail.com'
    # EMAIL_HOST_PASSWORD = 'tu_app_password'
    
    # Email del admin que recibe copia
    ADMIN_EMAIL = 'admin@example.com'  # Opcional
"""

import logging
from typing import Optional

from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


def send_certificate_emails(
    to_email: str,
    pdf_bytes: bytes,
    filename: str,
    user_name: Optional[str] = None,
    module_title: Optional[str] = None,
) -> bool:
    """
    Envía el certificado PDF por email al usuario y opcionalmente al admin.
    
    Args:
        to_email: Email del destinatario principal (usuario)
        pdf_bytes: Contenido del PDF en bytes
        filename: Nombre del archivo adjunto (ej: "certificado_abc123.pdf")
        user_name: Nombre del usuario para personalizar el mensaje
        module_title: Título del módulo para el asunto
    
    Returns:
        bool: True si el envío fue exitoso, False en caso contrario
    
    Raises:
        Exception: Si hay error en el envío (para que el caller pueda manejarlo)
    """
    subject = f"Certificado de Capacitación - {module_title or 'Ergonomía'}"
    
    # Personalizar el mensaje
    greeting = f"Hola {user_name}," if user_name else "Estimado/a,"
    
    body = f"""
{greeting}

¡Felicitaciones! Has completado exitosamente la capacitación.

Adjunto encontrarás tu certificado en formato PDF.

Este certificado tiene una validez de 1 (un) año desde la fecha de emisión.
Conservalo como constancia de tu capacitación.

Saludos cordiales,
Sistema de Capacitación en Ergonomía
    """.strip()
    
    # Email principal al usuario
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    email.attach(filename, pdf_bytes, "application/pdf")
    
    # Intentar enviar al usuario
    try:
        sent_count = email.send(fail_silently=False)
        logger.info(f"Certificado enviado a {to_email}: {sent_count} email(s)")
    except Exception as e:
        logger.error(f"Error enviando certificado a {to_email}: {e}")
        raise  # Re-lanzamos para que el caller decida qué hacer
    
    # Enviar copia al admin (si está configurado)
    admin_email = getattr(settings, "ADMIN_EMAIL", None)
    if admin_email and admin_email != to_email:
        try:
            admin_body = f"""
Nuevo certificado emitido.

Usuario: {user_name or "N/A"} ({to_email})
Módulo: {module_title or "N/A"}

El certificado se adjunta a este email.
            """.strip()
            
            admin_msg = EmailMessage(
                subject=f"[ADMIN] {subject}",
                body=admin_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[admin_email],
            )
            admin_msg.attach(filename, pdf_bytes, "application/pdf")
            admin_msg.send(fail_silently=True)  # No falla si el admin no recibe
            logger.info(f"Copia de certificado enviada al admin: {admin_email}")
        except Exception as e:
            # No re-lanzamos, el envío principal ya fue exitoso
            logger.warning(f"No se pudo enviar copia al admin: {e}")
    
    return True