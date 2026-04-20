let currentHistoryPage = 1;
const HISTORY_PAGE_SIZE = 9;
let totalHistoryPages = 1;
let currentHistoryItems = [];


function renderHistoryLoading(targetId = "history") {
  const el = document.getElementById(targetId);
  if (!el) return;

  el.innerHTML = `
    <div class="md:col-span-2 rounded-3xl border border-slate-200 bg-slate-50 p-8 text-center">
      <div class="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-emerald-100 border-t-emerald-700"></div>
      <p class="mt-4 text-sm font-medium text-slate-700">Loading scan history...</p>
    </div>
  `;
}


function renderHistoryError(message, targetId = "history") {
  const el = document.getElementById(targetId);
  if (!el) return;

  el.innerHTML = `
    <div class="md:col-span-2 rounded-3xl border border-red-200 bg-red-50 p-6 text-red-700">
      <p class="font-semibold">Could not load scan history</p>
      <p class="mt-2 text-sm">${escapeHTML(message)}</p>
    </div>
  `;
}


function updatePaginationControls(page, totalPages) {
  const slider = document.getElementById("historyPageSlider");
  const info = document.getElementById("historyPageInfo");
  const prevBtn = document.getElementById("historyPrevBtn");
  const nextBtn = document.getElementById("historyNextBtn");

  if (slider) {
    slider.min = "1";
    slider.max = String(Math.max(1, totalPages));
    slider.value = String(Math.min(Math.max(1, page), Math.max(1, totalPages)));
  }

  if (info) {
    info.textContent = `Page ${page} / ${totalPages}`;
  }

  if (prevBtn) prevBtn.disabled = page <= 1;
  if (nextBtn) nextBtn.disabled = page >= totalPages;
}


function renderBulletList(items, emptyLabel) {
  const safeItems = Array.isArray(items) ? items.filter(Boolean) : [];
  if (!safeItems.length) {
    return `<p class="text-sm text-slate-500">${escapeHTML(emptyLabel)}</p>`;
  }
  return `
    <ul class="space-y-1 text-sm text-slate-700">
      ${safeItems.map((item) => `<li>- ${escapeHTML(String(item))}</li>`).join("")}
    </ul>
  `;
}


function ensureHistoryModal() {
  if (document.getElementById("historyModal")) return;
  document.body.insertAdjacentHTML(
    "beforeend",
    `
    <div id="historyModal" class="fixed inset-0 z-[100] hidden">
      <div id="historyModalBackdrop" class="absolute inset-0 bg-black/40"></div>
      <div class="absolute inset-0 flex items-center justify-center p-4">
        <div class="w-full max-w-2xl rounded-3xl border border-slate-200 bg-white p-6 shadow-2xl">
          <div class="flex items-center justify-between gap-3">
            <h4 class="text-xl font-semibold text-slate-900">Scan Details</h4>
            <button id="historyModalClose" class="rounded-lg border border-slate-300 bg-white px-3 py-1 text-sm font-semibold text-slate-700 hover:bg-slate-50">Close</button>
          </div>
          <div id="historyModalContent" class="mt-4"></div>
        </div>
      </div>
    </div>
    `
  );

  const modal = document.getElementById("historyModal");
  const backdrop = document.getElementById("historyModalBackdrop");
  const closeBtn = document.getElementById("historyModalClose");

  const closeModal = () => modal?.classList.add("hidden");
  backdrop?.addEventListener("click", closeModal);
  closeBtn?.addEventListener("click", closeModal);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModal();
  });
}

function openHistoryModal(scan) {
  ensureHistoryModal();
  const modal = document.getElementById("historyModal");
  const content = document.getElementById("historyModalContent");
  if (!modal || !content) return;

  const treatmentSteps = Array.isArray(scan.treatment_steps) && scan.treatment_steps.length
    ? scan.treatment_steps
    : String(scan.treatment || "")
        .split(".")
        .map((s) => s.trim())
        .filter(Boolean);
  const productsRecommended = Array.isArray(scan.products_recommended)
    ? scan.products_recommended
    : [];

  content.innerHTML = `
    <div class="space-y-4">
      <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
        <p class="text-xs uppercase tracking-wide text-slate-500">Disease</p>
        <p class="mt-1 text-lg font-semibold text-slate-900">${escapeHTML(scan.disease || "Unknown")}</p>
        <p class="mt-2 text-sm text-slate-600">Location: ${escapeHTML(scan.location || "N/A")}</p>
        <p class="text-sm text-slate-600">Date: ${escapeHTML(scan.date || "N/A")}</p>
      </div>
      <div class="grid gap-3 sm:grid-cols-2">
        <div class="rounded-2xl border border-emerald-100 bg-emerald-50 p-4">
          <p class="font-semibold text-emerald-800">Treatment Suggested</p>
          <div class="mt-2">${renderBulletList(treatmentSteps, "No treatment recorded")}</div>
        </div>
        <div class="rounded-2xl border border-cyan-100 bg-cyan-50 p-4">
          <p class="font-semibold text-cyan-800">Products Recommended</p>
          <div class="mt-2">${renderBulletList(productsRecommended, "No products saved")}</div>
        </div>
      </div>
    </div>
  `;

  modal.classList.remove("hidden");
}

