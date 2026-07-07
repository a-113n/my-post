const text = document.getElementById("text");
text.addEventListener("input", () => {
  const len = text.value.length;
  document.querySelectorAll("input[name='platforms']").forEach((cb) => {
    const limit = parseInt(cb.dataset.limit, 10);
    const counter = document.querySelector(`.counter[data-for="${cb.value}"]`);
    if (counter) counter.textContent = String(limit - len);
  });
});