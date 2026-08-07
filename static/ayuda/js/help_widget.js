// static/ayuda/js/help_widget.js

document.addEventListener("DOMContentLoaded", () => {
  const helpWidgetElement = document.getElementById("helpWidget");
  if (!helpWidgetElement) return;

  const offcanvas = new bootstrap.Offcanvas(helpWidgetElement);
  const helpToggleButton = document.getElementById("helpToggle");

  const guideContentEl = document.getElementById("tabGuide");

  const chatForm = document.getElementById("chat-form");
  const chatInput = document.getElementById("chat-input");
  const chatMessages = document.getElementById("chat-messages");
  const submitButton = document.getElementById("chat-submit-btn");

  window.chatThread = window.chatThread || [];

  function renderSafeMarkdown(source) {
    const text = String(source || "");
    if (!window.marked || !window.DOMPurify) {
      const pre = document.createElement("pre");
      pre.className = "text-wrap";
      pre.textContent = text;
      return pre.outerHTML;
    }
    const rendered = window.marked.parse(text);
    return window.DOMPurify.sanitize(rendered, {
      USE_PROFILES: { html: true },
      ALLOW_DATA_ATTR: false,
      FORBID_TAGS: [
        "script", "style", "form", "input", "button", "textarea", "select",
        "option", "iframe", "object", "embed", "svg", "math", "img"
      ],
      FORBID_ATTR: ["style", "srcset"],
    });
  }

  function resolvedUrl(templateValue, slug) {
    return String(templateValue || "").replace("__slug__", encodeURIComponent(slug));
  }

  const tabs = document.getElementById("helpTabs");
  const offcanvasBody = helpWidgetElement.querySelector(".offcanvas-body");
  tabs.addEventListener("shown.bs.tab", () => {
    offcanvasBody.scrollTop = 0;
    const msgs = document.getElementById("chat-messages");
    if (msgs) msgs.scrollTop = msgs.scrollHeight;
  });

  if (helpToggleButton) {
    helpToggleButton.addEventListener("click", () => offcanvas.toggle());
  }

  helpWidgetElement.addEventListener("show.bs.offcanvas", () => {
    if (!helpToggleButton) return;
    helpToggleButton.classList.add("d-none");
    helpToggleButton.setAttribute("aria-hidden", "true");
  });
  helpWidgetElement.addEventListener("hidden.bs.offcanvas", () => {
    if (!helpToggleButton) return;
    helpToggleButton.classList.remove("d-none");
    helpToggleButton.removeAttribute("aria-hidden");
  });

  async function loadGuide(slug) {
    if (
      guideContentEl.dataset.loadedSlug === slug
      && helpWidgetElement.dataset.helpVersion
    ) {
      return helpWidgetElement.dataset.helpVersion;
    }
    try {
      const guideUrl = resolvedUrl(
        helpWidgetElement.dataset.guideUrlTemplate,
        slug,
      );
      if (!guideUrl) throw new Error("No se configuró la URL de la guía.");
      const r = await fetch(guideUrl, {
        credentials: "same-origin",
        headers: { Accept: "text/markdown" },
      });
      if (!r.ok) throw new Error(`El archivo de ayuda "${slug}.md" no está disponible.`);
      const md = await r.text();
      const helpVersion = r.headers.get("X-Help-Content-Version");
      if (!helpVersion) throw new Error("La guía no informó su versión.");
      guideContentEl.innerHTML = renderSafeMarkdown(md);
      guideContentEl.dataset.loadedSlug = slug;
      helpWidgetElement.dataset.helpVersion = helpVersion;
      return helpVersion;
    } catch (err) {
      console.error("Error al cargar la guía:", err);
      guideContentEl.replaceChildren();
      const errorMessage = document.createElement("p");
      errorMessage.className = "text-danger";
      errorMessage.textContent = "No se pudo cargar el contenido de la ayuda.";
      guideContentEl.appendChild(errorMessage);
      delete guideContentEl.dataset.loadedSlug;
      delete helpWidgetElement.dataset.helpVersion;
      throw err;
    }
  }

  helpWidgetElement.addEventListener("show.bs.offcanvas", async () => {
    const slug = helpWidgetElement.dataset.pageSlug;
    if (!slug) return;
    try {
      await loadGuide(slug);
    } catch {
      // loadGuide ya presenta un mensaje seguro en la pestaña Guía.
    }
  });

  function renderUserMessage(content) {
    const div = document.createElement("div");
    div.className = "user-message mb-2 text-end";
    const badge = document.createElement("span");
    badge.className = "badge bg-primary text-wrap";
    badge.textContent = content;
    div.appendChild(badge);
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function hideThinking() {
    document.getElementById("ai-thinking")?.remove();
  }

  function showThinking() {
    hideThinking();
    const wrap = document.createElement("div");
    wrap.className = "ai-thinking";
    wrap.id = "ai-thinking";
    wrap.setAttribute("role", "status");
    wrap.setAttribute("aria-live", "polite");

    const label = document.createElement("span");
    label.textContent = "ErgoBot está pensando";

    const dots = document.createElement("span");
    dots.className = "ai-thinking__dots";
    dots.setAttribute("aria-hidden", "true");
    dots.append(
      document.createElement("span"),
      document.createElement("span"),
      document.createElement("span"),
    );

    wrap.append(label, dots);
    chatMessages.appendChild(wrap);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function renderOrUpdateAIMessage(fullContent) {
    hideThinking();
    let ai = chatMessages.querySelector(".ai-message-container:last-child");
    if (!ai || ai.dataset.finalized === "true") {
      ai = document.createElement("div");
      ai.className = "ai-message-container mb-2";
      ai.dataset.finalized = "false";
      chatMessages.appendChild(ai);
    }
    ai.innerHTML = renderSafeMarkdown(fullContent);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  async function sendToAI(message) {
    const slug = helpWidgetElement.dataset.pageSlug;
    if (!slug) return;

    chatInput.disabled = true;
    submitButton.disabled = true;
    showThinking();

    let helpVersion;
    try {
      helpVersion = await loadGuide(slug);
    } catch {
      hideThinking();
      chatInput.disabled = false;
      submitButton.disabled = false;
      renderOrUpdateAIMessage(
        "⚠️ No se pudo verificar la versión de la guía. Intentá nuevamente.",
      );
      chatInput.focus();
      return;
    }

    const url = resolvedUrl(helpWidgetElement.dataset.chatUrlTemplate, slug);
    const csrfToken = chatForm.querySelector("[name=csrfmiddlewaretoken]")?.value;
    const controller = new AbortController();
    let fullResponse = "";
    let lastTick = Date.now();
    let finalized = false;
    const watchdog = setInterval(() => {
      // Si pasan 30s sin eventos, cerramos para evitar quedarse colgado
      if (Date.now() - lastTick > 30000) {
        controller.abort();
        finalize(fullResponse || "⚠️ Conexión inactiva.");
      }
    }, 5000);

    function finalize(text) {
      if (finalized) return;
      finalized = true;
      clearInterval(watchdog);
      hideThinking();
      renderOrUpdateAIMessage(text);
      const last = chatMessages.querySelector(".ai-message-container:last-child");
      if (last) last.dataset.finalized = "true";
      chatInput.disabled = false;
      submitButton.disabled = false;
      chatInput.focus();
    }

    function processEvent(rawEvent) {
      const dataLine = rawEvent
        .split("\n")
        .find((line) => line.startsWith("data:"));
      if (!dataLine) return;
      lastTick = Date.now();
      let data;
      try { data = JSON.parse(dataLine.slice(5).trim()); } catch { return; }

      if (data.delta) {
        fullResponse += data.delta;
        renderOrUpdateAIMessage(fullResponse + " ▌");
      }
      if (data.error) {
        finalize(`⚠️ Error: ${String(data.error)}`);
      }
      if (data.done) {
        finalize(fullResponse);
        if (Array.isArray(data.thread)) {
          const validThread = data.thread.every(
            (message) =>
              message && typeof message === "object"
              && ["user", "assistant"].includes(message.role)
              && typeof message.content === "string"
              && Object.keys(message).length === 2,
          );
          window.chatThread = validThread ? data.thread : [];
          if (!validThread) {
            console.warn(
              "Hilo con formato inesperado: se reinicia la conversación.",
            );
          }
        }
      }
    }

    try {
      const response = await fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          Accept: "text/event-stream",
          "X-CSRFToken": csrfToken || "",
        },
        body: JSON.stringify({
          q: message,
          thread: window.chatThread,
          help_version: helpVersion,
        }),
        signal: controller.signal,
      });
      if (!response.ok) {
        let detail = "No se pudo iniciar la consulta.";
        try {
          const payload = await response.json();
          if (payload?.error) detail = payload.error;
        } catch {
          // Conserva el mensaje genérico si la respuesta no es JSON.
        }
        throw new Error(detail);
      }
      if (!response.body) throw new Error("El navegador no recibió un stream.");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      while (!finalized) {
        const { value, done } = await reader.read();
        if (done) break;
        lastTick = Date.now();
        buffer += decoder.decode(value, { stream: true }).replace(/\r\n/g, "\n");
        let boundary = buffer.indexOf("\n\n");
        while (boundary !== -1) {
          processEvent(buffer.slice(0, boundary));
          buffer = buffer.slice(boundary + 2);
          boundary = buffer.indexOf("\n\n");
        }
      }
      if (!finalized) finalize(fullResponse || "⚠️ Conexión interrumpida.");
    } catch (error) {
      if (!finalized) {
        const detail = error?.name === "AbortError"
          ? "Conexión interrumpida."
          : (error?.message || "Conexión interrumpida.");
        finalize(fullResponse || `⚠️ ${detail}`);
      }
    }
  }

  if (chatForm) {
    chatForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const userMessage = (chatInput.value || "").trim();
      if (!userMessage) return;

      renderUserMessage(userMessage);
      sendToAI(userMessage);
      chatInput.value = "";
    });
  }
});
