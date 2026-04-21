// ===============================================
// INITIALIZE SCAN PAGE
// ===============================================

let currentObjectURL = null;
let isPredicting = false;

const SCAN_CACHE_KEY = "agroscan_scan_cache_v1";
const SCAN_CACHE_TTL_MS = 5 * 60 * 1000;

function getScanCacheStore() {
  try {
    const raw = localStorage.getItem(SCAN_CACHE_KEY);
    const parsed = raw ? JSON.parse(raw) : {};
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch (_error) {
    return {};
  }
}

function setScanCacheEntry(cacheKey, payload) {
  const store = getScanCacheStore();
  store[cacheKey] = {
    savedAt: Date.now(),
    payload,
  };
  try {
    localStorage.setItem(SCAN_CACHE_KEY, JSON.stringify(store));
  } catch (_error) {
    // Ignore quota errors safely.
  }
}

function getScanCacheEntry(cacheKey) {
  const store = getScanCacheStore();
  const entry = store[cacheKey];
  if (!entry || !entry.savedAt || !entry.payload) return null;
  if (Date.now() - entry.savedAt > SCAN_CACHE_TTL_MS) return null;
  return entry.payload;
}

function buildScanCacheKey(file, location, userId) {
  const fingerprint = `${file?.name || ""}|${file?.size || 0}|${file?.lastModified || 0}`;
  return `${userId}|${String(location || "").toLowerCase()}|${fingerprint}`;
}

function initScanPage() {

  const imageInput = document.getElementById("imageInput")
  const preview = document.getElementById("preview")
  const uploadHint = document.getElementById("uploadHint")
  const uploadDropHint = document.getElementById("uploadDropHint")
  const uploadZone = document.getElementById("uploadZone")
  const result = document.getElementById("result")

  // Hide result area on page load
  if (result) {
    result.classList.add("hidden")
  }

  if (imageInput && preview) {

    imageInput.addEventListener("change", function (e) {

      const file = e.target.files[0]

      if (file) {
        // Validate file type
        if (!file.type.startsWith('image/')) {
          alert("Please upload a valid image file")
          imageInput.value = ""
          return
        }

        // Validate file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
          alert("Image size must be less than 5MB")
          imageInput.value = ""
          return
        }

        // Revoke previous object URL to prevent memory leak
        if (currentObjectURL) {
          URL.revokeObjectURL(currentObjectURL)
        }

        currentObjectURL = URL.createObjectURL(file)
        preview.src = currentObjectURL
        preview.classList.remove("hidden")
        if (uploadHint) uploadHint.classList.add("hidden")
        if (uploadDropHint) uploadDropHint.classList.add("hidden")
      } else {
        preview.src = ""
        preview.classList.add("hidden")
        if (uploadHint) uploadHint.classList.remove("hidden")
        if (uploadDropHint) uploadDropHint.classList.remove("hidden")
      }

    })

  }

  if (uploadZone && imageInput) {
    const enterClass = "border-emerald-500";
    const bgClass = "bg-emerald-100";

    const activateDropState = () => {
      uploadZone.classList.add(enterClass, bgClass, "scale-[1.01]");
    };
    const deactivateDropState = () => {
      uploadZone.classList.remove(enterClass, bgClass, "scale-[1.01]");
    };

    ["dragenter", "dragover"].forEach((eventName) => {
      uploadZone.addEventListener(eventName, (event) => {
        event.preventDefault();
        activateDropState();
      });
    });

    ["dragleave", "drop"].forEach((eventName) => {
      uploadZone.addEventListener(eventName, (event) => {
        event.preventDefault();
        deactivateDropState();
      });
    });

    uploadZone.addEventListener("drop", (event) => {
      const droppedFile = event.dataTransfer?.files?.[0];
      if (!droppedFile) return;
      const dt = new DataTransfer();
      dt.items.add(droppedFile);
      imageInput.files = dt.files;
      imageInput.dispatchEvent(new Event("change", { bubbles: true }));
    });
  }

}



// ===============================================
// AUTO LOCATION DETECTION
// ===============================================

async function detectLocation() {

  if (!navigator.geolocation) {
    alert("Location detection not supported")
    return
  }

  navigator.geolocation.getCurrentPosition(

    async (position) => {

      const lat = position.coords.latitude
      const lon = position.coords.longitude

      try {
        // Use backend endpoint instead of exposing API key
        const res = await fetch(
          `${API_BASE_URL}/detect-location?lat=${lat}&lon=${lon}`
        )

        const data = await res.json()
        if (!res.ok) {
          throw new Error(data.detail || "Unable to detect city")
        }

        const city = data?.city || ""

        if (city) {
          const locationInput = document.getElementById("location")
          if (locationInput) {
            locationInput.value = city
          }
        } else {
          alert("Unable to detect city")
        }

      } catch (error) {

        console.error("Location detection error:", error)
        alert(error.message || "Location detection failed")

      }

    },

    () => {
      alert("Location permission denied")
    }

  )

}



// ===============================================
// RESET FORM
// ===============================================

function resetScanForm() {

  const imageInput = document.getElementById("imageInput")
  const preview = document.getElementById("preview")
  const uploadHint = document.getElementById("uploadHint")
  const uploadDropHint = document.getElementById("uploadDropHint")
  const result = document.getElementById("result")
  const locationInput = document.getElementById("location")
  const voiceLanguageInput = document.getElementById("voiceLanguage")

  if (locationInput) locationInput.value = ""
  if (voiceLanguageInput) voiceLanguageInput.value = "en"

  if (imageInput) imageInput.value = ""

  if (preview) {
    preview.src = ""
    preview.classList.add("hidden")
  }
  if (uploadHint) uploadHint.classList.remove("hidden")
  if (uploadDropHint) uploadDropHint.classList.remove("hidden")

  if (result) {
    result.innerHTML = ""
    result.classList.add("hidden")
  }

  // Revoke object URL on form reset
  if (currentObjectURL) {
    URL.revokeObjectURL(currentObjectURL)
    currentObjectURL = null
  }

}



// ===============================================
// PREDICT DISEASE
// ===============================================

