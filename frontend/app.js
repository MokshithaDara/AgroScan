// ======================================================
// API CONFIG
// ======================================================

window.API_BASE_URL = "http://127.0.0.1:8000";


// ======================================================
// USER ID (FOR FARMER HISTORY)
// ======================================================

window.getUserId = function () {

  if (!localStorage.getItem("user_id")) {

    localStorage.setItem(
      "user_id",
      "farmer_" + Math.random().toString(36).substring(2, 10)
    );

  }

  return localStorage.getItem("user_id");
};


// ======================================================
// CURRENT PAGE PATH
// ======================================================

window.getCurrentPath = function () {

  const path = window.location.pathname.split("/").pop();

  return path || "home.html";

};


// ======================================================
// NAVIGATION ITEMS
// ======================================================

window.getNavItems = function () {

  return [

    { name: "Home", icon: "🏠", href: "home.html" },

    { name: "Crop Scanner", icon: "📷", href: "index.html" },

    { name: "Dashboard", icon: "📊", href: "dashboard.html" },

    { name: "Advisory", icon: "🌦️", href: "advisory.html" },

    { name: "Knowledge Base", icon: "🌾", href: "library.html" }

  ];

};


// ======================================================
// MAIN UI SHELL
// ======================================================

window.renderShell = function (
  pageTitle,
  pageSubtitle,
  heroGradient = "from-emerald-900 via-green-800 to-lime-700"
) {

  const app = document.getElementById("app");
  const current = getCurrentPath();
  const navItems = getNavItems();

  app.innerHTML = `

  <div class="min-h-screen bg-slate-50 text-slate-800">

    <div class="lg:flex">

      <!-- SIDEBAR -->

      <aside class="hidden lg:flex lg:w-72 xl:w-80 min-h-screen flex-col bg-slate-950 text-white">

        <div class="px-6 py-6 border-b border-white/10">

          <div class="flex items-center gap-3">

            <div class="h-12 w-12 rounded-2xl bg-emerald-500/20 flex items-center justify-center text-2xl">
              🌿
            </div>

            <div>
              <h1 class="text-2xl font-bold tracking-wide">AgroScan</h1>
              <p class="text-sm text-slate-300">Smart Crop Intelligence</p>
            </div>

          </div>

        </div>


        <!-- NAVIGATION -->

        <nav class="px-4 py-6 space-y-2">

          ${navItems.map(item => `
          
          <a
            href="${item.href}"
            class="flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition ${
              current === item.href
                ? "bg-white text-slate-900 shadow-lg"
                : "text-slate-200 hover:bg-white/10"
            }"
          >
            <span>${item.icon}</span>
            <span>${item.name}</span>
          </a>

          `).join("")}

        </nav>


        <!-- FARMER INFO -->

        <div class="mt-auto p-4">

          <div class="rounded-3xl border border-white/10 bg-white/5 p-5">

            <p class="text-sm font-semibold">Farmer ID</p>

            <p class="mt-2 break-all text-xs text-slate-300">
              ${getUserId()}
            </p>

            <p class="mt-3 text-xs leading-6 text-slate-400">

              Upload crop image, detect disease, get treatment, weather advisory,
              and maintain scan history.

            </p>

          </div>

        </div>

      </aside>


      <!-- MAIN CONTENT -->

      <div class="flex-1 min-w-0">


        <!-- HEADER -->

        <header class="sticky top-0 z-40 border-b border-slate-200 bg-white/90 backdrop-blur">

          <div class="flex items-center justify-between px-4 py-4 md:px-6 lg:px-8">

            <div class="flex items-center gap-3">

              <button
                id="mobileMenuBtn"
                class="inline-flex h-11 w-11 items-center justify-center rounded-xl border border-slate-200 bg-white text-lg lg:hidden"
              >
                ☰
              </button>

              <div>

                <h2 class="text-lg md:text-xl font-bold text-slate-900">
                  ${pageTitle}
                </h2>

                <p class="text-xs md:text-sm text-slate-500">
                  ${pageSubtitle}
                </p>

              </div>

            </div>

            <div class="hidden md:flex items-center gap-3">

              <span class="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                AI Agriculture Platform
              </span>

            </div>

          </div>

        </header>


        <!-- PAGE BODY -->

        <main class="p-4 md:p-6 lg:p-8">

          <section class="mb-8 rounded-[28px] bg-gradient-to-r ${heroGradient} p-6 md:p-8 text-white shadow-2xl">

            <h3 class="text-3xl md:text-4xl font-bold">
              ${pageTitle}
            </h3>

            <p class="mt-3 max-w-2xl text-sm md:text-base text-white/85 leading-7">
              ${pageSubtitle}
            </p>

          </section>

          <div id="pageContent"></div>

        </main>

      </div>

    </div>

  </div>

  `;


  // MOBILE MENU

  const mobileMenuBtn = document.getElementById("mobileMenuBtn");

  if (mobileMenuBtn) {

    mobileMenuBtn.addEventListener("click", () => {

      alert("Mobile navigation coming soon");

    });

  }

};


// ======================================================
// DASHBOARD STAT CARD
// ======================================================

window.createStatCard = function (

  title,
  value,
  subtext,
  tone = "emerald"

) {

  const tones = {

    emerald: "bg-emerald-50 border-emerald-100 text-emerald-900",

    cyan: "bg-cyan-50 border-cyan-100 text-cyan-900",

    amber: "bg-amber-50 border-amber-100 text-amber-900",

    rose: "bg-rose-50 border-rose-100 text-rose-900",

    slate: "bg-slate-50 border-slate-200 text-slate-900"

  };

  return `

  <div class="rounded-3xl border p-5 ${tones[tone] || tones.slate}">

    <p class="text-xs uppercase tracking-wide opacity-70">
      ${title}
    </p>

    <p class="mt-3 text-2xl font-bold">
      ${value}
    </p>

    <p class="mt-2 text-sm opacity-80">
      ${subtext}
    </p>

  </div>

  `;

};


// ======================================================
// INITIALIZE USER ID
// ======================================================

document.addEventListener("DOMContentLoaded", () => {

  getUserId();

});


// ======================================================
// SCROLL ANIMATION
// ======================================================

function revealOnScroll() {

  const elements = document.querySelectorAll(".fade-up");

  elements.forEach(el => {

    const windowHeight = window.innerHeight;
    const elementTop = el.getBoundingClientRect().top;

    if (elementTop < windowHeight - 80) {

      el.classList.add("show");

    }

  });

}

window.addEventListener("scroll", revealOnScroll);
window.addEventListener("load", revealOnScroll);