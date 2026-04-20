function toNumber(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

const ADVISORY_CACHE_KEY = "agroscan_advisory_cache_v1";
const ADVISORY_CACHE_TTL_MS = 10 * 60 * 1000;

function getAdvisoryCacheStore() {
  try {
    const raw = localStorage.getItem(ADVISORY_CACHE_KEY);
    const parsed = raw ? JSON.parse(raw) : {};
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch (_error) {
    return {};
  }
}

function getAdvisoryCacheEntry(cacheKey) {
  const store = getAdvisoryCacheStore();
  const entry = store[cacheKey];
  if (!entry || !entry.savedAt || !entry.payload) return null;
  if (Date.now() - entry.savedAt > ADVISORY_CACHE_TTL_MS) return null;
  return entry.payload;
}

function setAdvisoryCacheEntry(cacheKey, payload) {
  const store = getAdvisoryCacheStore();
  store[cacheKey] = { savedAt: Date.now(), payload };
  try {
    localStorage.setItem(ADVISORY_CACHE_KEY, JSON.stringify(store));
  } catch (_error) {
    // Ignore quota-related failures.
  }
}

function classifyRisk(score) {
  if (score >= 75) return { level: "Severe", tone: "rose" };
  if (score >= 55) return { level: "High", tone: "amber" };
  if (score >= 30) return { level: "Moderate", tone: "cyan" };
  return { level: "Low", tone: "emerald" };
}

function buildAdvisory(temp, humidity, conditionRaw) {
  const condition = String(conditionRaw || "").toLowerCase();
  const isRainy = /(rain|drizzle|thunderstorm)/.test(condition);
  const isCloudy = /(cloud|mist|fog|haze)/.test(condition);

  let riskScore = 10;
  const reasons = [];
  const actions = [];

  if (humidity !== null) {
    if (humidity >= 85) {
      riskScore += 35;
      reasons.push(`Humidity is very high (${humidity}%), which strongly favors fungal spread.`);
      actions.push("Start preventive protection and inspect shaded lower canopy today.");
    } else if (humidity >= 75) {
      riskScore += 20;
      reasons.push(`Humidity is elevated (${humidity}%), so leaf-wetness duration can increase.`);
      actions.push("Improve airflow and avoid late-evening irrigation.");
    } else if (humidity <= 40) {
      riskScore += 8;
      reasons.push(`Humidity is low (${humidity}%), which can stress crop vigor.`);
      actions.push("Use moisture-conserving irrigation timing and mulching.");
    } else {
      reasons.push(`Humidity is moderate (${humidity}%), currently manageable with routine scouting.`);
    }
  }

  if (temp !== null) {
    if (temp >= 35) {
      riskScore += 18;
      reasons.push(`Temperature is high (${temp} C), increasing crop stress risk.`);
      actions.push("Prefer irrigation in early morning or evening.");
    } else if (temp <= 18) {
      riskScore += 10;
      reasons.push(`Temperature is cool (${temp} C), which can support moisture-driven leaf diseases.`);
      actions.push("Check leaves for early lesion or mildew signs.");
    } else {
      reasons.push(`Temperature is within a moderate range (${temp} C).`);
    }
  }

  if (isRainy) {
    riskScore += 25;
    reasons.push("Rain is present, which may spread infection and reduce spray retention.");
    actions.push("Avoid spray before rain; use the first stable dry window.");
  } else if (isCloudy && humidity !== null && humidity >= 75) {
    riskScore += 8;
    reasons.push("Cloud + high humidity can keep foliage wet for longer periods.");
    actions.push("Prioritize morning scouting and drainage checks.");
  }

  riskScore = Math.max(0, Math.min(100, riskScore));
  const risk = classifyRisk(riskScore);

  if (!actions.length) {
    actions.push("Continue routine crop scouting every 48 hours.");
    actions.push("Maintain sanitation and remove suspect plant debris.");
  }

  return {
    riskScore,
    riskLevel: risk.level,
    riskTone: risk.tone,
    reasons: Array.from(new Set(reasons)).slice(0, 3),
    actions: Array.from(new Set(actions)).slice(0, 3),
  };
}

function riskToneClasses(tone) {
  const map = {
    rose: "bg-rose-50 border-rose-200 text-rose-800",
    amber: "bg-amber-50 border-amber-200 text-amber-800",
    cyan: "bg-cyan-50 border-cyan-200 text-cyan-800",
    emerald: "bg-emerald-50 border-emerald-200 text-emerald-800",
  };
  return map[tone] || map.emerald;
}

function decisionConfig(advisory) {
  const level = String(advisory.riskLevel || "").toLowerCase();
  if (level === "severe" || level === "high") {
    return {
      badge: "High Risk",
      title: "Spray Planning Required",
      subtitle: "Schedule treatment in the next 12-24 hours.",
      nextCheck: "Next check: 24 hours",
      tone: "bg-rose-50 border-rose-200 text-rose-900",
    };
  }
  if (level === "moderate") {
    return {
      badge: "Watchful",
      title: "Preventive Action Window",
      subtitle: "Prepare preventive spray and tighten scouting now.",
      nextCheck: "Next check: 24 hours",
      tone: "bg-amber-50 border-amber-200 text-amber-900",
    };
  }
  return {
    badge: "Safe Conditions",
    title: "No Immediate Spray Needed",
    subtitle: "Continue routine monitoring and field hygiene.",
    nextCheck: "Next check: 48 hours",
    tone: "bg-emerald-50 border-emerald-200 text-emerald-900",
  };
}

function toHourLabel(hour) {
  const h = Number(hour);
  if (!Number.isFinite(h)) return "";
  if (h === 0) return "12 AM";
  if (h < 12) return `${h} AM`;
  if (h === 12) return "12 PM";
  return `${h - 12} PM`;
}

function windowLabelFromStart(startValue) {
  const start = String(startValue || "");
  const timePart = start.split(" ")[1] || "";
  const hour = Number((timePart.split(":")[0] || "").trim());
  if (!Number.isFinite(hour)) return null;

  if (hour >= 5 && hour <= 10) return "Morning";
  if (hour >= 16 && hour <= 19) return "Evening";
  if (hour >= 20 || hour <= 4) return "Night";
  return "Daytime";
}

function summarizeSprayWindows(sprayWindows) {
  const windows = Array.isArray(sprayWindows) ? sprayWindows : [];
  if (!windows.length) {
    return {
      bestText: "No strong spray slot currently available.",
      cards: [],
    };
  }

  const groups = new Map();
  for (const w of windows) {
    const label = windowLabelFromStart(w.start) || "Best Slot";
    if (!groups.has(label)) groups.set(label, []);
    groups.get(label).push(w);
  }

  const preferredOrder = ["Morning", "Evening", "Night", "Daytime", "Best Slot"];
  const cards = [];
  for (const label of preferredOrder) {
    const bucket = groups.get(label);
    if (!bucket || !bucket.length) continue;
    const first = bucket[0];
    const firstTime = String(first.start || "");
    const firstHour = Number(((firstTime.split(" ")[1] || "").split(":")[0] || "").trim());
    const slotStart = toHourLabel(firstHour);
    const slotEnd = toHourLabel(Number.isFinite(firstHour) ? (firstHour + 3) % 24 : null);

    cards.push({
      label,
      slot: slotStart && slotEnd ? `${slotStart} - ${slotEnd}` : firstTime,
      wind: first.wind_kmh,
      rain: first.rain_mm_3h,
    });

    if (cards.length === 2) break;
  }

  const primary = cards[0];
  const bestText = primary
    ? `${primary.label} window: ${primary.slot}`
    : "No strong spray slot currently available.";

  return { bestText, cards };
}

function riskPillClasses(levelRaw) {
  const level = String(levelRaw || "").toLowerCase();
  if (level.includes("severe") || level.includes("very high")) {
    return "bg-rose-100 text-rose-800 border border-rose-200";
  }
  if (level.includes("high")) {
    return "bg-amber-100 text-amber-800 border border-amber-200";
  }
  if (level.includes("moderate")) {
    return "bg-cyan-100 text-cyan-800 border border-cyan-200";
  }
  return "bg-emerald-100 text-emerald-800 border border-emerald-200";
}

async function getWeather() {
  const location = document.getElementById("loc").value.trim();
  if (!location) {
    alert("Please enter location");
    return;
  }

  const weatherDiv = document.getElementById("weather");
  const cacheKey = `weather|${location.toLowerCase()}`;
  const cached = getAdvisoryCacheEntry(cacheKey);
  if (cached) {
    renderWeatherCard(window.normalizePayload(cached), location, weatherDiv);
    return;
  }

  weatherDiv.innerHTML = `
  <div class="rounded-2xl border border-slate-200 bg-white p-8 text-center shadow">
    <div class="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-cyan-200 border-t-cyan-700"></div>
    <p class="mt-4 text-sm text-gray-600">Fetching weather data...</p>
  </div>
  `;

  try {
    const res = await fetch(`${API_BASE_URL}/weather?location=${encodeURIComponent(location)}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Unable to fetch weather data");

    setAdvisoryCacheEntry(cacheKey, data);
    renderWeatherCard(window.normalizePayload(data), location, weatherDiv);
  } catch (error) {
    weatherDiv.innerHTML = `
    <div class="rounded-xl border border-red-200 bg-red-50 p-6 text-red-700">
      ${escapeHTML(error.message || "Unable to fetch weather data")}
    </div>
    `;
  }
}

function renderWeatherCard(data, location, weatherDiv) {
  const temp = toNumber(data.temperature);
  const humidity = toNumber(data.humidity);
  const condition = data.condition ?? "N/A";
  const locationEscaped = escapeHTML(location);

  const advisory = buildAdvisory(temp, humidity, condition);
  const toneClasses = riskToneClasses(advisory.riskTone);
  const decision = decisionConfig(advisory);

  const reasonsHtml = advisory.reasons
    .map((r) => `<li class="text-sm text-slate-700">- ${escapeHTML(r)}</li>`)
    .join("");

  const actionsHtml = advisory.actions
    .map((a) => `<li class="text-sm text-slate-700">- ${escapeHTML(a)}</li>`)
    .join("");

  weatherDiv.innerHTML = `
  <div class="space-y-5">
    <div class="rounded-3xl border p-5 shadow ${decision.tone}">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <span class="rounded-full border px-3 py-1 text-xs font-semibold">${escapeHTML(decision.badge)}</span>
        <span class="text-xs font-semibold">${escapeHTML(decision.nextCheck)}</span>
      </div>
      <h3 class="mt-3 text-xl font-semibold">${escapeHTML(decision.title)}</h3>
      <p class="mt-1 text-sm">${escapeHTML(decision.subtitle)}</p>
    </div>

    <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow">
      <div class="flex items-center justify-between gap-4">
        <div>
          <h3 class="text-xl font-semibold text-slate-900">Current Weather</h3>
          <p class="text-sm text-slate-500">${locationEscaped}</p>
        </div>
        <span class="rounded-full px-3 py-1 text-xs font-semibold ${toneClasses} border">
          Risk: ${escapeHTML(advisory.riskLevel)} (${advisory.riskScore}/100)
        </span>
      </div>

      <div class="mt-5 grid grid-cols-2 gap-3 md:grid-cols-4">
        <div class="rounded-xl border border-slate-200 bg-slate-50 p-4 text-center">
          <p class="text-xs text-slate-500">Temp</p>
          <p class="mt-1 text-base font-bold text-slate-900">${temp !== null ? `${escapeHTML(String(temp))} C` : "N/A"}</p>
        </div>
        <div class="rounded-xl border border-slate-200 bg-slate-50 p-4 text-center">
          <p class="text-xs text-slate-500">Humidity</p>
          <p class="mt-1 text-base font-bold text-slate-900">${humidity !== null ? `${escapeHTML(String(humidity))}%` : "N/A"}</p>
        </div>
        <div class="rounded-xl border border-slate-200 bg-slate-50 p-4 text-center">
          <p class="text-xs text-slate-500">Condition</p>
          <p class="mt-1 text-base font-bold text-slate-900">${escapeHTML(condition)}</p>
        </div>
        <div class="rounded-xl border border-slate-200 bg-slate-50 p-4 text-center">
          <p class="text-xs text-slate-500">Location</p>
          <p class="mt-1 text-base font-bold text-slate-900">${locationEscaped}</p>
        </div>
      </div>
    </div>

    <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow">
      <h4 class="text-base font-semibold text-slate-900">Why this risk?</h4>
      <ul class="mt-3 space-y-1">${reasonsHtml}</ul>
    </div>

    <div class="rounded-3xl border border-emerald-200 bg-emerald-50 p-6 shadow">
      <h4 class="text-base font-semibold text-emerald-900">Action Plan (Next 24h)</h4>
      <ul class="mt-3 space-y-1">${actionsHtml}</ul>
    </div>
  </div>
  `;
}

async function detectWeatherLocation() {
  if (!navigator.geolocation) {
    alert("Geolocation not supported");
    return;
  }

  navigator.geolocation.getCurrentPosition(
    async (position) => {
      const lat = position.coords.latitude;
      const lon = position.coords.longitude;
      try {
        const res = await fetch(`${API_BASE_URL}/detect-location?lat=${lat}&lon=${lon}`);
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Unable to detect location");

        const city = data?.city || "";
        const locInput = document.getElementById("loc");
        if (city && locInput) locInput.value = city;
        else alert("Unable to detect location");
      } catch (error) {
        console.error("Location detection error:", error);
        alert(error.message || "Location detection failed");
      }
    },
    () => {
      alert("Location permission denied");
    }
  );
}

async function getForecastRisk() {
  const location = document.getElementById("loc").value.trim();
  const days = document.getElementById("forecastDays")?.value || "3";
  const box = document.getElementById("forecastRisk");
  if (!box) return;

  if (!location) {
    alert("Please enter location");
    return;
  }

  const cacheKey = `forecast|${location.toLowerCase()}|${days}`;
  const cached = getAdvisoryCacheEntry(cacheKey);
  if (cached) {
    renderForecastRisk(window.normalizePayload(cached), box);
    return;
  }

  box.innerHTML = `
  <div class="rounded-2xl border border-slate-200 bg-white p-6 text-sm text-slate-600 shadow">
    Loading forecast risk...
  </div>
  `;

  try {
    const res = await fetch(`${API_BASE_URL}/forecast-risk/${encodeURIComponent(location)}?days=${encodeURIComponent(days)}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Unable to fetch forecast risk");
    setAdvisoryCacheEntry(cacheKey, data);
    renderForecastRisk(window.normalizePayload(data), box);
  } catch (error) {
    box.innerHTML = `
    <div class="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">
      ${escapeHTML(error.message || "Unable to fetch forecast risk")}
    </div>
    `;
  }
}

function renderForecastRisk(data, box) {
  const daily = Array.isArray(data.daily_risk) ? data.daily_risk : [];
    const topDays = daily.slice(0, 7);
    const highOrSevere = topDays.filter((d) => /(high|severe|very high)/i.test(String(d.risk_level || ""))).length;
    const decisionTone = highOrSevere > 0 ? "bg-rose-50 border-rose-200 text-rose-900" : "bg-emerald-50 border-emerald-200 text-emerald-900";
    const decisionText = highOrSevere > 0
      ? `High-risk days detected (${highOrSevere}/${topDays.length}). Prioritize preventive spray timing.`
      : "Mostly low-risk trend. Continue routine scouting and sanitation.";

    const forecastCards = topDays.map((d) => `
      <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <div class="flex items-center justify-between gap-2">
          <p class="font-semibold text-slate-900">${escapeHTML(d.date)}</p>
          <span class="rounded-full px-2 py-1 text-xs font-semibold ${riskPillClasses(d.risk_level)}">${escapeHTML(d.risk_level)}</span>
        </div>
        <div class="mt-3 grid grid-cols-3 gap-2 text-sm text-slate-700">
          <p>Temp ${escapeHTML(String(d.temp_avg_c))} C</p>
          <p>Humidity ${escapeHTML(String(d.humidity_avg_pct))}%</p>
          <p>Rain ${escapeHTML(String(d.rain_total_mm))} mm</p>
        </div>
      </div>
    `).join("");

    const recommendationPool = topDays
      .flatMap((d) => d.preventive_recommendations || [])
      .map((r) => String(r || "").trim())
      .filter(Boolean);

    const seen = new Set();
    const recommendations = [];
    for (const line of recommendationPool) {
      const key = line.toLowerCase();
      if (seen.has(key)) continue;
      seen.add(key);
      recommendations.push(line);
    }

    const recommendationHtml = recommendations
      .slice(0, 3)
      .map((r) => `<li class="text-sm text-slate-700">- ${escapeHTML(r)}</li>`)
      .join("");

    const spraySummary = summarizeSprayWindows(data.spray_windows);
    const sprayCardsHtml = spraySummary.cards.map((c) => `
      <div class="rounded-xl border border-emerald-200 bg-emerald-50 p-3">
        <p class="text-sm font-semibold text-emerald-900">${escapeHTML(c.label)}: ${escapeHTML(c.slot)}</p>
        <p class="text-xs text-emerald-800">Wind ${escapeHTML(String(c.wind))} km/h | Rain ${escapeHTML(String(c.rain))} mm/3h</p>
      </div>
    `).join("");

    box.innerHTML = `
    <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow space-y-6">
      <div class="rounded-2xl border p-4 ${decisionTone}">
        <h3 class="text-lg font-semibold">Decision Summary</h3>
        <p class="mt-1 text-sm">${escapeHTML(decisionText)}</p>
      </div>

      <div>
        <h3 class="text-xl font-semibold text-slate-900">3-7 Day Risk</h3>
        <div class="mt-3 grid gap-3 md:grid-cols-2">
          ${forecastCards || '<p class="text-sm text-slate-500">No daily risk data available.</p>'}
        </div>
      </div>

      <div class="rounded-2xl border border-emerald-100 bg-emerald-50 p-4">
        <h4 class="font-semibold text-emerald-900">Spray Timing</h4>
        <p class="mt-1 text-sm text-emerald-900">Best spray time: ${escapeHTML(spraySummary.bestText)}</p>
        <div class="mt-3 grid gap-2 md:grid-cols-2">
          ${sprayCardsHtml || '<p class="text-sm text-slate-600">No suitable spray windows found.</p>'}
        </div>
      </div>

      <div class="rounded-2xl border border-cyan-100 bg-cyan-50 p-4">
        <h4 class="font-semibold text-cyan-900">Top Preventive Actions</h4>
        <ul class="mt-2 space-y-1">
          ${recommendationHtml || '<li class="text-sm text-slate-600">No recommendations available.</li>'}
        </ul>
      </div>
    </div>
    `;
}