async function predict() {
  if (isPredicting) return;

  const imageInput = document.getElementById("imageInput")
  const scanBtn = document.getElementById("scanBtn")
  const locationInput = document.getElementById("location")
  const voiceLanguageInput = document.getElementById("voiceLanguage")

  if (!imageInput || !scanBtn || !locationInput || !voiceLanguageInput) {
    alert("Form elements not found")
    return
  }

  const file = imageInput?.files?.[0]
  const location = locationInput.value.trim()
  const language = (voiceLanguageInput.value || "en").trim()
  const user_id = getUserId()

  if (!file) {
    alert("Please upload an image.")
    return
  }

  if (!location) {
    alert("Please enter location.")
    return
  }

  const formData = new FormData()

  formData.append("file", file)
  formData.append("location", location)
  formData.append("language", language)
  formData.append("user_id", user_id)

  const result = document.getElementById("result")
  if (!result) {
    alert("Result container not found")
    return
  }

  const originalBtnLabel = scanBtn.innerHTML
  const cacheKey = buildScanCacheKey(file, location, user_id)
  const cachedPayload = getScanCacheEntry(cacheKey)

  if (cachedPayload) {
    displayResult(window.normalizePayload(cachedPayload))
    return
  }

  isPredicting = true
  scanBtn.disabled = true
  scanBtn.innerHTML = `<span class="inline-flex items-center gap-2"><span class="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white/60 border-t-white"></span>Analyzing...</span>`
  result.classList.remove("hidden")
  result.scrollIntoView({ behavior: "smooth", block: "start" })

  result.innerHTML = `
  <div class="bg-white p-8 rounded-2xl shadow">
    <div class="animate-pulse space-y-4">
      <div class="h-5 w-40 rounded bg-slate-200"></div>
      <div class="h-24 rounded-xl bg-slate-100"></div>
      <div class="grid grid-cols-2 gap-3">
        <div class="h-14 rounded-lg bg-slate-100"></div>
        <div class="h-14 rounded-lg bg-slate-100"></div>
      </div>
      <p class="text-sm text-gray-600">Analyzing image...</p>
    </div>
  </div>
  `

  try {

    const res = await fetch(`${API_BASE_URL}/predict`, {
      method: "POST",
      body: formData
    })

    const apiData = await res.json()
    if (!res.ok) {
      throw new Error(apiData.detail || apiData.message || "API error")
    }

    const data = window.normalizePayload(apiData)
    setScanCacheEntry(cacheKey, data)
    displayResult(data)

  } catch (error) {

    const errorMsg = escapeHTML(error.message || "Something went wrong")

    result.innerHTML = `
    <div class="bg-red-50 border border-red-200 p-6 rounded-xl text-red-700">
      ? ${errorMsg} <br/>
      <ul class="mt-2 text-sm">
        <li>• Backend not running</li>
        <li>• API URL issue</li>
        <li>• Network problem</li>
      </ul>
    </div>
    `
    result.classList.remove("hidden")

  } finally {
    isPredicting = false
    scanBtn.disabled = false
    scanBtn.innerHTML = originalBtnLabel

  }

}

