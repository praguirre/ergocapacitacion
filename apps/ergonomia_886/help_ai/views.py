# help_ai/views.py

import asyncio
import json
import logging

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseNotAllowed,
    JsonResponse,
    StreamingHttpResponse,
)
from agents import Runner, RunConfig, ItemHelpers
from openai.types.responses import ResponseTextDeltaEvent


from .agents import page_agent
from .catalog import ALLOWED_HELP_SLUGS
from .limits import (
    ChatLease,
    ChatLimitExceeded,
    acquire_chat_lease,
    release_chat_lease,
)
from .prompts import HelpContentError, page_help_context


logger = logging.getLogger(__name__)


@login_required
def guide_view(request: HttpRequest, slug: str):
    """Sirve el Markdown y la versión exacta que debe usar el Chat."""
    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "Se requiere una sesión autenticada."},
            status=401,
        )
    if slug not in ALLOWED_HELP_SLUGS:
        return JsonResponse({"error": "Página de ayuda desconocida."}, status=404)

    try:
        context = page_help_context(slug)
    except HelpContentError:
        logger.exception("Contenido de ayuda no disponible para slug=%s", slug)
        return JsonResponse(
            {"error": "El contenido de ayuda no está disponible."},
            status=503,
        )

    response = HttpResponse(
        context.specific_markdown,
        content_type="text/markdown; charset=utf-8",
    )
    response["Cache-Control"] = "no-cache"
    response["ETag"] = f'"{context.version}"'
    response["X-Help-Content-Version"] = context.version
    response["X-Content-Type-Options"] = "nosniff"
    return response


def normalize_thread(raw_thread) -> list:
    if not isinstance(raw_thread, list):
        raise ValueError("thread debe ser una lista de mensajes")
    if len(raw_thread) > settings.CHAT_AI_MAX_THREAD_MESSAGES:
        raise ValueError("El historial supera la cantidad máxima de mensajes.")

    normalized = []
    for item in raw_thread:
        if not isinstance(item, dict) or set(item) != {"role", "content"}:
            raise ValueError("Cada mensaje debe contener únicamente role y content.")
        role = item.get("role")
        content = item.get("content")
        if role not in {"user", "assistant"}:
            raise ValueError("El historial contiene un rol no permitido.")
        if not isinstance(content, str):
            raise ValueError("El contenido de cada mensaje debe ser texto.")
        content = content.strip()
        if not content or len(content) > settings.CHAT_AI_MAX_MESSAGE_CHARS:
            raise ValueError("Un mensaje del historial tiene un tamaño inválido.")
        normalized.append({"role": role, "content": content})
    return normalized


def _extract_text(content) -> str:
    """Aplana el contenido de un mensaje del SDK a texto plano."""
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""

    parts = []
    for part in content:
        if not isinstance(part, dict):
            continue
        part_type = part.get("type")
        if part_type in {"output_text", "input_text", "text"}:
            parts.append(part.get("text") or "")
        elif part_type == "refusal":
            parts.append(part.get("refusal") or "")
    return "".join(parts)


def to_wire_thread(raw_items) -> list:
    """Convierte items del SDK al contrato estricto que acepta el cliente.

    La salida debe sobrevivir siempre a ``normalize_thread()``: el navegador
    la reenviará sin transformaciones en la consulta siguiente.
    """
    wire = []
    for item in raw_items or []:
        if not isinstance(item, dict):
            continue
        if item.get("type") not in (None, "message"):
            continue
        role = item.get("role")
        if role not in {"user", "assistant"}:
            continue
        text = _extract_text(item.get("content")).strip()
        if not text:
            continue
        wire.append(
            {
                "role": role,
                "content": text[: settings.CHAT_AI_MAX_MESSAGE_CHARS],
            }
        )

    limit = max(0, int(settings.CHAT_AI_MAX_THREAD_MESSAGES))
    if len(wire) > limit:
        # Con límites normales se conserva una cantidad par para no cortar
        # un intercambio. Un límite unitario se respeta literalmente.
        keep = limit if limit < 2 else limit - (limit % 2)
        wire = wire[-keep:] if keep else []
    return wire


