document.addEventListener("DOMContentLoaded", () => {
  const hamburger = document.getElementById("hamburger");
  const navMenu = document.getElementById("navMenu");
  const moreDropdownBtn = document.getElementById("moreDropdown");
  const moreDropdownMenu = document.getElementById("dropdownMenu");

  if (hamburger && navMenu) {
    hamburger.addEventListener("click", () => {
      navMenu.classList.toggle("active");
      hamburger.classList.toggle("active");
    });
  }

  if (moreDropdownBtn && moreDropdownMenu) {
    moreDropdownBtn.addEventListener("click", () => {
      moreDropdownBtn.classList.toggle("active");
      moreDropdownMenu.classList.toggle("active");
    });
  }

  document.addEventListener("click", (event) => {
    if (!moreDropdownBtn || !moreDropdownMenu) {
      return;
    }

    const isInside =
      moreDropdownBtn.contains(event.target) || moreDropdownMenu.contains(event.target);

    if (!isInside) {
      moreDropdownBtn.classList.remove("active");
      moreDropdownMenu.classList.remove("active");
    }
  });

  document.querySelectorAll(".btn-close").forEach((button) => {
    button.addEventListener("click", () => {
      const alert = button.closest(".alert");
      if (alert) {
        alert.remove();
      }
    });
  });
});
