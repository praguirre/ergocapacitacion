// static/js/quiz.js

/**
 * Lógica del Frontend para el Quiz interactivo.
 * Maneja el flujo: Inicio -> Preguntas -> Respuestas -> Submit -> Redirect
 */

let QUIZ = { attemptId: null, moduleSlug: null, order: 1 };

function initQuiz(moduleSlug) {
  QUIZ.moduleSlug = moduleSlug;
  const btn = document.getElementById("quizStartBtn");
  if (btn) btn.onclick = startQuiz;
}

// --- 1. Iniciar Intento ---
async function startQuiz() {
  setQuizBox(`<div class="text-secondary my-4"><span class="spinner-border spinner-border-sm me-2"></span>Iniciando examen...</div>`);
  
  try {
    const r = await fetch(`/quiz/${QUIZ.moduleSlug}/start/`, {
      method: "POST",
      headers: { "X-CSRFToken": getCsrf() },
      credentials: "same-origin",
    });

    if (!r.ok) {
      const err = await r.json().catch(() => ({}));
      if (r.status === 403 && err.locked) {
        let msg = '<div class="alert alert-warning text-start small">';
        msg += '<strong><i class="bi bi-lock me-1"></i>Examen no disponible</strong><br/>';
        if (err.lockout_until) msg += `Bloqueado hasta: ${formatIso(err.lockout_until)}<br/>`;
        if (err.retake_available_at) msg += `Disponible desde: ${formatIso(err.retake_available_at)}`;
        msg += '</div>';
        setQuizBox(msg);
        return;
      }
      setQuizBox(`<div class="alert alert-danger">Error al iniciar: ${err.error || "Desconocido"}</div>`);
      return;
    }

    const data = await r.json();
    QUIZ.attemptId = data.attempt_id;
    // Cargar primera pregunta
    renderQuestion(data.next);

  } catch (e) {
    console.error(e);
    setQuizBox(`<div class="alert alert-danger">Error de conexión.</div>`);
  }
}

// --- 2. Cargar Pregunta (Navegación) ---
async function loadQuestion(order) {
  try {
    const r = await fetch(`/quiz/${QUIZ.moduleSlug}/question/${order}/`, {
      credentials: "same-origin",
    });
    if (!r.ok) throw new Error("Error loading question");
    const q = await r.json();
    renderQuestion(q);
  } catch (e) {
    setQuizBox(`<div class="alert alert-danger">Error al cargar la pregunta ${order}.</div>`);
  }
}

// --- 3. Renderizar UI de Pregunta ---
function renderQuestion(q) {
  QUIZ.order = q.order;
  // Actualizar contador visual
  const counter = document.getElementById("quizCounter");
  if(counter) counter.textContent = `${q.order}/10`;

  const box = document.getElementById("quizBox");
  box.classList.remove("text-secondary", "text-center"); // Limpiar estilos de estado inicial
  box.innerHTML = `
    <div class="mb-3 fs-5"><strong>${escapeHtml(q.text)}</strong></div>
    <div id="quizChoices" class="d-grid gap-2"></div>
    <div id="quizFeedback" class="mt-3"></div>
  `;

  const choices = document.getElementById("quizChoices");
  q.choices.forEach(c => {
    const btn = document.createElement("button");
    btn.className = "btn btn-outline-light text-start p-3 choice-btn";
    btn.innerHTML = `<span class="badge bg-secondary me-2">${c.label}</span> ${escapeHtml(c.text)}`;
    btn.onclick = () => sendAnswer(q.question_id, c.choice_id, btn);
    choices.appendChild(btn);
  });
}

// --- 4. Enviar Respuesta ---
async function sendAnswer(questionId, choiceId, btnElement) {
  // Deshabilitar botones para evitar doble click
  document.querySelectorAll(".choice-btn").forEach(b => b.disabled = true);
  if(btnElement) btnElement.classList.replace("btn-outline-light", "btn-light"); // Feedback visual selección

  try {
    const r = await fetch(`/quiz/${QUIZ.moduleSlug}/answer/`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrf() },
      credentials: "same-origin",
      body: JSON.stringify({ attempt_id: QUIZ.attemptId, question_id: questionId, choice_id: choiceId })
    });

    if (!r.ok) {
      setFeedback(`<div class="alert alert-danger">Error al guardar respuesta.</div>`);
      return;
    }

    const data = await r.json();
    
    // Mostrar Feedback Inmediato
    const alertClass = data.correct ? "alert-success" : "alert-danger";
    const icon = data.correct ? '<i class="bi bi-check-circle-fill me-2"></i>' : '<i class="bi bi-x-circle-fill me-2"></i>';
    
    setFeedback(`
      <div class="alert ${alertClass} animate__animated animate__fadeIn">
        <strong>${icon}${escapeHtml(data.feedback_title)}</strong><br/>
        <small>${escapeHtml(data.feedback_text)}</small>
      </div>
      <div class="d-grid">
        <button id="nextBtn" class="btn btn-primary">
          ${data.done ? 'Ver Resultados' : 'Siguiente Pregunta <i class="bi bi-arrow-right"></i>'}
        </button>
      </div>
    `);

    document.getElementById("nextBtn").onclick = async () => {
      if (data.done) return submitQuiz();
      await loadQuestion(data.next_order);
    };

  } catch (e) {
    setFeedback(`<div class="alert alert-danger">Error de red.</div>`);
  }
}

// --- 5. Finalizar Examen ---
async function submitQuiz() {
  const box = document.getElementById("quizBox");
  box.innerHTML = `<div class="text-center py-5"><span class="spinner-border text-primary"></span><p class="mt-2">Calculando resultados...</p></div>`;

  try {
    const r = await fetch(`/quiz/${QUIZ.moduleSlug}/submit/`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrf() },
      credentials: "same-origin",
      body: JSON.stringify({ attempt_id: QUIZ.attemptId })
    });

    if (!r.ok) {
      box.innerHTML = `<div class="alert alert-danger">Error al finalizar el examen. Por favor recarga la página.</div>`;
      return;
    }

    const data = await r.json();
    // Redirigir a la pantalla de resultados
    window.location.href = data.result_url;

  } catch (e) {
    box.innerHTML = `<div class="alert alert-danger">Error crítico al enviar.</div>`;
  }
}

// --- Helpers ---

function setQuizBox(html) {
  const box = document.getElementById("quizBox");
  if (box) box.innerHTML = html;
}

function setFeedback(html) {
  const fb = document.getElementById("quizFeedback");
  if (fb) fb.innerHTML = html;
}

function getCsrf() {
  // Obtiene el token CSRF de las cookies de Django
  return document.cookie.split("; ").find(x => x.startsWith("csrftoken="))?.split("=")[1] || "";
}

function formatIso(iso) {
  if (!iso) return "";
  try { return new Date(iso).toLocaleString(); } catch { return iso; }
}

function escapeHtml(str) {
  return (str ?? "").toString()
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}