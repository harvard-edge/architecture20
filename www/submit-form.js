(function () {
  const config = window.arch2SubmitConfig;
  if (!config) {
    return;
  }

  const form = document.getElementById(config.formId || "submission-form");
  const previewBody = document.getElementById(config.bodyPreviewId || "submit-body-preview");
  const copyButton = document.getElementById(config.copyButtonId || "copy-submit-body");
  const labels = config.labels || [];

  if (!form || !previewBody || !copyButton) {
    return;
  }

  function value(name) {
    return (form.elements[name]?.value || "").trim();
  }

  function issueBody() {
    return labels.map(([label, name]) => {
      return `### ${label}\n\n${value(name) || "_No response_"}`;
    }).join("\n\n");
  }

  function updatePreview() {
    (config.preview || []).forEach(([selector, name, fallback]) => {
      const element = document.querySelector(selector);
      if (element) {
        element.textContent = value(name) || fallback || "";
      }
    });
    previewBody.value = issueBody();
  }

  function githubUrl() {
    const params = new URLSearchParams();
    const titleValue = value(config.titleField) || config.titleFallback || "";

    params.set("template", config.template);
    params.set("title", `${config.titlePrefix || ""}${titleValue}`);
    labels.forEach(([, name]) => {
      const fieldValue = value(name);
      if (fieldValue) {
        params.set(name, fieldValue);
      }
    });

    return `${config.issueUrl || "https://github.com/harvard-edge/arch2/issues/new"}?${params.toString()}`;
  }

  form.addEventListener("input", updatePreview);
  form.addEventListener("change", updatePreview);
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    updatePreview();
    if (!form.reportValidity()) {
      return;
    }
    window.open(githubUrl(), "_blank", "noopener");
  });

  copyButton.addEventListener("click", async function () {
    updatePreview();
    await navigator.clipboard.writeText(previewBody.value);
    copyButton.textContent = "Copied";
    window.setTimeout(() => {
      copyButton.textContent = config.copyLabel || "Copy generated body";
    }, 1400);
  });

  updatePreview();
})();
