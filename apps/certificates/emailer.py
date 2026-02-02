# apps/certificates/emailer.py
# ============================================================================
# COMMIT 8: Modificado para enviar certificados a empleador y responsable SySO
# ============================================================================
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
from typing import Optional, List

from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


def send_certificate_emails(
    to_email: str,
    pdf_bytes: bytes,
    filename: str,
    user_name: Optional[str] = None,
    module_title: Optional[str] = None,
    # =========================================================================
    # ✅ COMMIT 8: Nuevos parámetros para emails adicionales
    # =========================================================================
    employer_email: Optional[str] = None,
    safety_responsible_email: Optional[str] = None,
    company_name: Optional[str] = None,
    # =========================================================================
) -> bool:
    """
    Envía el certificado PDF por email al usuario, empleador, responsable SySO y admin.
    
    Args:
        to_email: Email del destinatario principal (usuario/trabajador)
        pdf_bytes: Contenido del PDF en bytes
        filename: Nombre del archivo adjunto (ej: "certificado_abc123.pdf")
        user_name: Nombre del usuario para personalizar el mensaje
        module_title: Título del módulo para el asunto
        employer_email: Email del empleador (COMMIT 8)
        safety_responsible_email: Email del responsable de Seg. e Higiene (COMMIT 8)
        company_name: Nombre de la empresa (COMMIT 8)
    
    Returns:
        bool: True si al menos el envío al usuario fue exitoso
    
    Raises:
        Exception: Si hay error en el envío principal (para que el caller pueda manejarlo)
    """
    subject = f"Certificado de Capacitación - {module_title or 'Ergonomía'}"
    
    # ==========================================================================
    # EMAIL 1: Al trabajador/usuario (PRINCIPAL - obligatorio)
    # ==========================================================================
    greeting = f"Hola {user_name}," if user_name else "Estimado/a,"
    
    body_usuario = f"""
{greeting}

¡Felicitaciones! Has completado exitosamente la capacitación.

Adjunto encontrarás tu certificado en formato PDF.

Este certificado tiene una validez de 1 (un) año desde la fecha de emisión.
Conservalo como constancia de tu capacitación.

Saludos cordiales,
Sistema de Capacitación en Ergonomía
    """.strip()
    
    email = EmailMessage(
        subject=subject,
        body=body_usuario,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    email.attach(filename, pdf_bytes, "application/pdf")
    
    # Intentar enviar al usuario
    try:
        sent_count = email.send(fail_silently=False)
        logger.info(f"Certificado enviado a trabajador {to_email}: {sent_count} email(s)")
    except Exception as e:
        logger.error(f"Error enviando certificado a {to_email}: {e}")
        raise  # Re-lanzamos para que el caller decida qué hacer

    # ==========================================================================
    # ✅ COMMIT 8: EMAIL 2 - Al empleador (si está configurado)
    # ==========================================================================
    if employer_email and employer_email.strip():
        try:
            body_empleador = f"""
Estimado/a,

Le informamos que el trabajador {user_name or "N/A"} ha completado exitosamente la capacitación en Ergonomía y Prevención de Riesgos Laborales.

Datos del trabajador:
• Nombre: {user_name or "N/A"}
• Email: {to_email}
• Empresa: {company_name or "N/A"}
• Módulo completado: {module_title or "Ergonomía"}

Adjunto encontrará el certificado correspondiente en formato PDF.

Este certificado tiene una validez de 1 (un) año desde la fecha de emisión.

Saludos cordiales,
Sistema de Capacitación en Ergonomía
            """.strip()
            
            email_empleador = EmailMessage(
                subject=f"[Empleador] {subject} - {user_name or to_email}",
                body=body_empleador,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[employer_email.strip()],
            )
            email_empleador.attach(filename, pdf_bytes, "application/pdf")
            email_empleador.send(fail_silently=True)  # No falla si no llega
            logger.info(f"Certificado enviado a empleador: {employer_email}")
        except Exception as e:
            logger.warning(f"No se pudo enviar certificado al empleador {employer_email}: {e}")

    # ==========================================================================
    # ✅ COMMIT 8: EMAIL 3 - Al responsable de Seguridad e Higiene (si está configurado)
    # ==========================================================================
    if safety_responsible_email and safety_responsible_email.strip():
        try:
            body_syso = f"""
Estimado/a Responsable de Seguridad e Higiene,

Le informamos que el siguiente trabajador ha completado exitosamente la capacitación en Ergonomía y Prevención de Riesgos Laborales:

Datos del trabajador:
• Nombre: {user_name or "N/A"}
• Email: {to_email}
• Empresa: {company_name or "N/A"}
• Módulo completado: {module_title or "Ergonomía"}

Adjunto encontrará el certificado correspondiente en formato PDF.

Este certificado tiene una validez de 1 (un) año desde la fecha de emisión.
Por favor, conserve este registro para la documentación de capacitaciones del personal.

Saludos cordiales,
Sistema de Capacitación en Ergonomía
            """.strip()
            
            email_syso = EmailMessage(
                subject=f"[Resp. SySO] {subject} - {user_name or to_email}",
                body=body_syso,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[safety_responsible_email.strip()],
            )
            email_syso.attach(filename, pdf_bytes, "application/pdf")
            email_syso.send(fail_silently=True)  # No falla si no llega
            logger.info(f"Certificado enviado a responsable SySO: {safety_responsible_email}")
        except Exception as e:
            logger.warning(f"No se pudo enviar certificado al resp. SySO {safety_responsible_email}: {e}")

    # ==========================================================================
    # EMAIL 4: Al admin (si está configurado) - Original
    # ==========================================================================
    admin_email = getattr(settings, "ADMIN_EMAIL", None)
    if admin_email and admin_email != to_email:
        try:
            admin_body = f"""
Nuevo certificado emitido.

Datos del trabajador:
• Usuario: {user_name or "N/A"} ({to_email})
• Empresa: {company_name or "N/A"}
• Módulo: {module_title or "N/A"}

Notificaciones enviadas a:
• Trabajador: {to_email}
• Empleador: {employer_email or "No configurado"}
• Resp. SySO: {safety_responsible_email or "No configurado"}

El certificado se adjunta a este email.
            """.strip()
            
            admin_msg = EmailMessage(
                subject=f"[ADMIN] {subject} - {user_name or to_email}",
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
