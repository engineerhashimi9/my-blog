/*!
 * Hashimi Blog — nav scroll + global theme toggle
 */
(function () {
  "use strict";

  const THEME_KEY = "hashimi-theme";

  function getSavedTheme() {
    try {
      return (
        localStorage.getItem(THEME_KEY) ||
        (localStorage.getItem("hashimi-about-theme") === "light" ? "light" : "dark")
      );
    } catch (e) {
      return "dark";
    }
  }

  function applyTheme(mode) {
    const isLight = mode === "light";
    document.documentElement.classList.toggle("theme-light", isLight);
    try {
      localStorage.setItem(THEME_KEY, isLight ? "light" : "dark");
      localStorage.removeItem("hashimi-about-theme");
    } catch (e) {}
  }

  function initThemeToggle() {
    const toggle = document.getElementById("themeToggle");
    if (!toggle) return;

    toggle.addEventListener("click", () => {
      const next = document.documentElement.classList.contains("theme-light")
        ? "dark"
        : "light";
      applyTheme(next);
    });
  }

  function initNavScroll() {
    const mainNav = document.getElementById("mainNav");
    if (!mainNav) return;

    let scrollPos = 0;
    const headerHeight = mainNav.clientHeight;

    window.addEventListener("scroll", () => {
      const currentTop = document.body.getBoundingClientRect().top * -1;

      if (currentTop < scrollPos) {
        if (currentTop > 0 && mainNav.classList.contains("is-fixed")) {
          mainNav.classList.add("is-visible");
        } else {
          mainNav.classList.remove("is-visible", "is-fixed");
        }
      } else {
        mainNav.classList.remove("is-visible");
        if (currentTop > headerHeight && !mainNav.classList.contains("is-fixed")) {
          mainNav.classList.add("is-fixed");
        }
      }

      scrollPos = currentTop;
    });
  }

  function initContactCopy() {
    const copyBtn = document.getElementById("copyEmailBtn");
    if (!copyBtn) return;

    copyBtn.addEventListener("click", async () => {
      const email = copyBtn.dataset.email || "engineerhashimi9@gmail.com";
      const label = copyBtn.querySelector("span");

      try {
        await navigator.clipboard.writeText(email);
        copyBtn.classList.add("is-copied");
        if (label) label.textContent = "Copied!";
        setTimeout(() => {
          copyBtn.classList.remove("is-copied");
          if (label) label.textContent = "Copy email";
        }, 2000);
      } catch (e) {
        if (label) label.textContent = "Copy failed";
        setTimeout(() => {
          if (label) label.textContent = "Copy email";
        }, 2000);
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    applyTheme(getSavedTheme());
    initThemeToggle();
    initNavScroll();
    initContactCopy();
  });
})();