function getDiseaseProfile(diseaseName) {
  const profileMap = {
    "Bract Mosaic Virus": {
      overview: "A banana viral disease that causes mosaic streaks and plant weakening.",
      symptoms: "Streaked/mottled leaves, poor growth, and lower bunch quality.",
      spread: "Mainly spread by infected planting material and aphid vectors.",
      favorable: "Warm weather with active aphid movement and infected suckers.",
      impact: "Can reduce bunch quality and cause serious stand loss if unmanaged.",
      risk: "Early roguing and vector control are critical to limit field-wide spread."
    },
    "Moko": {
      overview: "A destructive bacterial wilt disease in banana.",
      symptoms: "Sudden wilting, vascular discoloration, and fruit/flower symptoms.",
      spread: "Spreads through contaminated tools, soil/water movement, and infected suckers.",
      favorable: "Wet field movement, poor sanitation, and repeated cutting operations.",
      impact: "Rapid spread can result in severe yield loss across blocks.",
      risk: "Sanitation and immediate removal of infected plants are essential."
    },
    "Panama": {
      overview: "A soil-borne Fusarium wilt of banana affecting water transport.",
      symptoms: "Leaf yellowing, wilting, vascular browning, and gradual plant collapse.",
      spread: "Persists in soil; spreads with infected material and contaminated soil.",
      favorable: "Poor drainage and long-term contaminated soils.",
      impact: "Can persist for years in soil and reduce plantation lifespan.",
      risk: "Resistant varieties and drainage management are key long-term controls."
    },
    "Yellow and Black Sigatoka": {
      overview: "A major fungal leaf disease in banana reducing photosynthetic area.",
      symptoms: "Streaks/spots that darken, leaf necrosis, and early leaf death.",
      spread: "Fungal spores spread via wind and rain splash, especially in humidity.",
      favorable: "High humidity, long leaf wetness, and dense canopy.",
      impact: "Lower photosynthesis often results in poor fruit filling and yield reduction.",
      risk: "Rapid canopy loss can significantly reduce yield without timely fungicide rotation."
    },
    "Anthracnose": {
      overview: "A fungal disease in chilli causing lesions on fruits and foliage.",
      symptoms: "Dark sunken spots on fruits and necrotic patches on leaves.",
      spread: "Favored by warm, humid weather and rain splash.",
      favorable: "Frequent rain/humidity and infected crop residues.",
      impact: "Severely reduces marketable fruit quality and shelf life.",
      risk: "Can quickly reduce marketable yield if infected fruits are not removed."
    },
    "Leaf Curl": {
      overview: "A vector-associated viral syndrome causing severe leaf deformation.",
      symptoms: "Leaf curling, stunting, and reduced flowering/fruit set.",
      spread: "Primarily spread by whiteflies.",
      favorable: "Warm dry phases with growing whitefly population.",
      impact: "Plants stay stunted, with major drop in fruiting potential.",
      risk: "Vector suppression in early stage strongly affects final yield."
    },
    "Whitefly": {
      overview: "A sap-sucking pest that weakens plants and vectors viruses.",
      symptoms: "Leaf yellowing, curling, sticky honeydew, and sooty mold.",
      spread: "Population builds fast in warm weather and dense canopy.",
      favorable: "Hot dry weather and unchecked weed hosts.",
      impact: "Direct sap loss plus secondary viral transmission risk.",
      risk: "Unchecked populations can trigger secondary viral outbreaks."
    },
    "Rust": {
      overview: "A fungal disease characterized by rust-colored pustules on leaves.",
      symptoms: "Powdery rust pustules, yellowing, and premature leaf drop.",
      spread: "Spores spread through wind and moist conditions.",
      favorable: "Moderate temperatures with recurring leaf moisture.",
      impact: "Progressive defoliation reduces photosynthesis and pod/grain filling.",
      risk: "Timely fungicide and scouting prevent rapid disease escalation."
    },
    "Mosaic Virus": {
      overview: "A viral disease causing mottling and growth suppression.",
      symptoms: "Mosaic leaf color, distortion, and stunted growth.",
      spread: "Spread by vectors and infected plant material.",
      favorable: "High vector load and reuse of infected planting stock.",
      impact: "Causes chronic yield loss because curative treatment is unavailable.",
      risk: "No curative spray; early removal and vector control are essential."
    },
    "Downy Mildew": {
      overview: "A humidity-driven disease producing yellow patches and fungal growth.",
      symptoms: "Upper leaf chlorotic patches with downy growth underside.",
      spread: "Thrives under cool, moist, prolonged leaf-wetness conditions.",
      favorable: "Night humidity, dew, and frequent cloudy/rainy spells.",
      impact: "Fast spread can cause heavy foliage damage in clusters.",
      risk: "Can spread rapidly after rainy/humid spells without preventive action."
    },
    "Early Leaf Spot": {
      overview: "Commonly caused by Cercospora arachidicola in groundnut, producing circular brown lesions on leaves.",
      symptoms: "Brown circular spots with yellow halo, progressive leaf blighting, and premature defoliation.",
      spread: "Fungal spores spread through rain splash, wind, and infected crop residue.",
      favorable: "Warm temperatures with frequent dew or intermittent rainfall.",
      impact: "Leaf loss reduces photosynthetic area and can lower pod filling and yield.",
      risk: "Without early fungicide rotation, disease intensity can rise quickly across the field."
    },
    "Late Leaf Spot": {
      overview: "Groundnut leaf spot mainly associated with Nothopassalora personata, usually appearing at later growth stages.",
      symptoms: "Dark blackish spots on lower leaves followed by yellowing and rapid defoliation.",
      spread: "Spreads via airborne spores and rain splash under humid conditions.",
      favorable: "Prolonged humidity, dense canopy, and repeated wet-dry cycles.",
      impact: "Severe defoliation can reduce pod development and overall productivity.",
      risk: "Needs timely fungicide scheduling and canopy management to prevent outbreak escalation."
    },
    "Nutrition Deficiency": {
      overview: "An abiotic disorder from macro/micronutrient imbalance rather than pathogen infection.",
      symptoms: "Chlorosis, stunted growth, interveinal yellowing, or uneven canopy vigor.",
      spread: "Not contagious; driven by soil fertility gaps, pH imbalance, or poor uptake.",
      favorable: "High leaching, poor root health, and low-organic-matter soils.",
      impact: "Weak plants become more vulnerable to pest/disease pressure and yield loss.",
      risk: "Soil-test guided correction prevents chronic deficiency and hidden yield penalties."
    },
    "Black Rot": {
      overview: "A bacterial disease (commonly Xanthomonas campestris pv. campestris) affecting crucifers like cauliflower.",
      symptoms: "V-shaped yellow lesions from leaf margins, blackened veins, and plant weakening.",
      spread: "Moves via infected seed, splashing water, and contaminated tools.",
      favorable: "Warm wet weather and prolonged leaf wetness periods.",
      impact: "Can cause major stand loss and poor curd quality in severe infections.",
      risk: "Seed sanitation, clean irrigation, and tool hygiene are critical for control."
    },
    "Bacterial Spot": {
      overview: "A bacterial foliar disease causing angular lesions and tissue necrosis.",
      symptoms: "Small water-soaked spots that enlarge, darken, and coalesce on leaves.",
      spread: "Spread by rain splash, handling when wet, and contaminated implements.",
      favorable: "Wet weather and frequent canopy moisture retention.",
      impact: "Leaf damage reduces plant vigor and market quality.",
      risk: "Early bactericide use plus strict sanitation lowers secondary spread."
    },
    "Flea Beetle": {
      overview: "A chewing insect pest creating shot-hole damage in seedlings and young foliage.",
      symptoms: "Tiny round holes, windowing, and reduced early-stage vigor.",
      spread: "Adult beetles migrate from nearby weeds/crops into fields.",
      favorable: "Warm dry spells and unmanaged field borders.",
      impact: "Early canopy loss reduces establishment and yield potential.",
      risk: "Frequent scouting and early insect management prevent economic damage."
    },
    "Cordana": {
      overview: "A banana leaf spot disease often linked to Cordana spp., causing elongated necrotic lesions.",
      symptoms: "Oval to elongated brown lesions with yellow margins on older leaves.",
      spread: "Spores spread through rain splash and infected debris.",
      favorable: "Humid weather and poor field sanitation.",
      impact: "Can reduce functional leaf area and bunch filling efficiency.",
      risk: "Regular leaf pruning and preventive fungicide sprays are important."
    },
    "Pestalotiopsis": {
      overview: "A fungal leaf disease causing necrotic spotting and tissue blight in banana foliage.",
      symptoms: "Irregular necrotic patches, blight progression, and leaf drying.",
      spread: "Spreads through airborne/rain-splashed spores and infected residues.",
      favorable: "High humidity with persistent canopy wetness.",
      impact: "Loss of healthy leaf area can reduce photosynthate supply to fruits.",
      risk: "Early sanitation and protective fungicide cover minimize spread."
    },
    "Sigatoka": {
      overview: "A fungal leaf spot complex in banana affecting photosynthetic efficiency.",
      symptoms: "Linear streaks evolving into dark necrotic spots and leaf burn.",
      spread: "Spore dissemination by wind and moisture events.",
      favorable: "High humidity, dense canopy, and rainfall-driven wetness.",
      impact: "Severe infections reduce bunch weight and fruit quality.",
      risk: "Fungicide rotation and canopy ventilation are key to suppression."
    },
    "Insect Pest": {
      overview: "General insect pressure affecting leaf area, sap flow, and crop vigor.",
      symptoms: "Chewing/sucking damage, curling, spotting, or visible pest colonies.",
      spread: "Population buildup from nearby hosts and unmanaged weed reservoirs.",
      favorable: "Warm weather with weak field hygiene and delayed scouting.",
      impact: "Unmanaged infestations can trigger secondary disease outbreaks and yield loss.",
      risk: "Integrated pest management with scouting, traps, and targeted sprays is essential."
    },
    "Yellowish": {
      overview: "A chlorosis-like condition often linked to nutrient stress or root-zone imbalance.",
      symptoms: "General yellowing, weak growth, and reduced canopy density.",
      spread: "Not infectious; usually nutritional or physiological.",
      favorable: "Poor soil fertility, compaction, waterlogging, or pH mismatch.",
      impact: "Reduces biomass accumulation and final crop productivity.",
      risk: "Soil correction and balanced feeding are needed to restore vigor."
    },
  };

  let key = String(diseaseName || "");
  if (key.includes("-")) {
    key = key.split("-").slice(1).join("-").trim();
  }

  const fullLabel = String(diseaseName || "").trim();
  const cropName = fullLabel.includes("-") ? fullLabel.split("-")[0].trim() : "Crop";
  const diseaseLabel = key || "detected condition";

  return profileMap[key] || {
    overview: `${cropName} shows signs consistent with ${diseaseLabel}, which can affect crop vigor and productivity if unmanaged.`,
    symptoms: `Track progression of ${diseaseLabel} symptoms on leaves, stems, and productive parts.`,
    spread: "Progression is influenced by weather, field sanitation, and pest/vector pressure.",
    favorable: "Usually worsens under prolonged moisture, stressed canopy, or delayed intervention.",
    impact: `If unmanaged, ${diseaseLabel} can reduce yield quality and field performance.`,
    risk: "Early, crop-specific management and close scouting reduce escalation risk."
  };
}

