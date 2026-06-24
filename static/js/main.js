document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("newsletterForm");
  if (!form) return;

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const emailInput = document.getElementById("newsletterEmail");
    if (!emailInput.checkValidity()) return;

    document.getElementById("newsletterSuccess").classList.add("show");
    form.reset();
  });

  
  document.querySelectorAll(".toast").forEach(function (toastEl) {
    setTimeout(function () {
      toastEl.classList.add("fade-out");
      setTimeout(function () { toastEl.remove(); }, 200);
    }, 3500);
  });
});
