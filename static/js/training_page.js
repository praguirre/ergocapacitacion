(() => {
  const root = document.getElementById("training-page");
  if (!root) return;

  const moduleSlug = root.dataset.moduleSlug;
  const log = document.getElementById("chatLog");
  const input = document.getElementById("chatInput");
  const btn = document.getElementById("chatSend");

  async function handleSend() {
    const text = input.value.trim();
    if (!text) return;

    input.value = "";
    input.disabled = true;
    btn.disabled = true;
    log.innerHTML += `<div class="mt-2"><strong>👤 Usuario:</strong><br>${text}</div>`;
    log.innerHTML += '<div class="mt-2"><strong>🤖 Ergobot:</strong><br><span id="currentDelta"></span></div>';

    const deltaSpan = document.getElementById("currentDelta");
    log.scrollTop = log.scrollHeight;

    try {
      await sendErgobotMessage(moduleSlug, text, (delta) => {
        deltaSpan.textContent += delta;
        log.scrollTop = log.scrollHeight;
      });
      deltaSpan.removeAttribute("id");
    } catch (err) {
      log.innerHTML += '<div class="text-danger mt-1">Error: No se pudo conectar con el bot.</div>';
    } finally {
      input.disabled = false;
      btn.disabled = false;
      input.focus();
    }
  }

  btn.onclick = handleSend;
  input.onkeypress = (event) => {
    if (event.key === "Enter") handleSend();
  };
})();