function getWeatherRiskInsight(tempValue, humidityValue, conditionValue, diseaseName) {
  const temp = Number.isFinite(tempValue) ? tempValue : null;
  const humidity = Number.isFinite(humidityValue) ? humidityValue : null;
  const condition = String(conditionValue || "").toLowerCase();
  const disease = String(diseaseName || "").toLowerCase();
  const isFungalLike = /(mildew|anthracnose|sigatoka|rust|spot|rot|fung)/.test(disease);
  const isViralVectorLike = /(leaf curl|mosaic|virus|whitefly|aphid|vector)/.test(disease);
  const hasRainSignal = /(rain|drizzle|storm|thunder|shower)/.test(condition);
  const hasCloudSignal = /(cloud|mist|fog|overcast)/.test(condition);

  let score = 0;
  if (humidity !== null) {
    if (humidity >= 85) score += 3;
    else if (humidity >= 75) score += 2;
    else if (humidity >= 65) score += 1;
  }
  if (temp !== null) {
    if (temp >= 35) score += 2;
    else if (temp >= 31) score += 1;
    else if (temp < 18) score += 1;
  }
  if (hasRainSignal) score += 2;
  else if (hasCloudSignal) score += 1;

  if (isFungalLike && humidity !== null && humidity >= 70) score += 2;
  if (isViralVectorLike && temp !== null && temp >= 28) score += 1;

  let level = "Low";
  if (score >= 7) level = "High";
  else if (score >= 4) level = "Moderate";

  const notes = [];
  if (temp !== null && humidity !== null) {
    notes.push(`Current conditions: ${temp.toFixed(1)} °C temperature and ${humidity.toFixed(0)}% humidity.`);
  } else if (temp !== null) {
    notes.push(`Current conditions: ${temp.toFixed(1)} °C temperature (humidity unavailable).`);
  } else if (humidity !== null) {
    notes.push(`Current conditions: ${humidity.toFixed(0)}% humidity (temperature unavailable).`);
  }

  if (hasRainSignal) {
    notes.push("These rainy conditions can rapidly increase leaf wetness and disease spread.");
  } else if (hasCloudSignal && humidity !== null && humidity >= 60) {
    notes.push("These moderately humid, cloudy conditions may increase leaf wetness duration.");
  } else if (hasCloudSignal) {
    notes.push("Cloudy weather can retain surface moisture longer than clear conditions.");
  } else if (humidity !== null && humidity >= 65) {
    notes.push("These moderately humid but currently manageable conditions still require regular field checks.");
  } else {
    notes.push("Current weather is comparatively dry and manageable for routine crop operations.");
  }

  if (isFungalLike) {
    if (humidity !== null && humidity < 75) {
      notes.push("Since humidity is below 75%, immediate fungal risk is currently LOW.");
    } else if (humidity !== null && humidity < 85) {
      notes.push("Humidity is 75-84%; fungal pressure is MODERATE and can rise quickly after rain.");
    } else {
      notes.push("Humidity is very high (>=85%); fungal risk is HIGH under prolonged leaf wetness.");
    }
  } else {
    notes.push(`Overall weather risk is currently ${level.toUpperCase()} for disease progression.`);
  }

  if (level === "High") {
    notes.push("Action: Inspect crop immediately and begin preventive protection without delay.");
    notes.push("Avoid spraying just before rainfall; choose the nearest dry weather window.");
  } else if (level === "Moderate") {
    notes.push("Action: Increase field inspection to once daily and prepare preventive spray materials.");
    notes.push("Use canopy management and avoid late-evening irrigation to reduce moisture retention.");
  } else {
    notes.push("Action: Continue routine crop inspection every 48 hours.");
    notes.push("This is a good time for preventive practices like pruning, sanitation, and weed removal.");
  }

  notes.push("If humidity rises above 75% or rainfall begins, initiate preventive fungicide application early.");

  if (isFungalLike) {
    notes.push("Note: The detected disease is fungal-related and tends to spread faster under high moisture and humidity.");
  }
  if (isViralVectorLike) {
    notes.push("Note: The detected disease is vector/viral-related; monitor whitefly/aphid activity and trap counts closely.");
  }

  return { level, score, notes };
}

function extractProductNameFromLink(link) {
  if (!link) return "";
  try {
    const url = new URL(link);
    const params = new URLSearchParams(url.search);
    const query = params.get("k") || params.get("q") || "";
    if (!query) return "";
    return query.replace(/\+/g, " ").replace(/\bagriculture store\b/gi, "").trim();
  } catch (_error) {
    return "";
  }
}

