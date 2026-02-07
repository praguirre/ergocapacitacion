# apps/landing/urls.py
# ============================================================================
# COMMIT 11: URLs del landing principal
# ============================================================================

from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    path('', views.home, name='home'),
]