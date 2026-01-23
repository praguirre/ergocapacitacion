# apps/ergobot_ai/views.py
import json
from django.http import StreamingHttpResponse, HttpRequest
from django.contrib.auth.decorators import login_required
from agents import Runner
from .agents import ergobot_agent

def _sse(payload: dict) -> bytes:
    """Formatea los datos para el protocolo Server-Sent Events."""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n".encode("utf-8")

@login_required # Solo usuarios autenticados pueden usar el chat
async def ergobot_stream(request: HttpRequest, module_slug: str):
    q = (request.GET.get("q") or "").strip()
    thread_raw = request.GET.get("thread") or "[]"

    # Validación básica de consulta vacía
    if not q:
        resp = StreamingHttpResponse([_sse({"error": "empty"})], content_type="text/event-stream")
        _set_streaming_headers(resp)
        return resp

    # Procesamiento del historial de la conversación (thread)
    try:
        thread = json.loads(thread_raw)
        if not isinstance(thread, list):
            thread = []
    except Exception:
        thread = []

    agent = ergobot_agent(module_slug)
    messages = thread + [{"role": "user", "content": q}]

    async def gen():
        try:
            # Ejecutamos el agente en modo streaming
            result = Runner.run_streamed(agent, input=messages)
            async for ev in result.stream_events():
                # Filtramos los eventos de 'delta' (fragmentos de texto)
                if ev.type == "raw_response_event" and getattr(ev.data, "type", "") == "response.output_text.delta":
                    yield _sse({"delta": ev.data.delta})
        except Exception as e:
            yield _sse({"error": str(e)})

        yield _sse({"done": True})

    resp = StreamingHttpResponse(gen(), content_type="text/event-stream")
    _set_streaming_headers(resp)
    return resp

def _set_streaming_headers(response):
    """Configura cabeceras críticas para evitar que el navegador o proxy cacheen la respuesta."""
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no" # Crucial para Nginx y despliegues en la nube