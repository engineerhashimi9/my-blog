/*!
 * Hashimi Blog — Core Frontend Engine
 * Modern dark-theme interactions, particle background, reading progress, and theme switcher.
 */
(function () {
  "use strict";

  const THEME_KEY = "hashimi-theme";
  let particleAnimationId = null;

  /* ==========================================================================
     Theme Management
     ========================================================================== */
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

    // Dispatch custom event for canvas and other modules to react
    window.dispatchEvent(new CustomEvent("themechange", { detail: { theme: mode } }));
  }

  function initThemeToggle() {
    const toggle = document.getElementById("themeToggle");
    if (!toggle) return;

    toggle.addEventListener("click", () => {
      const isCurrentlyLight = document.documentElement.classList.contains("theme-light");
      applyTheme(isCurrentlyLight ? "dark" : "light");
    });
  }

  /* ==========================================================================
     Navigation Scroll & Glassmorphism
     ========================================================================== */
  function initNavScroll() {
    const mainNav = document.getElementById("mainNav");
    if (!mainNav) return;

    let lastScrollTop = 0;
    const threshold = 50;

    function handleScroll() {
      const currentScroll = window.pageYOffset || document.documentElement.scrollTop;

      // Toggle glassmorphism shadow & compressed padding
      if (currentScroll > threshold) {
        mainNav.classList.add("is-scrolled", "is-fixed");
      } else {
        mainNav.classList.remove("is-scrolled", "is-fixed");
      }

      // Smart hide / show when scrolling deeply
      if (currentScroll > 200) {
        if (currentScroll > lastScrollTop && currentScroll - lastScrollTop > 10) {
          // Scrolling down - hide navbar smoothly
          mainNav.style.transform = "translateY(-100%)";
        } else if (lastScrollTop - currentScroll > 10) {
          // Scrolling up - show navbar
          mainNav.style.transform = "translateY(0)";
        }
      } else {
        mainNav.style.transform = "translateY(0)";
      }

      lastScrollTop = Math.max(0, currentScroll);
    }

    window.addEventListener("scroll", handleScroll, { passive: true });
    handleScroll();
  }

  /* ==========================================================================
     Active Navbar Link Highlighting
     ========================================================================== */
  function initActiveNavLinks() {
    const navLinks = document.querySelectorAll("#mainNav .nav-link");
    if (!navLinks.length) return;

    const currentPath = window.location.pathname.replace(/\/+$/, "") || "/";

    navLinks.forEach((link) => {
      const href = link.getAttribute("href");
      if (!href || href.startsWith("#") || href.startsWith("javascript:")) return;

      try {
        const linkPath = new URL(link.href, window.location.origin).pathname.replace(/\/+$/, "") || "/";
        if (linkPath === currentPath) {
          link.classList.add("active");
          link.setAttribute("aria-current", "page");
        } else {
          link.classList.remove("active");
          link.removeAttribute("aria-current");
        }
      } catch (e) {}
    });
  }

  /* ==========================================================================
     Reading Progress Bar
     ========================================================================== */
  function initReadingProgress() {
    const progressBar = document.getElementById("readingProgress");
    if (!progressBar) return;

    function updateProgress() {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
      const clamped = Math.min(100, Math.max(0, progress));

      progressBar.style.width = clamped + "%";
      progressBar.setAttribute("aria-valuenow", Math.round(clamped));
    }

    window.addEventListener("scroll", updateProgress, { passive: true });
    window.addEventListener("resize", updateProgress);
    updateProgress();
  }

  /* ==========================================================================
     Scroll To Top Button
     ========================================================================== */
  function initScrollToTop() {
    const scrollBtn = document.getElementById("scrollToTopBtn");
    if (!scrollBtn) return;

    function checkScroll() {
      const scrolled = window.pageYOffset || document.documentElement.scrollTop;
      if (scrolled > 300) {
        scrollBtn.classList.add("is-visible");
      } else {
        scrollBtn.classList.remove("is-visible");
      }
    }

    window.addEventListener("scroll", checkScroll, { passive: true });
    checkScroll();

    scrollBtn.addEventListener("click", () => {
      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    });
  }

  /* ==========================================================================
     Contact Email Copy Button
     ========================================================================== */
  function initContactCopy() {
    const copyBtn = document.getElementById("copyEmailBtn");
    if (!copyBtn) return;

    copyBtn.addEventListener("click", async () => {
      const email = copyBtn.dataset.email || "engineerhashimi9@gmail.com";
      const label = copyBtn.querySelector("span");
      const icon = copyBtn.querySelector("i");

      try {
        await navigator.clipboard.writeText(email);
        copyBtn.classList.add("is-copied");
        if (label) label.textContent = "Copied to clipboard!";
        if (icon) icon.className = "fas fa-check";

        setTimeout(() => {
          copyBtn.classList.remove("is-copied");
          if (label) label.textContent = "Copy email";
          if (icon) icon.className = "fas fa-copy";
        }, 2200);
      } catch (err) {
        if (label) label.textContent = "Failed to copy";
        setTimeout(() => {
          if (label) label.textContent = "Copy email";
        }, 2000);
      }
    });
  }

  /* ==========================================================================
     Smooth Anchor Link Scrolling
     ========================================================================== */
  function initSmoothAnchors() {
    document.querySelectorAll('a[href^="#"]:not([href="#"]):not([data-bs-toggle])').forEach((anchor) => {
      anchor.addEventListener("click", function (e) {
        const targetId = this.getAttribute("href");
        try {
          const targetElem = document.querySelector(targetId);
          if (targetElem) {
            e.preventDefault();
            const navHeight = document.getElementById("mainNav")?.offsetHeight || 70;
            const targetPos = targetElem.getBoundingClientRect().top + window.pageYOffset - navHeight - 16;
            window.scrollTo({
              top: targetPos,
              behavior: "smooth",
            });
          }
        } catch (err) {}
      });
    });
  }

  /* ==========================================================================
     Scroll Reveal Animations (IntersectionObserver)
     ========================================================================== */
  function initScrollReveal() {
    const revealTargets = document.querySelectorAll(
      ".reveal, .reveal-up, .post-card, .comment-section, .content-card, .profile-card"
    );
    if (!revealTargets.length) return;

    if (!("IntersectionObserver" in window)) {
      revealTargets.forEach((el) => el.classList.add("is-revealed"));
      return;
    }

    const observer = new IntersectionObserver(
      (entries, obs) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-revealed");
            obs.unobserve(entry.target);
          }
        });
      },
      {
        threshold: 0.1,
        rootMargin: "0px 0px -40px 0px",
      }
    );

    revealTargets.forEach((el) => {
      el.classList.add("reveal-init");
      observer.observe(el);
    });
  }

  /* ==========================================================================
     Subtle Particle Canvas Background Animation
     ========================================================================== */
  function initParticleCanvas() {
    const canvas = document.getElementById("particleCanvas");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let width = 0;
    let height = 0;
    let particles = [];
    const maxParticles = window.innerWidth < 768 ? 28 : 55;
    const connectDistance = window.innerWidth < 768 ? 90 : 130;

    function getThemeColors() {
      const isLight = document.documentElement.classList.contains("theme-light");
      if (isLight) {
        return {
          particle1: "rgba(99, 102, 241, 0.45)",  // Indigo
          particle2: "rgba(6, 182, 212, 0.40)",   // Cyan
          line: "99, 102, 241",                   // Indigo line RGB
          lineAlpha: 0.10,
        };
      }
      return {
        particle1: "rgba(6, 182, 212, 0.65)",   // Neon Cyan
        particle2: "rgba(139, 92, 246, 0.65)",  // Neon Purple
        line: "6, 182, 212",                    // Cyan line RGB
        lineAlpha: 0.14,
      };
    }

    let colors = getThemeColors();

    window.addEventListener("themechange", () => {
      colors = getThemeColors();
    });

    function resize() {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      width = window.innerWidth;
      height = window.innerHeight;

      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = width + "px";
      canvas.style.height = height + "px";

      ctx.scale(dpr, dpr);
    }

    class Particle {
      constructor() {
        this.reset(true);
      }

      reset(init = false) {
        this.x = init ? Math.random() * width : Math.random() > 0.5 ? 0 : width;
        this.y = init ? Math.random() * height : Math.random() * height;
        this.radius = Math.random() * 1.8 + 1.2;
        this.vx = (Math.random() - 0.5) * 0.45;
        this.vy = (Math.random() - 0.5) * 0.45;
        this.colorType = Math.random() > 0.5 ? 1 : 2;
      }

      update() {
        this.x += this.vx;
        this.y += this.vy;

        if (this.x < 0 || this.x > width) this.vx *= -1;
        if (this.y < 0 || this.y > height) this.vy *= -1;
      }

      draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = this.colorType === 1 ? colors.particle1 : colors.particle2;
        ctx.fill();
      }
    }

    function initParticles() {
      particles = [];
      for (let i = 0; i < maxParticles; i++) {
        particles.push(new Particle());
      }
    }

    function animate() {
      ctx.clearRect(0, 0, width, height);

      // Draw connection lines
      const len = particles.length;
      for (let i = 0; i < len; i++) {
        const p1 = particles[i];
        p1.update();
        p1.draw();

        for (let j = i + 1; j < len; j++) {
          const p2 = particles[j];
          const dx = p1.x - p2.x;
          const dy = p1.y - p2.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < connectDistance) {
            const alpha = (1 - dist / connectDistance) * colors.lineAlpha;
            ctx.beginPath();
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = `rgba(${colors.line}, ${alpha})`;
            ctx.lineWidth = 0.8;
            ctx.stroke();
          }
        }
      }

      particleAnimationId = requestAnimationFrame(animate);
    }

    // Optimization: pause when tab hidden
    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        if (particleAnimationId) cancelAnimationFrame(particleAnimationId);
      } else {
        particleAnimationId = requestAnimationFrame(animate);
      }
    });

    let resizeTimeout;
    window.addEventListener("resize", () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        resize();
        initParticles();
      }, 200);
    });

    resize();
    initParticles();
    animate();
  }

  /* ==========================================================================
     DOM Initialization
     ========================================================================== */
  document.addEventListener("DOMContentLoaded", () => {
    applyTheme(getSavedTheme());
    initThemeToggle();
    initNavScroll();
    initActiveNavLinks();
    initReadingProgress();
    initScrollToTop();
    initContactCopy();
    initSmoothAnchors();
    initScrollReveal();
    initParticleCanvas();
  });
})();