function attachHistoryCardHandlers(targetId = "history") {
  const root = document.getElementById(targetId);
  if (!root) return;
  ensureHistoryModal();

  root.querySelectorAll("[data-scan-index]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const idx = Number(btn.getAttribute("data-scan-index"));
      const scan = currentHistoryItems[idx];
      if (scan) openHistoryModal(scan);
    });
  });
}


async function loadHistory(targetId = "history", page = 1) {
  const user_id = getUserId();
  renderHistoryLoading(targetId);

  try {
    const res = await fetch(
      `${API_BASE_URL}/history/${user_id}?page=${encodeURIComponent(page)}&page_size=${HISTORY_PAGE_SIZE}`
    );

    let data = null;
    try {
      data = await res.json();
    } catch {
      data = null;
    }

    if (!res.ok) {
      throw new Error(
        data?.detail ||
        `History request failed (${res.status} ${res.statusText}).`
      );
    }

    currentHistoryPage = data.current_page ?? page;
    totalHistoryPages = data.total_pages ?? 1;

    updatePaginationControls(currentHistoryPage, totalHistoryPages);

    const totalScans = document.getElementById("totalScans");
    const latestDisease = document.getElementById("latestDisease");

    if (totalScans) totalScans.textContent = data.total_scans ?? 0;

    if (!data.history || data.history.length === 0) {
      if (latestDisease) latestDisease.textContent = "-";

      document.getElementById(targetId).innerHTML = `
        <div class="md:col-span-2 rounded-3xl border border-slate-200 bg-slate-50 p-8 text-center">
          <p class="text-lg font-semibold text-slate-800">No scan history found</p>
          <p class="mt-2 text-sm text-slate-500">
            Scan a crop first from the Crop Scanner page.
          </p>
        </div>
      `;
      return;
    }

    currentHistoryItems = data.history;

    if (latestDisease) {
      latestDisease.textContent = data.history[0].disease || "-";
    }

    let html = "";

    data.history.forEach((scan, index) => {
      const diseaseEscaped = escapeHTML(scan.disease || "Unknown");
      const locationEscaped = escapeHTML(scan.location || "N/A");
      const dateEscaped = escapeHTML(scan.date || "N/A");
      const serialNo = (currentHistoryPage - 1) * HISTORY_PAGE_SIZE + index + 1;
      const treatmentSteps = Array.isArray(scan.treatment_steps) && scan.treatment_steps.length
        ? scan.treatment_steps
        : String(scan.treatment || "")
            .split(".")
            .map((s) => s.trim())
            .filter(Boolean);
      const productsRecommended = Array.isArray(scan.products_recommended)
        ? scan.products_recommended
        : [];
      html += `
        <div class="rounded-3xl border border-slate-200 bg-white p-5 shadow transition-all duration-200 hover:-translate-y-0.5 hover:border-emerald-300 hover:bg-emerald-50/40 hover:shadow-md">
          <button type="button" data-scan-index="${index}" class="flex w-full cursor-pointer items-start justify-between gap-4 text-left">
            <div>
              <p class="text-xs uppercase tracking-wide text-slate-500">Scan ${serialNo}</p>
              <h5 class="mt-2 text-lg font-semibold text-slate-900">${diseaseEscaped}</h5>
            </div>
            <div class="flex items-center gap-3">
              <span class="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                ${locationEscaped}
              </span>
            </div>
          </button>

          <div class="mt-5 space-y-3 text-sm text-slate-600">
            <p>
              <span class="font-semibold text-slate-800">Date:</span>
              ${dateEscaped}
            </p>

            <p>
              <span class="font-semibold text-slate-800">Location:</span>
              ${locationEscaped}
            </p>
          </div>
        </div>
      `;
    });

    document.getElementById(targetId).innerHTML = html;
    attachHistoryCardHandlers(targetId);
  } catch (error) {
    console.error("History load error:", error);
    const msg = String(error?.message || "");
    const isNetworkFetchError =
      msg.toLowerCase().includes("failed to fetch") ||
      msg.toLowerCase().includes("networkerror") ||
      msg.toLowerCase().includes("load failed");

    renderHistoryError(
      isNetworkFetchError
        ? "Cannot reach backend API. Check backend is running at " + API_BASE_URL
        : (error.message || "Failed to connect to backend."),
      targetId
    );
  }
}


function initHistoryPagination() {
  const prevBtn = document.getElementById("historyPrevBtn");
  const nextBtn = document.getElementById("historyNextBtn");
  const slider = document.getElementById("historyPageSlider");

  if (prevBtn) {
    prevBtn.addEventListener("click", () => {
      if (currentHistoryPage > 1) {
        loadHistory("history", currentHistoryPage - 1);
      }
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener("click", () => {
      if (currentHistoryPage < totalHistoryPages) {
        loadHistory("history", currentHistoryPage + 1);
      }
    });
  }

  if (slider) {
    slider.addEventListener("input", (e) => {
      const nextPage = Number(e.target.value || "1");
      updatePaginationControls(nextPage, totalHistoryPages);
    });

    slider.addEventListener("change", (e) => {
      const nextPage = Number(e.target.value || "1");
      if (nextPage !== currentHistoryPage) {
        loadHistory("history", nextPage);
      }
    });
  }
}