function getProductReason(productName, diseaseName) {
  const product = String(productName || "").toLowerCase();
  const disease = String(diseaseName || "").toLowerCase();
  const exactReasons = {
    "balanced npk fertilizer": "Why this product: restores primary N-P-K balance to recover growth and leaf color.",
    "micronutrient mixture": "Why this product: corrects trace-element deficiency symptoms like chlorosis and weak new growth.",
    "seaweed growth booster": "Why this product: acts as a biostimulant to improve stress tolerance and root activity.",
    "mancozeb fungicide": "Why this product: broad-spectrum protectant that helps limit new fungal infection on foliage.",
    "copper fungicide": "Why this product: contact fungicidal action helps suppress surface-level pathogen spread.",
    "propiconazole fungicide": "Why this product: systemic triazole action helps slow internal fungal progression.",
    "metalaxyl fungicide": "Why this product: targeted activity is useful in downy-mildew-type disease pressure.",
    "neem oil spray": "Why this product: lowers soft-bodied pest pressure and supports vector management.",
    "yellow sticky trap": "Why this product: traps flying vectors for early monitoring and population reduction.",
    "imidacloprid insecticide": "Why this product: systemic control option for sucking pests when vector load is high.",
  };
  if (exactReasons[product]) {
    return exactReasons[product];
  }

  if (/mancozeb|propiconazole|tebuconazole|metalaxyl|chlorothalonil|copper|fungicide/.test(product)) {
    if (/mildew|anthracnose|sigatoka|rust|spot|rot|fung/.test(disease)) {
      return "Why this product: selected to reduce active fungal pressure for the detected disease profile.";
    }
    return "Why this product: supports preventive and early-stage fungal disease suppression.";
  }
  if (/neem|imidacloprid|trap|insecticide|whitefly|aphid/.test(product)) {
    if (/leaf curl|mosaic|virus|whitefly|aphid|vector/.test(disease)) {
      return "Why this product: selected to control vectors that can worsen viral disease spread.";
    }
    return "Why this product: helps reduce vector/insect pressure that drives disease spread.";
  }
  if (/npk|micronutrient|seaweed|growth booster|tonic|conditioner/.test(product)) {
    if (/nutrition deficiency|yellowish/.test(disease)) {
      return "Why this product: selected to correct nutritional imbalance and restore canopy vigor.";
    }
    return "Why this product: helps improve crop vigor and recovery under stress symptoms.";
  }
  if (/disinfectant|bactericide|oxychloride/.test(product) || /bacterial|rot/.test(disease)) {
    return "Why this product: supports sanitation and bacterial disease-pressure reduction.";
  }
  return "Why this product: selected as a practical support input for the detected condition.";
}

function getFieldApplicationGuide(diseaseName) {
  const key = String(diseaseName || "").toLowerCase();
  const guideMap = [
    {
      match: /(anthracnose|sigatoka|rust|spot|mildew|rot|cordana|pestalotiopsis)/,
      dosage: "Protectant fungicide: typically 2.0-2.5 g per liter water (follow label of selected product).",
      frequency: "Spray every 7-10 days during active infection window; tighten interval after rain.",
      method: "Spray both leaf surfaces in early morning/evening for better retention."
    },
    {
      match: /(leaf curl|mosaic|virus|whitefly|aphid|flea beetle|insect)/,
      dosage: "Vector control spray: use label-recommended dose for insecticide or neem formulation.",
      frequency: "Repeat at 5-7 day interval if vector pressure stays high.",
      method: "Combine with yellow sticky traps and remove heavily infected plants."
    },
    {
      match: /(nutrition deficiency|yellowish)/,
      dosage: "Balanced foliar nutrient mix: commonly 2-3 g per liter (as per product label).",
      frequency: "Reapply in 10-14 days based on crop response and soil test.",
      method: "Prefer split application and maintain uniform soil moisture."
    },
  ];

  const match = guideMap.find((item) => item.match.test(key));
  return match || {
    dosage: "Use crop-specific registered input at label dosage.",
    frequency: "Recheck symptoms after 3-5 days and repeat only if needed.",
    method: "Prioritize sanitation, scouting, and local agronomy recommendations."
  };
}

function getRegionalTip(locationName, diseaseName) {
  const location = String(locationName || "").toLowerCase();
  const disease = String(diseaseName || "").toLowerCase();
  const coastalAp = /(guntur|ongole|nellore|vijayawada|tirupati|bhimavaram|machilipatnam)/.test(location);
  const telangana = /(hyderabad|warangal|nizamabad|karimnagar|khammam)/.test(location);

  if (coastalAp && /(mildew|anthracnose|sigatoka|rust|spot|rot)/.test(disease)) {
    return "Coastal humidity zones: keep canopy open and avoid late-evening irrigation to reduce overnight leaf wetness.";
  }
  if (telangana && /(whitefly|leaf curl|mosaic|virus|aphid)/.test(disease)) {
    return "Warmer inland conditions: monitor vector surge twice weekly and maintain trap-based scouting.";
  }
  if (coastalAp || telangana) {
    return "Regional note: align spray timing around local humidity/rain swings and maintain strict field sanitation.";
  }
  return "Regional note: adapt schedule to local extension advisories and recent weather trend.";
}

function playBrowserVoiceAdvice(text) {
  if (!text) return;
  if (!("speechSynthesis" in window)) {
    alert("Voice playback is not supported in this browser.");
    return;
  }
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-IN";
  utterance.rate = 1;
  utterance.pitch = 1;
  window.speechSynthesis.speak(utterance);
}

function setupResultAccordion(root) {
  if (!root) return;

  const items = Array.from(root.querySelectorAll(".ag-acc-item"));
  const triggers = Array.from(root.querySelectorAll(".ag-acc-trigger"));
  const expandAllBtn = root.querySelector("#accExpandAll");
  const collapseAllBtn = root.querySelector("#accCollapseAll");

  const setOpenState = (item, open) => {
    const content = item.querySelector(".ag-acc-content");
    const chevron = item.querySelector(".ag-acc-chevron");
    if (!content) return;

    if (open) {
      item.classList.add("border-emerald-300", "bg-emerald-50/70", "shadow-md");
      item.classList.remove("border-slate-200", "bg-white");
      content.style.maxHeight = `${content.scrollHeight}px`;
      content.style.opacity = "1";
      if (chevron) chevron.classList.add("rotate-180");
      item.dataset.open = "true";
    } else {
      item.classList.remove("border-emerald-300", "bg-emerald-50/70", "shadow-md");
      item.classList.add("border-slate-200", "bg-white");
      content.style.maxHeight = "0px";
      content.style.opacity = "0";
      if (chevron) chevron.classList.remove("rotate-180");
      item.dataset.open = "false";
    }
  };

  const closeAll = () => {
    items.forEach((item) => setOpenState(item, false));
  };

  triggers.forEach((trigger) => {
    trigger.addEventListener("click", () => {
      const item = trigger.closest(".ag-acc-item");
      const isOpen = item?.dataset.open === "true";
      closeAll();
      if (item && !isOpen) setOpenState(item, true);
    });
  });

  if (expandAllBtn) {
    expandAllBtn.addEventListener("click", () => {
      items.forEach((item) => setOpenState(item, true));
    });
  }

  if (collapseAllBtn) {
    collapseAllBtn.addEventListener("click", () => {
      closeAll();
    });
  }

  closeAll();
}



