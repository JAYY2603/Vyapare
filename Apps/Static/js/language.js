document.addEventListener("DOMContentLoaded", () => {
  const dropdownButton = document.getElementById("languageDropdown");
  const languageMenu = document.getElementById("languageMenu");
  const currentLanguage = document.getElementById("currentLanguage");
  const options = document.querySelectorAll(".language-option");

  const savedLanguage = localStorage.getItem("vyapareLanguage") || "en";

  const applyLanguage = (lang) => {
    const dictionary = window.translations?.[lang] || window.translations?.en || {};

    document.querySelectorAll("[data-i18n]").forEach((element) => {
      const key = element.getAttribute("data-i18n");
      if (dictionary[key]) {
        element.textContent = dictionary[key];
      }
    });

    if (currentLanguage) {
      currentLanguage.textContent = lang.toUpperCase();
    }

    localStorage.setItem("vyapareLanguage", lang);
  };

  applyLanguage(savedLanguage);

  if (dropdownButton && languageMenu) {
    dropdownButton.addEventListener("click", () => {
      dropdownButton.classList.toggle("active");
      languageMenu.classList.toggle("active");
    });

    document.addEventListener("click", (event) => {
      const isInside =
        dropdownButton.contains(event.target) || languageMenu.contains(event.target);

      if (!isInside) {
        dropdownButton.classList.remove("active");
        languageMenu.classList.remove("active");
      }
    });
  }

  options.forEach((option) => {
    option.addEventListener("click", (event) => {
      event.preventDefault();
      const selectedLanguage = option.dataset.lang || "en";
      applyLanguage(selectedLanguage);
    });
  });
});
