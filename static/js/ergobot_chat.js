// static/js/ergobot_chat.js

// Mantiene el historial de la conversación en la sesión actual
window.ergobotThread = window.ergobotThread || [];

async function sendErgobotMessage(moduleSlug, text, onDelta) {
  const url = new URL(`/ai/ergobot/${moduleSlug}/stream/`, window.location.origin);
  url.searchParams.set("q", text);
  url.searchParams.set("thread", JSON.stringify(window.ergobotThread));

  const resp = await fetch(url.toString(), {
    headers: { "Accept": "text/event-stream" },
    credentials: "same-origin", // Importante para mantener la sesión de Django
  });

  if (!resp.ok || !resp.body) {
    throw new Error(`SSE failed: ${resp.status}`);
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder("utf-8");

  let assistantText = "";
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // El protocolo SSE separa eventos por doble salto de línea
    const events = buffer.split("\n\n");
    buffer = events.pop() || "";

    for (const evt of events) {
      const lines = evt.split("\n");
      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;

        const payload = JSON.parse(line.slice(6));

        if (payload.delta) {
          assistantText += payload.delta;
          if (onDelta) onDelta(payload.delta);
        }

        if (payload.done) {
          // Guardamos ambos mensajes en el hilo para dar contexto a la siguiente pregunta
          window.ergobotThread.push({ role: "user", content: text });
          window.ergobotThread.push({ role: "assistant", content: assistantText });
          return assistantText;
        }

        if (payload.error) {
          const msg = `\n\n[Error Ergobot] ${payload.error}`;
          if (onDelta) onDelta(msg);
          return assistantText + msg;
        }
      }
    }
  }
  return assistantText;
}

window.sendErgobotMessage = sendErgobotMessage;