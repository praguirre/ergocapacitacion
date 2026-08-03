(() => {
  const root = document.getElementById("presencial-quiz");
  if (!root) return;

  const questions = JSON.parse(root.dataset.questions);
  const submitUrl = root.dataset.submitUrl;
  const answers = {};
  let currentIndex = 0;

  const questionArea = document.getElementById("question-area");
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");
  const submitBtn = document.getElementById("submit-btn");
  const progressBar = document.getElementById("progress-bar");
  const currentQSpan = document.getElementById("current-q");

  function selectChoice(questionId, choiceId, button) {
    answers[questionId] = choiceId;
    document.querySelectorAll(".choice-btn").forEach((choice) => choice.classList.remove("selected"));
    button.classList.add("selected");
    nextBtn.disabled = false;
    submitBtn.disabled = Object.keys(answers).length < questions.length;
  }

  function renderQuestion(index) {
    const question = questions[index];
    currentQSpan.textContent = index + 1;
    progressBar.style.width = `${((index + 1) / questions.length) * 100}%`;

    let html = `
      <div class="card question-card bg-dark border-secondary">
        <div class="card-body p-4">
          <h5 class="text-white mb-4">${index + 1}. ${question.text}</h5>
          <div class="d-grid gap-2">`;

    question.choices.forEach((choice) => {
      const selected = answers[question.id] === choice.id ? "selected" : "";
      html += `
        <button class="btn choice-btn p-3 text-light ${selected}"
                data-question-id="${question.id}" data-choice-id="${choice.id}">
          ${choice.text}
        </button>`;
    });

    html += "</div></div></div>";
    questionArea.innerHTML = html;
    questionArea.querySelectorAll(".choice-btn").forEach((button) => {
      button.addEventListener("click", () => selectChoice(
        Number(button.dataset.questionId),
        Number(button.dataset.choiceId),
        button,
      ));
    });

    prevBtn.disabled = index === 0;
    if (index === questions.length - 1) {
      nextBtn.classList.add("d-none");
      submitBtn.classList.remove("d-none");
    } else {
      nextBtn.classList.remove("d-none");
      submitBtn.classList.add("d-none");
    }
    nextBtn.disabled = !answers[question.id];
    submitBtn.disabled = Object.keys(answers).length < questions.length;
  }

  document.getElementById("repeat-quiz-btn").addEventListener("click", () => location.reload());
  prevBtn.addEventListener("click", () => {
    if (currentIndex > 0) {
      currentIndex -= 1;
      renderQuestion(currentIndex);
    }
  });
  nextBtn.addEventListener("click", () => {
    if (currentIndex < questions.length - 1) {
      currentIndex += 1;
      renderQuestion(currentIndex);
    }
  });
  submitBtn.addEventListener("click", async () => {
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Enviando...';
    const csrfToken = document.cookie.split("csrftoken=")[1]?.split(";")[0];

    try {
      const response = await fetch(submitUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ answers }),
      });
      const data = await response.json();
      document.getElementById("quiz-section").classList.add("d-none");
      document.getElementById("result-section").classList.remove("d-none");
      const icon = document.getElementById("result-icon");
      const score = document.getElementById("result-score");
      const text = document.getElementById("result-text");

      if (data.passed) {
        icon.innerHTML = '<i class="bi bi-check-circle-fill text-success" style="font-size: 4rem;"></i>';
        score.innerHTML = `<span class="result-passed">${data.score}/${data.total}</span>`;
        text.textContent = "¡Aprobado! Podés generar la planilla de asistencia.";
      } else {
        icon.innerHTML = '<i class="bi bi-x-circle-fill text-danger" style="font-size: 4rem;"></i>';
        score.innerHTML = `<span class="result-failed">${data.score}/${data.total}</span>`;
        text.textContent = "No aprobado. Mínimo requerido: 8/10.";
      }
    } catch (error) {
      alert("Error al enviar el quiz. Intentá de nuevo.");
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="bi bi-check-lg me-2"></i>Finalizar Quiz';
    }
  });

  renderQuestion(0);
})();
