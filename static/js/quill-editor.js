/*!
 * Quill rich text — syncs to hidden WTForms textareas on submit
 */
(function () {
  const FULL_TOOLBAR = [
    [{ header: [1, 2, 3, false] }],
    ["bold", "italic", "underline", "strike"],
    ["blockquote", "code-block"],
    [{ list: "ordered" }, { list: "bullet" }],
    ["link"],
    ["clean"],
  ];

  const COMPACT_TOOLBAR = [
    ["bold", "italic"],
    ["blockquote", "link"],
    ["clean"],
  ];

  function initEditor(wrap) {
    const field = wrap.querySelector(".quill-sync-field");
    const host = wrap.querySelector(".quill-editor-host");
    if (!field || !host || host.dataset.quillReady) {
      return;
    }

    const mode = wrap.dataset.mode || "full";
    const quill = new Quill(host, {
      theme: "snow",
      modules: {
        toolbar: mode === "compact" ? COMPACT_TOOLBAR : FULL_TOOLBAR,
      },
      placeholder:
        mode === "compact"
          ? "Share your thoughts…"
          : "Write your story — headings, lists, links, and more…",
    });

    host.dataset.quillReady = "1";

    if (field.value && field.value.trim()) {
      quill.clipboard.dangerouslyPasteHTML(field.value);
    }

    const form = wrap.closest("form");
    if (form) {
      form.addEventListener("submit", () => {
        const html = quill.root.innerHTML;
        const empty =
          html === "<p><br></p>" ||
          html === "<p></p>" ||
          !quill.getText().trim();
        field.value = empty ? "" : html;
      });
    }
  }

  function initAll() {
    document.querySelectorAll(".quill-editor-wrap").forEach(initEditor);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAll);
  } else {
    initAll();
  }
})();
