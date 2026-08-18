from django.utils.dateparse import parse_datetime


ATTRIBUTION_FIELDS = [
    "attribution_source",
    "attribution_medium",
    "attribution_campaign",
    "attribution_content",
    "attribution_landing_path",
    "attribution_referrer_host",
    "attribution_first_seen_at",
]


def _parse_first_seen_at(value):
    if not isinstance(value, str):
        return None
    try:
        return parse_datetime(value)
    except (TypeError, ValueError):
        return None


def aplicar_atribucion(user, request) -> None:
    """Persiste la atribución first-touch sin interrumpir nunca el alta.

    La sesión se limpia tras un guardado exitoso y también cuando el usuario
    no es profesional. Si el guardado falla, la atribución permanece en sesión
    para no sumar otro posible error al flujo principal de registro.
    """
    try:
        attribution = request.session.get("attribution")
        if not attribution:
            return

        if not user.is_professional:
            request.session.pop("attribution", None)
            return

        user.attribution_source = attribution.get("source", "")
        user.attribution_medium = attribution.get("medium", "")
        user.attribution_campaign = attribution.get("campaign", "")
        user.attribution_content = attribution.get("content", "")
        user.attribution_landing_path = attribution.get("landing_path", "")
        user.attribution_referrer_host = attribution.get("referrer_host", "")
        user.attribution_first_seen_at = _parse_first_seen_at(
            attribution.get("first_seen_at")
        )

        user.save(update_fields=ATTRIBUTION_FIELDS)
        request.session.pop("attribution", None)
    except Exception:
        pass
