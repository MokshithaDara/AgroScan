function initDashboardPage() {

  const farmerIdElement = document.getElementById("farmerIdText");

  if (farmerIdElement) {
    farmerIdElement.textContent = getUserId();
  }

  loadHistory();
}


// -----------------------------------------------------
// LOADING UI
// -----------------------------------------------------

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


// -----------------------------------------------------
// ERROR UI
// -----------------------------------------------------

function renderHistoryError(message, targetId = "history") {

  const el = document.getElementById(targetId);

  if (!el) return;

  el.innerHTML = `
    <div class="md:col-span-2 rounded-3xl border border-red-200 bg-red-50 p-6 text-red-700">
      <p class="font-semibold">Could not load scan history</p>
      <p class="mt-2 text-sm">${message}</p>
    </div>
  `;

}


// -----------------------------------------------------
// LOAD HISTORY FROM FASTAPI
// -----------------------------------------------------

async function loadHistory(targetId = "history") {

  const user_id = getUserId();

  renderHistoryLoading(targetId);

  try {

    const res = await fetch(`${API_BASE_URL}/history/${user_id}`);

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || "Failed to fetch history.");
    }

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

    if (latestDisease) {
      latestDisease.textContent = data.history[0].disease || "-";
    }

    let html = "";

    data.history.forEach((scan, index) => {

      html += `

        <div class="rounded-3xl border border-slate-200 bg-white p-5 shadow">

          <div class="flex items-start justify-between gap-4">

            <div>
              <p class="text-xs uppercase tracking-wide text-slate-500">
                Scan ${index + 1}
              </p>

              <h5 class="mt-2 text-lg font-semibold text-slate-900">
                ${scan.disease || "Unknown"}
              </h5>
            </div>

            <span class="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
              ${scan.location || "N/A"}
            </span>

          </div>

          <div class="mt-5 space-y-3 text-sm text-slate-600">

            <p>
              <span class="font-semibold text-slate-800">Date:</span>
              ${scan.date || "N/A"}
            </p>

            <p>
              <span class="font-semibold text-slate-800">Location:</span>
              ${scan.location || "N/A"}
            </p>

          </div>

        </div>

      `;

    });

    document.getElementById(targetId).innerHTML = html;

  } catch (error) {

    console.error("History load error:", error);

    renderHistoryError(
      error.message || "Failed to connect to backend.",
      targetId
    );

  }

}