// ===============================================
// INITIALIZE SCAN PAGE
// ===============================================

function initScanPage() {

  const imageInput = document.getElementById("imageInput")
  const preview = document.getElementById("preview")

  if (imageInput && preview) {

    imageInput.addEventListener("change", function (e) {

      const file = e.target.files[0]

      if (file) {
        preview.src = URL.createObjectURL(file)
        preview.classList.remove("hidden")
      } else {
        preview.src = ""
        preview.classList.add("hidden")
      }

    })

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

        const res = await fetch(
          `https://api.openweathermap.org/geo/1.0/reverse?lat=${lat}&lon=${lon}&limit=1&appid=49954bebd2163025ef42b71310bc8345`
        )

        const data = await res.json()

        const city = data?.[0]?.name || ""

        if (city) {
          document.getElementById("location").value = city
        } else {
          alert("Unable to detect city")
        }

      } catch {

        alert("Location detection failed")

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
  const result = document.getElementById("result")

  document.getElementById("location").value = ""
  document.getElementById("language").value = "en"

  if (imageInput) imageInput.value = ""

  if (preview) {
    preview.src = ""
    preview.classList.add("hidden")
  }

  if (result) result.innerHTML = ""

}



// ===============================================
// PREDICT DISEASE
// ===============================================

async function predict() {

  const imageInput = document.getElementById("imageInput")
  const scanBtn = document.getElementById("scanBtn")

  const file = imageInput?.files?.[0]
  const location = document.getElementById("location").value.trim()
  const language = document.getElementById("language").value

  let user_id = localStorage.getItem("user_id")

  if (!user_id) {
    user_id = "farmer_" + Math.random().toString(36).substring(2, 10)
    localStorage.setItem("user_id", user_id)
  }

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

  scanBtn.disabled = true

  result.innerHTML = `
  <div class="bg-white p-8 rounded-2xl shadow text-center">
    <div class="animate-spin mx-auto h-10 w-10 border-4 border-emerald-200 border-t-emerald-700 rounded-full"></div>
    <p class="mt-4 text-sm text-gray-600">Analyzing image...</p>
  </div>
  `

  try {

    const res = await fetch(`${API_BASE_URL}/predict`, {
      method: "POST",
      body: formData
    })

    if (!res.ok) {
      throw new Error("API error")
    }

    const data = await res.json()

    displayResult(data)

  } catch (error) {

    result.innerHTML = `
    <div class="bg-red-50 border border-red-200 p-6 rounded-xl text-red-700">
      Prediction failed. Please check backend.
    </div>
    `

  } finally {

    scanBtn.disabled = false

  }

}



// ===============================================
// DISPLAY RESULT
// ===============================================

function displayResult(data) {

  const result = document.getElementById("result")

  const scan = data.scan || {}
  const weather = data.weather || {}
  const media = data.media || {}
  const products = data.products || []
  const alerts = data.alerts || []

  const isHealthy =
    scan.disease === "Healthy Crop" ||
    scan.disease === "Healthy"



  // --------------------------------
  // Treatment Steps
  // --------------------------------

  let treatmentHTML = ""

  if (isHealthy) {

    treatmentHTML = `
      <div class="bg-green-50 border border-green-200 p-6 rounded-xl">

        <h4 class="text-lg font-semibold text-green-700">
        🌱 Healthy Crop Advice
        </h4>

        <ul class="mt-4 space-y-2 text-sm text-green-800">

          <li class="flex gap-2">
          <span>✔</span> Crop appears healthy
          </li>

          <li class="flex gap-2">
          <span>✔</span> Maintain irrigation and fertilization
          </li>

          <li class="flex gap-2">
          <span>✔</span> Continue regular crop monitoring
          </li>

        </ul>

      </div>
    `

  } else {

    const treatmentSteps = (data.treatment || "")
      .split(".")
      .filter(s => s.trim() !== "")
      .map(step => `
        <li class="flex gap-2">
          <span class="text-emerald-600">✔</span>
          <span>${step.trim()}</span>
        </li>
      `).join("")

    treatmentHTML = `
      <div class="bg-gradient-to-r from-emerald-50 to-green-50 p-6 rounded-2xl shadow">

        <h4 class="text-lg font-semibold">🌿 Treatment Steps</h4>

        <ul class="mt-4 space-y-2 text-sm">
          ${treatmentSteps || "No treatment available"}
        </ul>

      </div>
    `

  }



  // --------------------------------
  // Products
  // --------------------------------

  const productsHTML = products.map(p => `
    <a href="${p.link}" target="_blank"
      class="bg-emerald-700 hover:bg-emerald-800 text-white px-4 py-2 rounded-lg text-sm">
      ${p.platform}
    </a>
  `).join("")



  // --------------------------------
  // Alerts
  // --------------------------------

  const alertsHTML = alerts.map(a => `
    <div class="bg-amber-50 border border-amber-200 p-3 rounded-lg text-sm text-amber-800">
      ${a}
    </div>
  `).join("")



  // --------------------------------
  // Result Card
  // --------------------------------

  const label = isHealthy ? "Status" : "Disease"
  const diseaseText = isHealthy ? "Healthy Crop" : (scan.disease ?? "Unknown")



  result.innerHTML = `

  <div class="space-y-8">

    <div class="rounded-[28px] p-6 shadow-xl text-white
      bg-gradient-to-r from-emerald-700 via-green-600 to-teal-600">

      <h3 class="text-2xl font-bold">
        ${isHealthy ? "Crop Health Result" : "Prediction Result"}
      </h3>

      <div class="grid grid-cols-2 gap-4 mt-6">

        <div>
          <p class="text-sm">${label}</p>
          <p class="text-xl font-bold">${diseaseText}</p>
        </div>

        <div>
          <p class="text-sm">Location</p>
          <p class="text-xl font-bold">${scan.location ?? "N/A"}</p>
        </div>

      </div>

    </div>


    ${treatmentHTML}



    <div class="bg-white p-6 rounded-2xl shadow">

      <h4 class="text-lg font-semibold">Weather Snapshot</h4>

      <div class="grid grid-cols-3 gap-4 mt-4">

        <div class="bg-slate-50 p-4 rounded-lg text-center">
          <p class="text-xs text-gray-500">Temperature</p>
          <p class="font-bold">${weather.temperature ?? "N/A"}</p>
        </div>

        <div class="bg-slate-50 p-4 rounded-lg text-center">
          <p class="text-xs text-gray-500">Humidity</p>
          <p class="font-bold">${weather.humidity ?? "N/A"}</p>
        </div>

        <div class="bg-slate-50 p-4 rounded-lg text-center">
          <p class="text-xs text-gray-500">Location</p>
          <p class="font-bold">${scan.location ?? "N/A"}</p>
        </div>

      </div>

    </div>



    ${alerts.length ? `

    <div class="bg-white p-6 rounded-2xl shadow">

      <h4 class="font-semibold">Alerts</h4>

      <div class="mt-4 space-y-2">
        ${alertsHTML}
      </div>

    </div>

    ` : ""}



    ${products.length ? `

    <div class="bg-white p-6 rounded-2xl shadow">

      <h4 class="font-semibold">Recommended Products</h4>

      <div class="mt-4 flex gap-3 flex-wrap">
        ${productsHTML}
      </div>

    </div>

    ` : ""}



    ${media.voice ? `

    <div class="bg-white p-6 rounded-2xl shadow">

      <h4 class="font-semibold">Voice Advice</h4>

      <audio controls class="mt-4 w-full">
        <source src="${API_BASE_URL}/static/${media.voice}" type="audio/mpeg">
      </audio>

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

}