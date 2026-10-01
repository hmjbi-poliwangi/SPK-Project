// ============================================================
// SPK Profile Matching - Utility Functions
// ============================================================

/**
 * Escape HTML special characters to prevent XSS.
 */
function escapeHtml(text) {
  if (!text) return "";
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Show an alert notification at the top of the content area.
 * @param {string} message - The message to display.
 * @param {string} type - 'success' | 'error' | 'info'
 */
function showAlert(message, type) {
  const container = document.getElementById("alert-container");
  const alert = document.createElement("div");
  alert.className = `alert alert-${type} animate-alert-in`;
  alert.textContent = message;
  container.appendChild(alert);

  setTimeout(() => {
    alert.style.opacity = "0";
    alert.style.transition = "opacity 0.3s";
    setTimeout(() => alert.remove(), 300);
  }, 3000);
}

/**
 * Show simple user-friendly error on screen, log technical detail to console.
 * @param {string} technicalError - The actual error detail (logged to console).
 * @param {string} simpleMessage - Simple message to display (e.g. "Data sudah ada/duplikat!").
 */
function showSimpleError(technicalError, simpleMessage) {
  console.error(technicalError);
  showAlert(simpleMessage || 'Terjadi kesalahan', 'error');
}

/**
 * Open a modal overlay by its id.
 */
function openModal(id) {
  const modal = document.getElementById(id);
  modal.classList.add('open');
  document.body.style.overflow = 'hidden';
}

/**
 * Close a modal overlay by its id.
 */
function closeModal(id) {
  const modal = document.getElementById(id);
  modal.classList.remove('open');
  document.body.style.overflow = '';
}

// Close modal when clicking outside the dialog
document.addEventListener("click", function (e) {
  if (e.target.classList.contains("modal-overlay")) {
    e.target.classList.remove("open");
    document.body.style.overflow = '';
  }
});

// Close modal with Escape key
document.addEventListener("keydown", function (e) {
  if (e.key === "Escape" || e.key === "Esc" || e.keyCode === 27) {
    document
      .querySelectorAll(".modal-overlay.open")
      .forEach((m) => {
        m.classList.remove("open");
      });
    document.body.style.overflow = '';
  }
});

// Mobile menu toggle
document.addEventListener("DOMContentLoaded", function () {
  const mobileMenuBtn = document.getElementById("mobile-menu-btn");
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebar-overlay");

  if (mobileMenuBtn && sidebar && overlay) {
    mobileMenuBtn.addEventListener("click", function () {
      sidebar.classList.toggle("-translate-x-full");
      overlay.classList.toggle("hidden");
    });

    overlay.addEventListener("click", function () {
      sidebar.classList.add("-translate-x-full");
      overlay.classList.add("hidden");
    });
  }

  // Highlight active page in sidebar
  const path = window.location.pathname;
  const navBtns = document.querySelectorAll(".sidebar .nav-btn");
  navBtns.forEach((btn) => {
    const page = btn.getAttribute("data-page");
    if (page && path.includes(page)) {
      btn.classList.add("active");
    }
  });

  // Activate resizable columns on all data-tables
  document
    .querySelectorAll(".data-table")
    .forEach((tbl) => makeTableResizable(tbl));
});

// ============================================================
// Resizable Table Columns (drag column borders)
// ============================================================

/**
 * Enable column resizing by dragging the right border of each TH.
 * The table must have `table-layout: fixed` for reliable behaviour.
 * Column widths are saved to localStorage so they persist across page refreshes.
 */
function makeTableResizable(table) {
  const storageKey =
    "colwidths_" +
    window.location.pathname.replace(/\//g, "_") +
    "_" +
    (table.id || "tbl");

  const saved = localStorage.getItem(storageKey);
  if (saved) {
    try {
      const widths = JSON.parse(saved);
      const cols = table.querySelectorAll("th");
      cols.forEach((th, i) => {
        if (widths[i] && widths[i] > 0) {
          th.style.width = widths[i] + "px";
          th.style.minWidth = widths[i] + "px";
        }
      });
    } catch (e) {
      /* ignore corrupt data */
    }
  }

  const cols = table.querySelectorAll("th");
  cols.forEach((th, idx) => {
    if (th.querySelector(".resize-handle")) return;

    const handle = document.createElement("div");
    handle.className = "resize-handle";
    th.appendChild(handle);

    handle.addEventListener("mousedown", function (e) {
      e.preventDefault();
      e.stopPropagation();

      const startX = e.clientX;
      const startWidth = th.offsetWidth;

      function onMouseMove(ev) {
        const diff = ev.clientX - startX;
        const newWidth = Math.max(40, startWidth + diff);
        th.style.width = newWidth + "px";
        th.style.minWidth = newWidth + "px";
      }

      function onMouseUp() {
        document.removeEventListener("mousemove", onMouseMove);
        document.removeEventListener("mouseup", onMouseUp);
        document.body.style.cursor = "";
        document.body.style.userSelect = "";

        const allCols = table.querySelectorAll("th");
        const widths = {};
        allCols.forEach((c, i) => {
          widths[i] = c.offsetWidth;
        });
        try {
          localStorage.setItem(storageKey, JSON.stringify(widths));
        } catch (e) {
          /* storage full, ignore */
        }
      }

      document.addEventListener("mousemove", onMouseMove);
      document.addEventListener("mouseup", onMouseUp);
      document.body.style.cursor = "col-resize";
      document.body.style.userSelect = "none";
    });
  });
}
