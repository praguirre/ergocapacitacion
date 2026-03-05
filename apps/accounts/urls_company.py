# apps/accounts/urls_company.py
# ============================================================================
# COMMIT 32: URLs de autenticación para empresas
# ============================================================================

from django.urls import path
from . import views_company
from . import views_professional  # reutilizar logout

urlpatterns = [
    path('registro/', views_company.company_register, name='company_register'),
    path('login/', views_company.company_login, name='company_login'),
    path('logout/', views_professional.logout_view, name='company_logout'),
]
