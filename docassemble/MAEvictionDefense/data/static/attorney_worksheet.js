// Jump within the current form without submitting it or replacing its inputs.
(function () {
  "use strict";
  function restoreSavedNone() {
    if (!document.getElementById("made-attorney-menu")) {
      return;
    }
    document.querySelectorAll(".made-attorney-saved-none-container").forEach(function (group) {
      var none = group.querySelector("input.danota-checkbox");
      // Never replace a substantive selection, including an unsaved edit.
      if (none && !none.checked && !group.querySelector("input.danon-nota-checkbox:checked")) {
        window.jQuery(none).prop("checked", true).trigger("change");
      }
    });
  }
  if (window.madeAttorneyJumpHandler) {
    return;
  }
  window.madeAttorneyJumpHandler = true;
  window.jQuery(document).on("daPageLoad", restoreSavedNone);
  document.addEventListener("click", function (event) {
    if (!document.getElementById("made-attorney-menu")) {
      return;
    }
    var link = event.target.closest("a");
    if (!link) {
      return;
    }
    // Docassemble rewrites hash links when it renders Markdown. Recognize
    // that specific wrapper without evaluating its JavaScript.
    var href = link.getAttribute("href") || "";
    var anchor = href.match(/^#(made-attorney-[a-z-]+)$/);
    if (!anchor) {
      anchor = href.match(/^javascript:\s*daGoToAnchor\(\s*["']#(made-attorney-[a-z-]+)["']\s*\);?\s*$/);
    }
    var target = anchor && document.getElementById(anchor[1]);
    if (!target) {
      return;
    }
    event.preventDefault();
    event.stopImmediatePropagation();
    target.scrollIntoView({ block: "start" });
    target.focus({ preventScroll: true });
  }, true);
}());
