/**
 * About Me page — typing animation, counters, scroll reveal, theme toggle
 */
(function () {
  "use strict";

  /* Only run on the About page */
  const typingEl = document.getElementById("aboutTypingText");
  if (!typingEl) return;

  const TYPING_LINES = [
    'Engineer Hashimi >_',
    'const me = new Developer();',
    'whoami → engineer_hashimi',
  ];

  /* ---- Typing animation ---- */
  function initTyping() {
    let lineIndex = 0;
    let charIndex = 0;
    let deleting = false;

    function tick() {
      const current = TYPING_LINES[lineIndex];

      if (!deleting) {
        typingEl.textContent = current.slice(0, charIndex + 1);
        charIndex += 1;

        if (charIndex === current.length) {
          deleting = true;
          setTimeout(tick, 2200);
          return;
        }
        setTimeout(tick, 75);
      } else {
        typingEl.textContent = current.slice(0, charIndex - 1);
        charIndex -= 1;

        if (charIndex === 0) {
          deleting = false;
          lineIndex = (lineIndex + 1) % TYPING_LINES.length;
          setTimeout(tick, 500);
          return;
        }
        setTimeout(tick, 40);
      }
    }

    tick();
  }

  /* ---- Animated stat counters ---- */
  function animateCounter(el) {
    const target = parseInt(el.dataset.count, 10);
    const suffix = el.dataset.suffix || "";
    const duration = 1800;
    const start = performance.now();

    function step(now) {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const value = Math.round(eased * target);
      el.textContent = value + suffix;

      if (progress < 1) {
        requestAnimationFrame(step);
      }
    }

    requestAnimationFrame(step);
  }

  function initCounters() {
    const counters = document.querySelectorAll(".about-stat__value[data-count]");
    if (!counters.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting || entry.target.dataset.animated) return;
          entry.target.dataset.animated = "true";
          animateCounter(entry.target);
        });
      },
      { threshold: 0.4 }
    );

    counters.forEach((el) => observer.observe(el));
  }

  /* ---- Scroll reveal ---- */
  function initReveal() {
    const items = document.querySelectorAll("[data-reveal]");
    if (!items.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );

    items.forEach((el) => observer.observe(el));
  }

  /* ---- Boot ---- */
  document.addEventListener("DOMContentLoaded", () => {
    initTyping();
    initCounters();
    initReveal();
  });
})();
