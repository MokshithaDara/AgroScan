const diseases = [

{crop:"Banana",name:"Bract Mosaic Virus Disease",
desc:"Viral disease causing mosaic patterns on banana leaves.",
treatment:"Remove infected plants and control aphids."},

{crop:"Banana",name:"Moko",
desc:"Bacterial wilt disease causing plant wilting.",
treatment:"Remove infected plants and disinfect tools."},

{crop:"Banana",name:"Panama",
desc:"Fusarium wilt disease causing yellowing leaves.",
treatment:"Use resistant varieties."},

{crop:"Banana",name:"Yellow and Black Sigatoka",
desc:"Severe fungal disease damaging banana leaves.",
treatment:"Apply systemic fungicides."},

{crop:"Banana",name:"Cordana",
desc:"Leaf disease producing brown lesions.",
treatment:"Remove infected leaves."},

{crop:"Banana",name:"Pestalotiopsis",
desc:"Fungal infection producing leaf spots.",
treatment:"Use carbendazim spray."},

{crop:"Banana",name:"Sigatoka",
desc:"Leaf streak disease affecting banana plants.",
treatment:"Apply fungicides."},

{crop:"Banana",name:"Insect Pest",
desc:"General insect pest attack on banana plants.",
treatment:"Use neem oil spray."},


{crop:"Chilli",name:"Anthracnose",
desc:"Fungal disease causing lesions on fruits.",
treatment:"Apply copper fungicide."},

{crop:"Chilli",name:"Leaf Curl",
desc:"Virus causing leaf curling.",
treatment:"Control whiteflies."},

{crop:"Chilli",name:"Whitefly",
desc:"Sap sucking pest spreading viral diseases.",
treatment:"Use neem oil spray."},

{crop:"Chilli",name:"Yellowish",
desc:"Leaves turning yellow due to nutrient deficiency.",
treatment:"Apply balanced fertilizer."},


{crop:"Groundnut",name:"Nutrition Deficiency",
desc:"Poor growth due to nutrient deficiency.",
treatment:"Apply NPK fertilizer."},

{crop:"Groundnut",name:"Early Leaf Spot",
desc:"Brown spots appearing early.",
treatment:"Apply mancozeb."},

{crop:"Groundnut",name:"Late Leaf Spot",
desc:"Severe fungal infection.",
treatment:"Use chlorothalonil."},

{crop:"Groundnut",name:"Rust",
desc:"Orange fungal pustules.",
treatment:"Use rust fungicide."},


{crop:"Radish",name:"Downy Mildew",
desc:"Yellow patches and fungal growth.",
treatment:"Apply metalaxyl."},

{crop:"Radish",name:"Flea Beetle",
desc:"Beetles causing holes in leaves.",
treatment:"Use neem spray."},

{crop:"Radish",name:"Mosaic Virus",
desc:"Virus causing mosaic patterns.",
treatment:"Remove infected plants."},


{crop:"Cauliflower",name:"Downy Mildew",
desc:"Leaf disease producing yellow spots.",
treatment:"Apply fungicide."},

{crop:"Cauliflower",name:"Black Rot",
desc:"Bacterial disease causing V-shaped lesions.",
treatment:"Use copper bactericide."},

{crop:"Cauliflower",name:"Bacterial Spot",
desc:"Water soaked spots on leaves.",
treatment:"Apply copper spray."},


]


const crops=[...new Set(diseases.map(d=>d.crop))]


function renderCrops(){

const container=document.getElementById("content")

let html=""

crops.forEach(crop=>{

html+=`

<div onclick="renderDiseases('${crop}')"
class="bg-white p-8 rounded-2xl shadow hover:shadow-xl hover:-translate-y-1 transition cursor-pointer text-center">

<h2 class="text-xl font-semibold text-emerald-800">${crop}</h2>

<p class="text-sm text-gray-500 mt-2">
Click to view diseases
</p>

</div>

`

})

container.innerHTML=html

}


function renderDiseases(crop){

const container=document.getElementById("content")

const cropDiseases=diseases.filter(d=>d.crop===crop)

let html=`

<div class="col-span-full mb-4">

<button onclick="renderCrops()"
class="text-sm text-emerald-700 mb-2">
← Back to Crops
</button>

<h2 class="text-2xl font-bold text-emerald-800">
${crop.toUpperCase()} DISEASES
</h2>

</div>

`

cropDiseases.forEach(d=>{

html+=`

<div onclick="openPopup('${d.name}','${d.desc}','${d.treatment}')"
class="bg-white p-6 rounded-xl shadow hover:shadow-xl cursor-pointer">

<h3 class="text-lg font-semibold">${d.name}</h3>

<p class="text-sm text-gray-600 mt-3">
${d.desc}
</p>

</div>

`

})

container.innerHTML=html

}


function initSearch(){

const search=document.getElementById("searchInput")

search.addEventListener("input",function(){

const q=this.value.toLowerCase().trim()

/* if search box empty → show crops again */

if(q===""){
renderCrops()
return
}

const filtered=diseases.filter(d=>
d.name.toLowerCase().includes(q)
)

let html=""

filtered.forEach(d=>{

html+=`

<div onclick="openPopup('${d.name}','${d.desc}','${d.treatment}')"
class="bg-white p-6 rounded-xl shadow cursor-pointer">

<h3 class="text-lg font-semibold">${d.name}</h3>

<p class="text-sm text-gray-600 mt-3">${d.desc}</p>

<p class="text-xs text-gray-400 mt-2">${d.crop}</p>

</div>

`

})

document.getElementById("content").innerHTML=html

})

}


function openPopup(name,desc,treatment){

document.getElementById("popupTitle").innerText=name
document.getElementById("popupDesc").innerText=desc
document.getElementById("popupTreatment").innerText="Treatment: "+treatment

document.getElementById("popup").classList.remove("hidden")
document.getElementById("popup").classList.add("flex")

}


function closePopup(){

document.getElementById("popup").classList.add("hidden")

}