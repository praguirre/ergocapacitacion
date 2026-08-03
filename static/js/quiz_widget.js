document.addEventListener("DOMContentLoaded", () => {
  const root = document.getElementById("quiz-root");
  if (!root?.dataset.moduleSlug) return;
  initQuiz(root.dataset.moduleSlug);
});
