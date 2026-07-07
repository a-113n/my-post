const text = document.getElementById("text");
if (text) {
  const checkboxes = document.querySelectorAll("input[name='platforms']");

  function recount() {
    const len = text.value.length;
    checkboxes.forEach((cb) => {
      const limit = parseInt(cb.dataset.limit, 10);
      const remaining = limit - len;
      const counter = document.querySelector(`.counter[data-for="${cb.value}"]`);
      if (counter) {
        counter.textContent = String(remaining);
        counter.classList.toggle("warn", remaining > 0 && remaining <= 10);
        counter.classList.toggle("over", remaining <= 0);
      }
    });
  }

  checkboxes.forEach((cb) => {
    cb.addEventListener("change", () => {
      cb.closest(".chip")?.classList.toggle("checked", cb.checked);
    });
  });

  text.addEventListener("input", recount);
  recount();
}
