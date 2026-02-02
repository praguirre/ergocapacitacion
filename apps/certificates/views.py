# apps/certificates/views.py
"""
Vistas para la gestión de certificados.
"""

from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404

from .models import Certificate


@login_required
def download_certificate(request, cert_id):
    """
    Descarga el PDF del certificado.
    
    Solo el dueño del certificado puede descargarlo.
    
    URL: /certificados/<uuid:cert_id>/download/
    """
    # Buscamos el certificado por UUID
    certificate = get_object_or_404(Certificate, id=cert_id)
    
    # Verificar que el usuario es el dueño
    if certificate.user != request.user:
        raise Http404("Certificado no encontrado")
    
    # Verificar que el archivo existe
    if not certificate.pdf_file:
        raise Http404("El archivo PDF no está disponible")
    
    # Servir el archivo
    try:
        # Generar nombre de archivo con el nombre del usuario
        user_name = getattr(certificate.user, 'full_name', '') or 'usuario'
        # Limpiar el nombre: reemplazar espacios y caracteres especiales
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in user_name)
        safe_name = safe_name.replace(' ', '_').strip('_') or 'usuario'
        filename = f"certificado_{safe_name}.pdf"
        
        response = FileResponse(
            certificate.pdf_file.open("rb"),
            as_attachment=True,
            filename=filename
        )
        return response
    except Exception:
        raise Http404("Error al acceder al archivo")


@login_required  
def view_certificate(request, cert_id):
    """
    Muestra el PDF del certificado en el navegador (sin descargar).
    
    URL: /certificados/<uuid:cert_id>/view/
    """
    certificate = get_object_or_404(Certificate, id=cert_id)
    
    if certificate.user != request.user:
        raise Http404("Certificado no encontrado")
    
    if not certificate.pdf_file:
        raise Http404("El archivo PDF no está disponible")
    
    try:
        # Generar nombre de archivo con el nombre del usuario
        user_name = getattr(certificate.user, 'full_name', '') or 'usuario'
        # Limpiar el nombre: reemplazar espacios y caracteres especiales
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in user_name)
        safe_name = safe_name.replace(' ', '_').strip('_') or 'usuario'
        filename = f"certificado_{safe_name}.pdf"
        
        response = FileResponse(
            certificate.pdf_file.open("rb"),
            content_type="application/pdf"
        )
        # Content-Disposition: inline hace que se muestre en el navegador
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        return response
    except Exception:
        raise Http404("Error al acceder al archivo")


@login_required
def my_certificates(request):
    """
    Lista todos los certificados del usuario actual.
    
    URL: /certificados/
    
    TODO: Implementar template si se necesita una vista de lista.
    """
    certificates = Certificate.objects.filter(user=request.user).select_related("module")
    
    # Por ahora retornamos JSON simple (se puede cambiar a render con template)
    from django.http import JsonResponse
    
    data = [
        {
            "id": str(c.id),
            "module": c.module.title,
            "issued_at": c.issued_at.isoformat(),
            "valid_until": c.valid_until.isoformat(),
            "is_valid": c.is_valid,
            "download_url": f"/certificados/{c.id}/download/",
        }
        for c in certificates
    ]
    
    return JsonResponse({"certificates": data})







"""
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404

from .models import Certificate


@login_required
def download_certificate(request, cert_id):

    # Buscamos el certificado por UUID
    certificate = get_object_or_404(Certificate, id=cert_id)
    
    # Verificar que el usuario es el dueño
    if certificate.user != request.user:
        raise Http404("Certificado no encontrado")
    
    # Verificar que el archivo existe
    if not certificate.pdf_file:
        raise Http404("El archivo PDF no está disponible")
    
    # Servir el archivo
    try:
        response = FileResponse(
            certificate.pdf_file.open("rb"),
            as_attachment=True,
            filename=f"certificado_{certificate.module.slug}.pdf"
        )
        return response
    except Exception:
        raise Http404("Error al acceder al archivo")


@login_required  
def view_certificate(request, cert_id):

    certificate = get_object_or_404(Certificate, id=cert_id)
    
    if certificate.user != request.user:
        raise Http404("Certificado no encontrado")
    
    if not certificate.pdf_file:
        raise Http404("El archivo PDF no está disponible")
    
    try:
        response = FileResponse(
            certificate.pdf_file.open("rb"),
            content_type="application/pdf"
        )
        # Content-Disposition: inline hace que se muestre en el navegador
        response["Content-Disposition"] = f'inline; filename="certificado_{certificate.module.slug}.pdf"'
        return response
    except Exception:
        raise Http404("Error al acceder al archivo")


@login_required
def my_certificates(request):

    certificates = Certificate.objects.filter(user=request.user).select_related("module")
    
    # Por ahora retornamos JSON simple (se puede cambiar a render con template)
    from django.http import JsonResponse
    
    data = [
        {
            "id": str(c.id),
            "module": c.module.title,
            "issued_at": c.issued_at.isoformat(),
            "valid_until": c.valid_until.isoformat(),
            "is_valid": c.is_valid,
            "download_url": f"/certificados/{c.id}/download/",
        }
        for c in certificates
    ]
    
    return JsonResponse({"certificates": data})
"""