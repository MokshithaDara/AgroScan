async function getWeather(){

const location=document.getElementById("loc").value

if(!location){

alert("Please enter location")

return

}

const weatherDiv=document.getElementById("weather")

weatherDiv.innerHTML=`
<div class="bg-white p-8 rounded-2xl shadow text-center">
Loading weather data...
</div>
`

try{

const res=await fetch(`${API_BASE_URL}/weather/${location}`)

const data=await res.json()

const temp=data.temperature ?? "N/A"
const humidity=data.humidity ?? "N/A"
const condition=data.condition ?? "N/A"

let advisory="Monitor crop conditions regularly."

if(humidity>80){
advisory="High humidity detected. Risk of fungal diseases may increase."
}

if(temp>35){
advisory="High temperature detected. Ensure proper irrigation."
}

weatherDiv.innerHTML=`

<div class="space-y-6">

<div class="bg-white p-6 rounded-2xl shadow">

<div class="flex items-center gap-4">

<div class="text-4xl">
🌦️
</div>

<div>

<h3 class="text-xl font-semibold">
Weather Overview
</h3>

<p class="text-sm text-gray-500">
${location}
</p>

</div>

</div>


<div class="grid grid-cols-3 gap-4 mt-6">

<div class="bg-slate-50 p-4 rounded-xl text-center">

<p class="text-sm text-gray-500">Temperature</p>

<p class="text-xl font-bold">${temp}</p>

</div>


<div class="bg-slate-50 p-4 rounded-xl text-center">

<p class="text-sm text-gray-500">Humidity</p>

<p class="text-xl font-bold">${humidity}</p>

</div>


<div class="bg-slate-50 p-4 rounded-xl text-center">

<p class="text-sm text-gray-500">Condition</p>

<p class="text-xl font-bold">${condition}</p>

</div>

</div>

</div>


<div class="bg-cyan-50 border border-cyan-200 p-6 rounded-xl">

<h4 class="font-semibold text-cyan-800">
Crop Advisory
</h4>

<p class="text-sm mt-2 text-cyan-900">
${advisory}
</p>

</div>

</div>

`

}catch(error){

weatherDiv.innerHTML=`
<div class="bg-red-50 border border-red-200 p-6 rounded-xl text-red-700">
Unable to fetch weather data
</div>
`

}

}


async function detectWeatherLocation(){

if(!navigator.geolocation){

alert("Geolocation not supported")

return

}

navigator.geolocation.getCurrentPosition(

async(position)=>{

const lat=position.coords.latitude
const lon=position.coords.longitude

try{

const res=await fetch(
`https://api.openweathermap.org/geo/1.0/reverse?lat=${lat}&lon=${lon}&limit=1&appid=49954bebd2163025ef42b71310bc8345`
)

const data=await res.json()

const city=data[0]?.name || ""

if(city){

document.getElementById("loc").value=city

}else{

alert("Unable to detect location")

}

}catch{

alert("Location detection failed")

}

},

()=>{

alert("Location permission denied")

}

)

}