# apps/company/context_processors.py
# ============================================================================
# COMMIT 33: Context processor para datos de empresa en templates
# ============================================================================


def company_context(request):
    """
    Agrega flags de tipo de usuario y datos de empresa al contexto de templates.
    Disponible en TODOS los templates vía TEMPLATES.context_processors.
    """
    ctx = {
        'is_company_user': False,
        'is_professional_user': False,
        'is_backoffice_user': False,
        'company_profile': None,
    }

    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return ctx

    user = request.user
    ctx['is_backoffice_user'] = getattr(user, 'is_backoffice_user', False)
    ctx['is_professional_user'] = getattr(user, 'is_professional', False)
    ctx['is_company_user'] = getattr(user, 'is_company', False)

    if ctx['is_company_user']:
        try:
            ctx['company_profile'] = user.company_profile
        except Exception:
            ctx['company_profile'] = None

    return ctx
