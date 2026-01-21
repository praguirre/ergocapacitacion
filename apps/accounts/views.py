from django.http import HttpResponse

def health(_request):
    """Endpoint simple para verificar que el servidor responde."""
    return HttpResponse("OK")