async def chat_stream_generator(
    slug: str,
    user_msg: str,
    thread: list,
    lease: ChatLease,
    content_version: str,
):
    """
    Envía SSE:
      - {"delta": "..."} por token (raw deltas)
      - Fallback: si no hay deltas, usa run_item_stream_event/message_output_created
      - {"done": true, "thread": [...]} al finalizar
      - {"error": "..."} si algo falla
    """
    run = None
    next_event_task = None
    try:
        agent = page_agent(slug, content_version)

        # Conversación manual (válida): historial + mensaje actual en 'input'
        messages = (thread or []) + [{"role": "user", "content": user_msg}]

        run = Runner.run_streamed(
            agent,
            input=messages,
            max_turns=8,
            run_config=RunConfig(
                workflow_name="ErgoApp-Chat",
                trace_include_sensitive_data=False,
            ),
        )

        saw_raw_delta = False
        assistant_text = []
        heartbeat_seconds = max(
            0.1,
            min(
                float(settings.CHAT_AI_HEARTBEAT_SECONDS),
                float(settings.CHAT_AI_STREAM_TIMEOUT_SECONDS),
            ),
        )
        deadline = (
            asyncio.get_running_loop().time()
            + float(settings.CHAT_AI_STREAM_TIMEOUT_SECONDS)
        )
        event_stream = run.stream_events().__aiter__()
        next_event_task = asyncio.create_task(anext(event_stream))

        while next_event_task is not None:
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                raise TimeoutError("El stream superó el tiempo máximo permitido.")

            done, _ = await asyncio.wait(
                {next_event_task},
                timeout=min(heartbeat_seconds, remaining),
            )
            if not done:
                yield ": heartbeat\n\n"
                continue

            try:
                event = next_event_task.result()
            except StopAsyncIteration:
                next_event_task = None
                break

            next_event_task = asyncio.create_task(anext(event_stream))
            et = getattr(event, "type", None)

            # 1) Tokens crudos (lo normal)
            if et == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                delta = event.data.delta or ""
                if delta:
                    saw_raw_delta = True
                    assistant_text.append(delta)
                    yield f"data: {json.dumps({'delta': delta})}\n\n"
                continue

            # 2) Fallback: si no hubo deltas, cuando el mensaje se crea mandamos su texto
            if et == "run_item_stream_event" and getattr(event, "name", "") == "message_output_created":
                if not saw_raw_delta:
                    chunk = ItemHelpers.text_message_output(event.item) or ""
                    if chunk:
                        assistant_text.append(chunk)
                        yield f"data: {json.dumps({'delta': chunk})}\n\n"
                continue

        # El SDK devuelve items de Responses API con claves y contenido que
        # normalize_thread() rechaza. Se convierten al contrato de cable antes
        # de enviarlos al navegador.
        answer = "".join(assistant_text).strip()
        fallback = (thread or []) + [{"role": "user", "content": user_msg}]
        if answer:
            fallback.append({"role": "assistant", "content": answer})

        try:
            final_thread = to_wire_thread(run.to_input_list())
        except Exception:
            logger.exception("No se pudo derivar el hilo del run para slug=%s", slug)
            final_thread = []

        if not final_thread:
            final_thread = to_wire_thread(fallback)

        yield f"data: {json.dumps({'done': True, 'thread': final_thread})}\n\n"

    except asyncio.CancelledError:
        logger.info("Stream del Chat IA cancelado por el cliente para slug=%s", slug)
        raise
    except TimeoutError:
        logger.warning("Timeout del Chat IA para slug=%s", slug)
        yield (
            "data: "
            + json.dumps(
                {
                    "error": (
                        "La consulta superó el tiempo máximo. "
                        "Intentá nuevamente con una pregunta más breve."
                    )
                }
            )
            + "\n\n"
        )
        final_thread = to_wire_thread(thread or [])
        yield f"data: {json.dumps({'done': True, 'thread': final_thread})}\n\n"
    except Exception:
        logger.exception("Error durante el stream del Chat IA para slug=%s", slug)
        yield f"data: {json.dumps({'error': 'Ocurrió un error al procesar tu solicitud. Intenta nuevamente.'})}\n\n"
        final_thread = to_wire_thread(thread or [])
        yield f"data: {json.dumps({'done': True, 'thread': final_thread})}\n\n"
    finally:
        if next_event_task is not None and not next_event_task.done():
            next_event_task.cancel()
            try:
                await next_event_task
            except (asyncio.CancelledError, StopAsyncIteration):
                pass
        if run is not None and not getattr(run, "is_complete", False):
            try:
                run.cancel()
            except Exception:
                logger.exception("No se pudo cancelar el run para slug=%s", slug)
        await sync_to_async(release_chat_lease, thread_sensitive=True)(lease)