// ===============================================
// ===============================================
// DISPLAY RESULT
// ===============================================

function displayResult(data) {
  const safeData = window.normalizePayload(data || {});

  const result = document.getElementById("result")

  const scan = safeData.scan || {}
  const weather = safeData.weather || {}
  const media = safeData.media || {}
  const products = safeData.products || []

  const isHealthy =
    scan.disease === "Healthy Crop" ||
    scan.disease === "Healthy"



  // --------------------------------
  // Treatment Steps
  // --------------------------------

  let treatmentSectionHTML = ""

  if (isHealthy) {

    treatmentSectionHTML = `
      <ul class="space-y-2 text-sm text-slate-700">
        <li class="flex gap-2"><span class="text-emerald-600">-</span><span>Crop appears healthy.</span></li>
        <li class="flex gap-2"><span class="text-emerald-600">-</span><span>Maintain irrigation and balanced nutrition plan.</span></li>
        <li class="flex gap-2"><span class="text-emerald-600">-</span><span>Continue routine scouting for early symptom detection.</span></li>
      </ul>
    `

  } else {

    const treatmentSource = Array.isArray(safeData.treatment_steps) && safeData.treatment_steps.length
      ? safeData.treatment_steps.join(". ")
      : (safeData.treatment || "");
    const treatmentList = (treatmentSource || "")
      .split(".")
      .filter(s => s.trim() !== "")
      .map(step => step.trim());
    const weatherCautionList = Array.isArray(safeData.weather_cautions)
      ? safeData.weather_cautions.filter(Boolean)
      : [];
    const allTreatmentSteps = treatmentList
      .map(step => `
        <li class="flex gap-2">
          <span class="text-emerald-600">-</span>
          <span>${escapeHTML(step)}</span>
        </li>
      `).join("");
    const cautionHtml = weatherCautionList.map((item) => `
      <li class="flex gap-2">
        <span class="text-amber-600">-</span>
        <span>${escapeHTML(item)}</span>
      </li>
    `).join("");

    treatmentSectionHTML = `
      <ul class="space-y-2 text-sm text-slate-700">
        ${allTreatmentSteps || '<li class="flex gap-2"><span class="text-emerald-600">-</span><span>No treatment available.</span></li>'}
        ${cautionHtml}
      </ul>
    `

  }



  // --------------------------------
  // Disease Info
  // --------------------------------

  const diseaseProfile = getDiseaseProfile(scan.disease ?? "");
  const diseaseSectionHTML = !isHealthy
    ? `
      <ul class="space-y-2 text-sm text-slate-700">
        <li class="flex gap-2"><span class="text-emerald-600">-</span><span><span class="font-semibold">Overview:</span> ${escapeHTML(diseaseProfile.overview)}</span></li>
        <li class="flex gap-2"><span class="text-emerald-600">-</span><span><span class="font-semibold">Symptoms:</span> ${escapeHTML(diseaseProfile.symptoms)}</span></li>
        <li class="flex gap-2"><span class="text-emerald-600">-</span><span><span class="font-semibold">Spread:</span> ${escapeHTML(diseaseProfile.spread)}</span></li>
        <li class="flex gap-2"><span class="text-emerald-600">-</span><span><span class="font-semibold">Favorable Conditions:</span> ${escapeHTML(diseaseProfile.favorable)}</span></li>
        <li class="flex gap-2"><span class="text-emerald-600">-</span><span><span class="font-semibold">Impact:</span> ${escapeHTML(diseaseProfile.impact)}</span></li>
      </ul>
    `
    : `<ul class="space-y-2 text-sm text-slate-700"><li class="flex gap-2"><span class="text-emerald-600">-</span><span>No disease profile needed for healthy crop status.</span></li></ul>`;


  // --------------------------------
  // Products (show products first, links next)
  // --------------------------------

  const groupedProducts = new Map();
  products.forEach((item) => {
    const name = String(item.product || extractProductNameFromLink(item.link) || "Recommended Crop Input").trim();
    if (!groupedProducts.has(name)) {
      groupedProducts.set(name, { links: [], meta: null });
    }
    const group = groupedProducts.get(name);
    group.links.push({
      platform: String(item.platform || "Store"),
      link: String(item.link || ""),
    });
    if (!group.meta) {
      group.meta = {
        reason: String(item.reason || "").trim(),
        whenToUse: String(item.when_to_use || "").trim(),
        whenNotToUse: String(item.when_not_to_use || "").trim(),
        doseGuidance: String(item.dose_guidance || "").trim(),
        weatherNote: String(item.weather_note || "").trim(),
      };
    }
  });

  const recommendedProducts = [...groupedProducts.keys()];
  const productNamesHTML = recommendedProducts.map(name => `
    <div class="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-900">
      ${escapeHTML(name)}
    </div>
  `).join("");

  const productLinksHTML = [...groupedProducts.entries()].map(([productName, productData]) => {
    const linksHTML = productData.links.map((p) => {
      const platform = p.platform || "Store";
      const platformText =
        platform === "Amazon" ? "Buy on Amazon" :
        platform === "Flipkart" ? "Buy on Flipkart" :
        "Open Agri Store Search";
      const link = escapeHTML(p.link || "");
      return `
        <a href="${link}" target="_blank" rel="noopener noreferrer"
          class="inline-flex bg-emerald-700 hover:bg-emerald-800 text-white px-3 py-2 rounded-lg text-sm">
          ${platformText}
        </a>
      `;
    }).join("");

    const reasonText = productData.meta?.reason || getProductReason(productName, scan.disease);
    const whenToUseText = productData.meta?.whenToUse || "Use when symptoms and field scouting support this selection.";
    const whenNotToUseText = productData.meta?.whenNotToUse || "Do not apply blindly without symptom and label confirmation.";
    const doseText = productData.meta?.doseGuidance || "Follow product label for crop and stage-specific dose.";
    const weatherNoteText = productData.meta?.weatherNote || "";

    return `
      <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
        <p class="text-sm font-semibold text-slate-900">${escapeHTML(productName)}</p>
        <ul class="mt-2 space-y-1 text-xs text-slate-700">
          <li><span class="font-semibold">Why:</span> ${escapeHTML(reasonText)}</li>
          <li><span class="font-semibold">When to use:</span> ${escapeHTML(whenToUseText)}</li>
          <li><span class="font-semibold">When not to use:</span> ${escapeHTML(whenNotToUseText)}</li>
          <li><span class="font-semibold">Dose guidance:</span> ${escapeHTML(doseText)}</li>
          ${weatherNoteText ? `<li><span class="font-semibold">Weather note:</span> ${escapeHTML(weatherNoteText)}</li>` : ""}
        </ul>
        <div class="mt-3 flex flex-wrap gap-2">
          ${linksHTML}
        </div>
      </div>
    `;
  }).join("")

  // --------------------------------
  // Result Card (with XSS protection)
  // --------------------------------

  const label = isHealthy ? "Status" : "Disease"
  const diseaseText = isHealthy
    ? "Healthy Crop"
    : escapeHTML(scan.disease ?? "Unknown")
  const location = escapeHTML(scan.location ?? "N/A")
  const tempValue = weather.temperature != null ? Number(weather.temperature) : null
  const humidityValue = weather.humidity != null ? Number(weather.humidity) : null
  const weatherRisk = getWeatherRiskInsight(tempValue, humidityValue, weather.condition, scan.disease)
  const weatherLevelClass = weatherRisk.level === "High"
    ? "bg-red-100 text-red-700 border-red-200"
    : weatherRisk.level === "Moderate"
      ? "bg-amber-100 text-amber-700 border-amber-200"
      : "bg-emerald-100 text-emerald-700 border-emerald-200";
  const weatherNotesHTML = weatherRisk.notes
    .map((n) => `<li>- ${escapeHTML(n)}</li>`)
    .join("")
  const adviceText = isHealthy
    ? "Good news. The crop appears healthy. Continue irrigation, nutrition management, and regular scouting."
    : `Detected condition: ${scan.disease || "crop disease"}. Recommended treatment: ${safeData.treatment || "follow local agronomy guidance and start preventive management."}`
  const fieldGuide = getFieldApplicationGuide(scan.disease)
  const regionalTip = getRegionalTip(scan.location, scan.disease)
  const fieldGuideSectionHTML = !isHealthy
    ? `
      <ul class="space-y-2 text-sm text-slate-700">
        <li class="flex gap-2"><span class="text-emerald-600">-</span><span><span class="font-semibold">Dosage:</span> ${escapeHTML(fieldGuide.dosage)}</span></li>
        <li class="flex gap-2"><span class="text-emerald-600">-</span><span><span class="font-semibold">Frequency:</span> ${escapeHTML(fieldGuide.frequency)}</span></li>
        <li class="flex gap-2"><span class="text-emerald-600">-</span><span><span class="font-semibold">Method:</span> ${escapeHTML(fieldGuide.method)}</span></li>
        <li class="flex gap-2"><span class="text-emerald-600">-</span><span><span class="font-semibold">Local Insight:</span> ${escapeHTML(regionalTip)}</span></li>
        <li class="flex gap-2"><span class="text-emerald-600">-</span><span>Verify label dosage, PHI/REI, and local agronomy guidance before application.</span></li>
      </ul>
    `
    : `<ul class="space-y-2 text-sm text-slate-700"><li class="flex gap-2"><span class="text-emerald-600">-</span><span>Field application guide is not required for healthy crop status.</span></li></ul>`;
  const treatmentCardTitle = isHealthy ? "Healthy Crop Care" : "Treatment Plan";

  const aboutDiseaseCardHTML = !isHealthy ? `
    <div class="ag-acc-item rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-emerald-300 hover:bg-emerald-50/40 hover:shadow-md">
      <button type="button" class="ag-acc-trigger flex w-full cursor-pointer items-center justify-between text-left">
        <span class="flex items-center gap-3"><span class="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-100">🌿</span><span class="font-semibold text-slate-900">About Disease</span></span>
      </button>
      <div class="ag-acc-content overflow-hidden transition-all duration-300"><div class="pt-3">${diseaseSectionHTML}</div></div>
    </div>
  ` : "";

  const treatmentCardHTML = `
    <div class="ag-acc-item rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-emerald-300 hover:bg-emerald-50/40 hover:shadow-md">
      <button type="button" class="ag-acc-trigger flex w-full cursor-pointer items-center justify-between text-left">
        <span class="flex items-center gap-3"><span class="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-100">💊</span><span class="font-semibold text-slate-900">${treatmentCardTitle}</span></span>
      </button>
      <div class="ag-acc-content overflow-hidden transition-all duration-300"><div class="pt-3">${treatmentSectionHTML}</div></div>
    </div>
  `;

  const weatherCardHTML = `
    <div class="ag-acc-item rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-emerald-300 hover:bg-emerald-50/40 hover:shadow-md">
      <button type="button" class="ag-acc-trigger flex w-full cursor-pointer items-center justify-between text-left">
        <span class="flex items-center gap-3"><span class="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-100">🌦️</span><span class="font-semibold text-slate-900">Weather Insights</span></span>
      </button>
      <div class="ag-acc-content overflow-hidden transition-all duration-300">
        <div class="pt-3 space-y-3">
          <div class="inline-flex items-center gap-2 rounded-full border px-3 py-1 text-sm font-semibold ${weatherLevelClass}"><span>Current Risk:</span><span>${escapeHTML(weatherRisk.level)}</span></div>
          <div class="grid grid-cols-2 gap-3 md:grid-cols-4">
            <div class="rounded-xl border border-slate-200 bg-slate-50 p-3 text-center">
              <p class="text-xs text-slate-500">🌡️ Temperature</p>
              <p class="text-sm font-semibold text-slate-900">${Number.isFinite(tempValue) ? `${escapeHTML(String(tempValue))} °C` : "N/A"}</p>
            </div>
            <div class="rounded-xl border border-slate-200 bg-slate-50 p-3 text-center">
              <p class="text-xs text-slate-500">💧 Humidity</p>
              <p class="text-sm font-semibold text-slate-900">${Number.isFinite(humidityValue) ? `${escapeHTML(String(humidityValue))}%` : "N/A"}</p>
            </div>
            <div class="rounded-xl border border-slate-200 bg-slate-50 p-3 text-center">
              <p class="text-xs text-slate-500">📍 Location</p>
              <p class="text-sm font-semibold text-slate-900">${location}</p>
            </div>
            <div class="rounded-xl border border-slate-200 bg-slate-50 p-3 text-center">
              <p class="text-xs text-slate-500">☁️ Condition</p>
              <p class="text-sm font-semibold text-slate-900">${escapeHTML(weather.condition ?? "N/A")}</p>
            </div>
          </div>
          <div class="rounded-xl border border-cyan-100 bg-cyan-50 p-3">
            <p class="text-sm font-semibold text-cyan-900">How to use this weather data</p>
            <ul class="mt-2 space-y-1 text-sm text-cyan-900">${weatherNotesHTML}</ul>
          </div>
        </div>
      </div>
    </div>
  `;

  const fieldGuideCardHTML = !isHealthy ? `
    <div class="ag-acc-item rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-emerald-300 hover:bg-emerald-50/40 hover:shadow-md">
      <button type="button" class="ag-acc-trigger flex w-full cursor-pointer items-center justify-between text-left">
        <span class="flex items-center gap-3"><span class="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-100">🧭</span><span class="font-semibold text-slate-900">Field Application Guide</span></span>
      </button>
      <div class="ag-acc-content overflow-hidden transition-all duration-300"><div class="pt-3">${fieldGuideSectionHTML}</div></div>
    </div>
  ` : "";

  const productsCardHTML = !isHealthy && products.length ? `
    <div class="ag-acc-item rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-emerald-300 hover:bg-emerald-50/40 hover:shadow-md">
      <button type="button" class="ag-acc-trigger flex w-full cursor-pointer items-center justify-between text-left">
        <span class="flex items-center gap-3"><span class="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-100">🛒</span><span class="font-semibold text-slate-900">Recommended Products</span></span>
      </button>
      <div class="ag-acc-content overflow-hidden transition-all duration-300">
        <div class="pt-3">
          <div class="grid gap-2">${productNamesHTML}</div>
          <div class="mt-3 grid gap-2 md:grid-cols-2">${productLinksHTML}</div>
        </div>
      </div>
    </div>
  ` : "";

  const accordionCardsHTML = [
    aboutDiseaseCardHTML,
    treatmentCardHTML,
    weatherCardHTML,
    fieldGuideCardHTML,
    productsCardHTML
  ].filter(Boolean).join("");

  // Show result area
  result.classList.remove("hidden")

  result.innerHTML = `

  <div class="space-y-8">

    <div class="rounded-[28px] border border-emerald-300 p-6 shadow-2xl text-white
      bg-gradient-to-r from-emerald-800 via-green-700 to-teal-700">

      <div class="flex items-center gap-3">
        <span class="inline-flex h-10 w-10 items-center justify-center rounded-full bg-white/20 text-xl">🌿</span>
        <h3 class="text-2xl font-bold">
          ${isHealthy ? "Crop Health Result" : "Prediction Result"}
        </h3>
      </div>

      <div class="grid grid-cols-2 gap-4 mt-6">

        <div>
          <p class="text-sm">${label}</p>
          <p class="text-xl font-bold">${diseaseText}</p>
        </div>

        <div>
          <p class="text-sm">Location</p>
          <p class="text-xl font-bold">${location}</p>
        </div>

      </div>

    </div>

    <div id="resultAccordion" class="space-y-4">
      <div class="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow">
        <h4 class="text-base font-semibold text-slate-900">Insights</h4>
        <div class="flex gap-2">
          <button id="accExpandAll" class="rounded-lg border border-emerald-300 bg-emerald-50 px-3 py-2 text-xs font-semibold text-emerald-700 hover:bg-emerald-100">Expand All</button>
          <button id="accCollapseAll" class="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50">Collapse All</button>
        </div>
      </div>

      <div class="grid gap-4">
        ${accordionCardsHTML}
      </div>
    </div>

    ${(media.voice || adviceText) ? `
    <div class="rounded-2xl border border-emerald-200 bg-gradient-to-r from-emerald-600 to-teal-600 p-5 shadow-lg text-white">
      <div class="flex items-center justify-between gap-3">
        <h4 class="text-lg font-semibold">Voice Advice</h4>
        <span class="rounded-full bg-white/20 px-3 py-1 text-xs font-semibold">Audio Assist</span>
      </div>
      <p class="mt-2 text-sm text-white/90">Tap to listen to spoken guidance for this scan result.</p>
      ${media.voice ? `
      <div class="mt-3 rounded-xl bg-white p-3">
        <audio controls class="w-full">
          ${(() => {
            const voicePath = (media.voice?.startsWith("http") || media.voice?.startsWith("data:"))
              ? media.voice
              : `${API_BASE_URL}/static/${media.voice}`;
            return `<source src="${voicePath}" type="audio/mpeg">`;
          })()}
        </audio>
      </div>
      ` : `
      <button id="browserVoiceBtn" class="mt-4 inline-flex w-full items-center justify-center rounded-xl bg-white px-4 py-3 text-base font-semibold text-emerald-700 shadow hover:bg-emerald-50">▶ Play Voice Advice</button>
      `}
    </div>
    ` : ""}



    ${media.heatmap ? `

    <div class="bg-white p-6 rounded-2xl shadow">

      <h4 class="font-semibold">Disease Heatmap</h4>

      <img src="${API_BASE_URL}/static/${media.heatmap}"
      class="mt-4 rounded-xl w-full">

    </div>

    ` : ""}

  </div>

  `

  setupResultAccordion(document.getElementById("resultAccordion"))

  const browserVoiceBtn = document.getElementById("browserVoiceBtn")
  if (browserVoiceBtn) {
    browserVoiceBtn.addEventListener("click", () => playBrowserVoiceAdvice(adviceText))
  }

}




