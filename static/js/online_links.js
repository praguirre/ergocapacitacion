(() => {
  function copyLink(linkId) {
    const input = document.getElementById(`link-${linkId}`);
    const icon = document.getElementById(`icon-${linkId}`);

    navigator.clipboard.writeText(input.value).then(() => {
      icon.className = "bi bi-clipboard-check text-success";
      setTimeout(() => { icon.className = "bi bi-clipboard"; }, 2000);
    }).catch(() => {
      input.select();
      document.execCommand("copy");
      icon.className = "bi bi-clipboard-check text-success";
      setTimeout(() => { icon.className = "bi bi-clipboard"; }, 2000);
    });
  }

  document.querySelectorAll(".js-copy-link").forEach((button) => {
    button.addEventListener("click", () => copyLink(button.dataset.linkId));
  });
})();