# Vista ASGI (async) que devuelve SSE
async def chat_view(request: HttpRequest, slug: str):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    user_id = await sync_to_async(
        lambda: request.user.pk if request.user.is_authenticated else None,
        thread_sensitive=True,
    )()
    if user_id is None:
        return JsonResponse(
            {"error": "Se requiere una sesión autenticada."},
            status=401,
        )

    if slug not in ALLOWED_HELP_SLUGS:
        return JsonResponse({"error": "Página de ayuda desconocida."}, status=404)

    try:
        payload = json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "El cuerpo JSON es inválido."}, status=400)
    if not isinstance(payload, dict) or set(payload) - {
        "q",
        "thread",
        "help_version",
    }:
        return JsonResponse(
            {"error": "El cuerpo solo puede contener q, thread y help_version."},
            status=400,
        )

    user_msg = payload.get("q")
    if not isinstance(user_msg, str):
        return JsonResponse({"error": "La pregunta debe ser texto."}, status=400)
    user_msg = user_msg.strip()
    if not user_msg:
        return JsonResponse({"error": "La pregunta es requerida."}, status=400)
    if len(user_msg) > settings.CHAT_AI_MAX_QUESTION_CHARS:
        return JsonResponse({"error": "La pregunta es demasiado extensa."}, status=400)

    try:
        thread = normalize_thread(payload.get("thread", []))
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    help_version = payload.get("help_version")
    if not isinstance(help_version, str) or len(help_version) != 64:
        return JsonResponse(
            {"error": "Primero debe cargarse una versión válida de la guía."},
            status=400,
        )
    try:
        context = page_help_context(slug)
    except HelpContentError:
        logger.exception("Contenido de ayuda no disponible para slug=%s", slug)
        return JsonResponse(
            {"error": "El contenido de ayuda no está disponible."},
            status=503,
        )
    if help_version != context.version:
        return JsonResponse(
            {
                "error": (
                    "La ayuda fue actualizada. Recargá la guía antes de consultar."
                ),
                "help_version": context.version,
            },
            status=409,
        )

    try:
        lease = await sync_to_async(
            acquire_chat_lease,
            thread_sensitive=True,
        )(user_id)
    except ChatLimitExceeded as exc:
        response = JsonResponse({"error": str(exc)}, status=429)
        response["Retry-After"] = str(exc.retry_after)
        return response

    resp = StreamingHttpResponse(
        chat_stream_generator(
            slug,
            user_msg,
            thread,
            lease,
            context.version,
        ),
        content_type="text/event-stream; charset=utf-8",
    )
    resp["Cache-Control"] = "no-cache, no-transform"
    resp["X-Accel-Buffering"] = "no"  # Nginx/proxy
    return resp
