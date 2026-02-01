document.addEventListener("DOMContentLoaded", () => {
  const dropdownButton = document.getElementById("languageDropdown");
  const languageMenu = document.getElementById("languageMenu");
  const currentLanguage = document.getElementById("currentLanguage");
  const options = document.querySelectorAll(".language-option");

  const savedLanguage = localStorage.getItem("vyapareLanguage") || "en";

  const applyLanguage = (lang) => {
    const dictionary = window.translations?.[lang] || window.translations?.en || {};

    // Translate text content
    document.querySelectorAll("[data-i18n]").forEach((element) => {
      const key = element.getAttribute("data-i18n");
      if (dictionary[key]) {
        element.textContent = dictionary[key];
      }
    });

    // Translate placeholders
    document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
      const key = element.getAttribute("data-i18n-placeholder");
      if (dictionary[key]) {
        element.placeholder = dictionary[key];
      }
    });

    // Update hero text if it exists
    const heroLine1 = document.getElementById("heroLine1");
    const heroLine2Prefix = document.getElementById("heroLine2Prefix");
    const heroLine2Highlight = document.getElementById("heroLine2Highlight");
    
    if (heroLine1) {
      const line1Key = heroLine1.getAttribute("data-i18n");
      if (line1Key && dictionary[line1Key]) {
        heroLine1.textContent = dictionary[line1Key];
      }
    }
    if (heroLine2Prefix) {
      const prefixKey = heroLine2Prefix.getAttribute("data-i18n");
      if (prefixKey && dictionary[prefixKey]) {
        heroLine2Prefix.textContent = dictionary[prefixKey];
      }
    }
    if (heroLine2Highlight) {
      const highlightKey = heroLine2Highlight.getAttribute("data-i18n");
      if (highlightKey && dictionary[highlightKey]) {
        heroLine2Highlight.textContent = dictionary[highlightKey];
      }
    }

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
