# apps/certificates/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Lista de certificados del usuario
    path("", views.my_certificates, name="certificates_list"),
    
    # Descargar PDF (fuerza descarga)
    path("<uuid:cert_id>/download/", views.download_certificate, name="certificate_download"),
    
    # Ver PDF en navegador
    path("<uuid:cert_id>/view/", views.view_certificate, name="certificate_view"),
]