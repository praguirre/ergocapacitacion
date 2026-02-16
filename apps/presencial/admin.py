# apps/presencial/admin.py
# ============================================================================
# COMMIT 21: Admin de sesiones presenciales
# ============================================================================

from django.contrib import admin

from .models import PresencialSession


@admin.register(PresencialSession)
class PresencialSessionAdmin(admin.ModelAdmin):
    list_display = (
        'module', 'professional', 'session_date', 'location',
        'participants_count', 'quiz_score', 'quiz_passed', 'created_at',
    )
    list_filter = ('module', 'quiz_passed', 'session_date')
    search_fields = ('professional__email', 'professional__first_name', 'location')
    date_hierarchy = 'session_date'

    readonly_fields = ('created_at',)
