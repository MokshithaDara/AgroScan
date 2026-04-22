from typing import Dict, List, Optional


def _normalize_disease_name(disease: str) -> str:
    text = str(disease or "")
    for token in ("Ã¢â‚¬â€œ", "â€“", "–", "—"):
        text = text.replace(token, "-")
    if "-" in text:
        text = text.split("-", 1)[-1].strip()
    return text.replace("_", " ")


PRODUCT_CATALOG: Dict[str, List[Dict[str, str]]] = {
    "Bract Mosaic Virus": [
        {
            "product": "Systemic Vector Control Insecticide",
            "why": "Bract mosaic spread is vector-driven, so rapid vector knockdown reduces spread rate.",
            "when_to_use": "Immediately after first symptomatic plants and active aphid/whitefly activity.",
            "when_not_to_use": "Do not expect recovery of already infected plants from spray alone.",
            "dose_guidance": "Use crop-registered vector-control label dose only.",
        },
        {
            "product": "Neem-Based Botanical Insecticide",
            "why": "Supports vector suppression between systemic sprays in integrated schedules.",
            "when_to_use": "Low to moderate vector pressure and preventive windows.",
            "when_not_to_use": "Avoid use during heavy rain or strong wind conditions.",
            "dose_guidance": "Apply formulation-specific label rate.",
        },
        {
            "product": "Yellow Sticky Trap",
            "why": "Improves vector monitoring and helps reduce migrating insect load.",
            "when_to_use": "Deploy from early crop stage and maintain through risk period.",
            "when_not_to_use": "Do not rely on traps alone during high vector pressure.",
            "dose_guidance": "Maintain recommended trap density and timely replacement.",
        },
    ],
    "Moko": [
        {
            "product": "Copper Bactericide",
            "why": "Provides protective bacterial suppression on susceptible plant surfaces.",
            "when_to_use": "Early-stage field detection with strict sanitation measures.",
            "when_not_to_use": "Not curative for advanced vascular infection in heavily affected plants.",
            "dose_guidance": "Use banana-registered label dose and interval.",
        },
        {
            "product": "Tool Disinfectant Solution",
            "why": "Reduces mechanical spread through knives, pruning tools, and handling equipment.",
            "when_to_use": "Before and after each plant handling or pruning operation.",
            "when_not_to_use": "Do not skip disinfection between rows/blocks.",
            "dose_guidance": "Prepare disinfectant concentration exactly as label recommends.",
        },
        {
            "product": "Soil Bio-Consortium",
            "why": "Supports root-zone microbial balance and plant resilience under bacterial pressure.",
            "when_to_use": "As preventive support in moderately affected fields.",
            "when_not_to_use": "Not a substitute for rouging severely infected plants.",
            "dose_guidance": "Apply through drench or soil incorporation per label.",
        },
    ],
    "Panama": [
        {
            "product": "Trichoderma Biofungicide",
            "why": "Supports suppression of soil-borne Fusarium pressure in integrated management.",
            "when_to_use": "At planting and in early disease-risk stages.",
            "when_not_to_use": "Do not rely on single application under heavy field load.",
            "dose_guidance": "Use soil application dose exactly per label guidance.",
        },
        {
            "product": "Soil Health Conditioner",
            "why": "Improves root-zone environment and helps reduce stress susceptibility.",
            "when_to_use": "During soil rehabilitation and rotation cycles.",
            "when_not_to_use": "Not curative for plants already showing severe wilt collapse.",
            "dose_guidance": "Apply in split schedule according to product label.",
        },
        {
            "product": "Micronutrient Root Drench",
            "why": "Supports root vigor and helps maintain productivity in mildly affected blocks.",
            "when_to_use": "Early stress signals before severe vascular symptoms.",
            "when_not_to_use": "Avoid over-application in poorly drained soils.",
            "dose_guidance": "Use crop-stage and label-based drench concentration.",
        },
    ],
    "Yellow and Black Sigatoka": [
        {
            "product": "Propiconazole Fungicide",
            "why": "Systemic fungicide helps suppress active sigatoka lesion expansion.",
            "when_to_use": "At first visible streak/spot progression on leaves.",
            "when_not_to_use": "Avoid repeated same chemistry without rotation.",
            "dose_guidance": "Apply banana-registered label dose and interval.",
        },
        {
            "product": "Mancozeb Protectant Fungicide",
            "why": "Protects new foliage and reduces fresh infection establishment.",
            "when_to_use": "After systemic spray or before prolonged humid spells.",
            "when_not_to_use": "Avoid spray immediately before expected rain.",
            "dose_guidance": "Usually 2.0-2.5 g/l where label allows.",
        },
        {
            "product": "Sticker-Spreader Adjuvant",
            "why": "Improves spray retention on banana leaf surface under humid conditions.",
            "when_to_use": "Dense canopy or moderate rain-risk periods.",
            "when_not_to_use": "Do not overdose or mix with incompatible formulations.",
            "dose_guidance": "Use minimal effective label rate in tank mix.",
        },
    ],
    "Cordana": [
        {
            "product": "Copper Fungicide",
            "why": "Provides contact suppression for fungal leaf spotting complexes.",
            "when_to_use": "At first detection of leaf spotting symptoms.",
            "when_not_to_use": "Avoid repeated high-dose use during heat stress.",
            "dose_guidance": "Use crop-registered label dose and interval.",
        },
        {
            "product": "Chlorothalonil Protectant",
            "why": "Broad protectant coverage helps reduce spread to new leaves.",
            "when_to_use": "Humid weather windows with active spotting.",
            "when_not_to_use": "Not ideal as sole option under severe active infection.",
            "dose_guidance": "Apply at label-specified concentration.",
        },
        {
            "product": "Sticker-Spreader Adjuvant",
            "why": "Improves coverage uniformity on broad banana leaves.",
            "when_to_use": "When canopy density limits spray penetration.",
            "when_not_to_use": "Skip if selected fungicide label advises against adjuvant.",
            "dose_guidance": "Use lowest effective label dose.",
        },
    ],
    "Pestalotiopsis": [
        {
            "product": "Mancozeb Fungicide",
            "why": "Provides broad protectant action to limit fresh lesion development.",
            "when_to_use": "At initial spotting and before wet-weather continuation.",
            "when_not_to_use": "Avoid delayed use after severe canopy infection.",
            "dose_guidance": "Usually 2.0-2.5 g/l where crop label permits.",
        },
        {
            "product": "Tebuconazole Fungicide",
            "why": "Systemic support helps contain progressing fungal infection.",
            "when_to_use": "Follow-up window after protectant spray.",
            "when_not_to_use": "Avoid continuous single-mode use without rotation.",
            "dose_guidance": "Use registered crop dose exactly per label.",
        },
        {
            "product": "Copper Fungicide",
            "why": "Adds contact protection and lowers surface pathogen pressure.",
            "when_to_use": "Humid periods with repeated leaf wetness.",
            "when_not_to_use": "Avoid excessive repeat applications in hot hours.",
            "dose_guidance": "Follow label interval and concentration.",
        },
    ],
    "Sigatoka": [
        {
            "product": "Propiconazole Fungicide",
            "why": "Systemic action helps slow sigatoka progression on active leaves.",
            "when_to_use": "At earliest streak/spot progression stage.",
            "when_not_to_use": "Do not use repeatedly without fungicide rotation.",
            "dose_guidance": "Apply banana-registered label dose.",
        },
        {
            "product": "Mancozeb Protectant Fungicide",
            "why": "Protects emerging foliage from fresh infection.",
            "when_to_use": "Before prolonged humid periods or after rain.",
            "when_not_to_use": "Avoid sprays when rainfall is imminent.",
            "dose_guidance": "Use label-guided concentration and interval.",
        },
        {
            "product": "Sticker-Spreader Adjuvant",
            "why": "Improves canopy coverage and retention in large-leaf crop architecture.",
            "when_to_use": "Dense canopy and medium rain-risk windows.",
            "when_not_to_use": "Do not exceed adjuvant label dosage.",
            "dose_guidance": "Use lowest effective tank-mix rate.",
        },
    ],
    "Insect Pest": [
        {
            "product": "Broad-Spectrum Insecticide",
            "why": "Provides rapid suppression when unknown pest complex is damaging crop.",
            "when_to_use": "After scouting confirms threshold-crossing pest activity.",
            "when_not_to_use": "Avoid routine blanket use without monitoring data.",
            "dose_guidance": "Use only registered crop-pest label dose.",
        },
        {
            "product": "Neem Oil Spray",
            "why": "Supports integrated pest management and resistance rotation strategy.",
            "when_to_use": "Early infestations and between synthetic spray windows.",
            "when_not_to_use": "Avoid spraying under harsh midday sun.",
            "dose_guidance": "Typical 3-5 ml/l depending on formulation label.",
        },
        {
            "product": "Pheromone/Sticky Trap",
            "why": "Improves pest monitoring and helps reduce adult population pressure.",
            "when_to_use": "Continuous deployment through vulnerable crop stages.",
            "when_not_to_use": "Not sufficient as stand-alone control under severe attack.",
            "dose_guidance": "Install at recommended density and replace regularly.",
        },
    ],
    "Anthracnose": [
        {
            "product": "Mancozeb Fungicide",
            "why": "Broad-spectrum protectant useful to suppress new anthracnose infection on foliage/fruits.",
            "when_to_use": "At first lesions and before continuous wet weather.",
            "when_not_to_use": "Avoid spraying when rain is expected within a few hours.",
            "dose_guidance": "Usually 2.0-2.5 g/l water (verify product label).",
        },
        {
            "product": "Copper Fungicide",
            "why": "Adds contact protection and helps reduce surface pathogen load.",
            "when_to_use": "During humid periods with active lesion expansion.",
            "when_not_to_use": "Avoid repeated excessive use in heat-stress periods.",
            "dose_guidance": "Use crop-specific label dose and interval.",
        },
        {
            "product": "Sticker-Spreader Adjuvant",
            "why": "Improves spray retention and coverage on waxy/uneven leaf surface.",
            "when_to_use": "When rain risk is moderate and canopy is dense.",
            "when_not_to_use": "Do not overdose; follow adjuvant compatibility guidance.",
            "dose_guidance": "Use minimal label rate with fungicide tank mix.",
        },
    ],
    "Leaf Curl": [
        {
            "product": "Imidacloprid Insecticide",
            "why": "Targets whitefly vectors that drive leaf curl spread.",
            "when_to_use": "When vector counts cross threshold in scouting/traps.",
            "when_not_to_use": "Avoid repeated back-to-back same mode of action to reduce resistance.",
            "dose_guidance": "Use registered crop dose per label.",
        },
        {
            "product": "Neem Oil Spray",
            "why": "Supports early-stage vector suppression and integrated management.",
            "when_to_use": "Low to moderate whitefly pressure and preventive windows.",
            "when_not_to_use": "Avoid intense midday heat spray.",
            "dose_guidance": "Typical 3-5 ml/l depending on formulation label.",
        },
        {
            "product": "Yellow Sticky Trap",
            "why": "Provides visible monitoring and passive vector reduction.",
            "when_to_use": "Throughout crop stage, especially early outbreak signs.",
            "when_not_to_use": "Do not rely on traps alone during heavy infestation.",
            "dose_guidance": "Deploy uniformly across field and borders.",
        },
    ],
    "Mosaic Virus": [
        {
            "product": "Vector Control Insecticide",
            "why": "Virus spread depends on vectors, so vector suppression is critical.",
            "when_to_use": "At first virus symptoms and active aphid/whitefly presence.",
            "when_not_to_use": "Do not expect curative action on already infected plants.",
            "dose_guidance": "Use only registered vector-control dose on label.",
        },
        {
            "product": "Yellow Sticky Trap",
            "why": "Improves early warning and reduces vector flight activity.",
            "when_to_use": "As preventive monitoring from early crop stage.",
            "when_not_to_use": "Not sufficient as stand-alone control under high vector pressure.",
            "dose_guidance": "Maintain adequate trap density and replacement schedule.",
        },
        {
            "product": "Neem Oil Concentrate",
            "why": "Supports integrated vector suppression in rotation strategy.",
            "when_to_use": "Between systemic sprays or at low infestation levels.",
            "when_not_to_use": "Avoid poor-coverage conditions (high wind/rain).",
            "dose_guidance": "Use formulation-specific label rate.",
        },
    ],
    "Rust": [
        {
            "product": "Propiconazole Fungicide",
            "why": "Systemic action helps slow active rust progression.",
            "when_to_use": "At initial pustule appearance.",
            "when_not_to_use": "Avoid repeated single chemistry without rotation.",
            "dose_guidance": "Commonly ~0.8-1.0 ml/l; confirm label.",
        },
        {
            "product": "Tebuconazole Fungicide",
            "why": "Provides complementary rust control in rotation.",
            "when_to_use": "Follow-up spray window after initial systemic application.",
            "when_not_to_use": "Avoid during high-heat stress hours.",
            "dose_guidance": "Use registered dose for crop stage.",
        },
        {
            "product": "Protectant Fungicide",
            "why": "Reduces fresh spore establishment on new foliage.",
            "when_to_use": "After rainfall/high humidity events.",
            "when_not_to_use": "Not ideal as only option in severe active infection.",
            "dose_guidance": "Apply as per protectant product label.",
        },
    ],
    "Downy Mildew": [
        {
            "product": "Metalaxyl Fungicide",
            "why": "Targeted anti-downy action during conducive moisture conditions.",
            "when_to_use": "Early signs or weather-conducive phase for downy spread.",
            "when_not_to_use": "Avoid delayed use after severe canopy infection.",
            "dose_guidance": "Use anti-downy registered dose and interval on label.",
        },
        {
            "product": "Mancozeb + Metalaxyl Mix",
            "why": "Provides systemic + protectant support in one schedule.",
            "when_to_use": "Moderate to high humidity windows.",
            "when_not_to_use": "Do not spray before expected rainfall.",
            "dose_guidance": "Follow premix label dose exactly.",
        },
        {
            "product": "Sticker-Spreader Adjuvant",
            "why": "Improves coverage and retention when leaf wetness risk is high.",
            "when_to_use": "Dense canopy and intermittent cloud/moisture periods.",
            "when_not_to_use": "Skip if incompatible with selected formulation.",
            "dose_guidance": "Use minimal effective label rate.",
        },
    ],
    "Whitefly": [
        {
            "product": "Imidacloprid Insecticide",
            "why": "Systemic knockdown reduces active whitefly population quickly.",
            "when_to_use": "When trap/scouting threshold is crossed.",
            "when_not_to_use": "Avoid repeated same molecule without rotation.",
            "dose_guidance": "Use registered crop-specific label dose.",
        },
        {
            "product": "Neem Oil Spray",
            "why": "Supports early suppression and helps in resistance-management programs.",
            "when_to_use": "Low to moderate infestation windows.",
            "when_not_to_use": "Avoid application under extreme heat or rain forecast.",
            "dose_guidance": "Apply formulation label rate (commonly 3-5 ml/l).",
        },
        {
            "product": "Yellow Sticky Trap",
            "why": "Essential for monitoring and passive reduction of flying adults.",
            "when_to_use": "Place early and maintain throughout season.",
            "when_not_to_use": "Do not rely only on traps at high infestation.",
            "dose_guidance": "Use recommended field density and replacement cycle.",
        },
    ],
    "Yellowish": [
        {
            "product": "Balanced NPK Fertilizer",
            "why": "Addresses common macro-nutrient imbalance behind yellowing symptoms.",
            "when_to_use": "When uniform chlorosis suggests nutritional stress.",
            "when_not_to_use": "Avoid heavy single-dose application on dry soils.",
            "dose_guidance": "Split application as per crop stage and label.",
        },
        {
            "product": "Micronutrient Mixture",
            "why": "Corrects likely Zn/Fe/Mg trace deficiencies linked to leaf yellowing.",
            "when_to_use": "Interveinal chlorosis and weak new growth signs.",
            "when_not_to_use": "Do not mix incompatible salts in one tank.",
            "dose_guidance": "Use foliar/soil dose per label recommendation.",
        },
        {
            "product": "Seaweed Biostimulant",
            "why": "Improves stress recovery and supports root activity.",
            "when_to_use": "After correction spray in stressed crop conditions.",
            "when_not_to_use": "Not a replacement for core nutrient correction.",
            "dose_guidance": "Apply low label dose at recommended interval.",
        },
    ],
    "Early Leaf Spot": [
        {
            "product": "Chlorothalonil Protectant Fungicide",
            "why": "Early protectant cover limits fresh spot establishment.",
            "when_to_use": "At first visible lesions on lower foliage.",
            "when_not_to_use": "Avoid delayed start after severe spread.",
            "dose_guidance": "Use registered label concentration and interval.",
        },
        {
            "product": "Mancozeb Fungicide",
            "why": "Broad-spectrum support helps suppress early lesion progression.",
            "when_to_use": "Humid conditions and rainfall-triggered infection windows.",
            "when_not_to_use": "Avoid sprays just before rainfall.",
            "dose_guidance": "Typically 2.0-2.5 g/l where label allows.",
        },
        {
            "product": "Sticker-Spreader Adjuvant",
            "why": "Improves spray distribution and retention on lower canopy leaves.",
            "when_to_use": "Dense canopy or frequent dew periods.",
            "when_not_to_use": "Skip if formulation compatibility is not confirmed.",
            "dose_guidance": "Use minimal effective label rate.",
        },
    ],
    "Late Leaf Spot": [
        {
            "product": "Tebuconazole Fungicide",
            "why": "Systemic support is useful when late leaf spot pressure is active.",
            "when_to_use": "At first clear expansion of late spot lesions.",
            "when_not_to_use": "Avoid repeated solo chemistry use without alternation.",
            "dose_guidance": "Use label-approved crop dose and interval.",
        },
        {
            "product": "Mancozeb Protectant Fungicide",
            "why": "Protects newly emerging foliage against fresh infection cycles.",
            "when_to_use": "Follow-up spray after systemic window and humid forecasts.",
            "when_not_to_use": "Avoid if rain is expected shortly after application.",
            "dose_guidance": "Use registered dose as per product label.",
        },
        {
            "product": "Propiconazole Fungicide",
            "why": "Alternative systemic option for rotation and resistance management.",
            "when_to_use": "Next scheduled rotation window under continued pressure.",
            "when_not_to_use": "Do not overuse without mode-of-action rotation.",
            "dose_guidance": "Apply crop-specific label concentration.",
        },
    ],
    "Flea Beetle": [
        {
            "product": "Targeted Beetle Insecticide",
            "why": "Reduces active flea beetle feeding damage on young leaves.",
            "when_to_use": "When shot-hole injury crosses scouting threshold.",
            "when_not_to_use": "Avoid routine use without threshold confirmation.",
            "dose_guidance": "Use label-recommended crop-pest dose.",
        },
        {
            "product": "Neem Oil Spray",
            "why": "Supports suppression in early or moderate beetle pressure.",
            "when_to_use": "Early infestation and preventive border management.",
            "when_not_to_use": "Avoid spraying during high-temperature midday period.",
            "dose_guidance": "Use formulation label rate.",
        },
        {
            "product": "Sticky Trap",
            "why": "Improves pest monitoring and migration tracking at field edges.",
            "when_to_use": "Install early and maintain through vulnerable growth stages.",
            "when_not_to_use": "Not sufficient as a stand-alone in severe infestation.",
            "dose_guidance": "Deploy as per recommended spacing and count.",
        },
    ],
    "Black Rot": [
        {
            "product": "Copper Bactericide",
            "why": "Protective bacterial suppression helps reduce further spread.",
            "when_to_use": "At early symptom stage with strict sanitation practices.",
            "when_not_to_use": "Not curative for heavily infected tissues.",
            "dose_guidance": "Use crop-specific label concentration and interval.",
        },
        {
            "product": "Sanitizer for Tools",
            "why": "Prevents mechanical spread during pruning and handling.",
            "when_to_use": "Before and after each row/plant operation.",
            "when_not_to_use": "Do not skip disinfection between infected and healthy blocks.",
            "dose_guidance": "Prepare solution at manufacturer-recommended concentration.",
        },
        {
            "product": "Protective Bio-Bactericide",
            "why": "Adds preventive support in integrated bacterial disease management.",
            "when_to_use": "Preventive and early-stage field management.",
            "when_not_to_use": "Do not depend on bio-product alone in severe outbreak.",
            "dose_guidance": "Use formulation label dose and reapplication interval.",
        },
    ],
    "Bacterial Spot": [
        {
            "product": "Copper Oxychloride Bactericide",
            "why": "Common protective option for bacterial foliar spot suppression.",
            "when_to_use": "At initial spotting and during wet-weather risk periods.",
            "when_not_to_use": "Avoid repeated high-frequency use without guidance.",
            "dose_guidance": "Use registered crop label dose only.",
        },
        {
            "product": "Bio-Bactericide",
            "why": "Supports integrated management and reduces reliance on one chemistry.",
            "when_to_use": "Rotation window between copper-based sprays.",
            "when_not_to_use": "Not a stand-alone option during severe active spread.",
            "dose_guidance": "Apply at formulation-specific label rate.",
        },
        {
            "product": "Sticker-Spreader Adjuvant",
            "why": "Improves leaf-surface coverage in dense foliage conditions.",
            "when_to_use": "Humid conditions where complete coverage is difficult.",
            "when_not_to_use": "Do not mix if bactericide label disallows adjuvant use.",
            "dose_guidance": "Use minimal effective label amount.",
        },
    ],
    "Nutrition Deficiency": [
        {
            "product": "Balanced NPK Fertilizer",
            "why": "Corrects major macronutrient imbalance affecting vigor.",
            "when_to_use": "When deficiency pattern indicates N-P-K correction need.",
            "when_not_to_use": "Avoid one-time heavy dose in dry/stressed crop.",
            "dose_guidance": "Split doses per soil-test and crop stage.",
        },
        {
            "product": "Micronutrient Mixture",
            "why": "Addresses trace nutrient limits like Zn/Fe/B deficiency symptoms.",
            "when_to_use": "Interveinal chlorosis or weak new growth symptoms.",
            "when_not_to_use": "Do not combine incompatible salts in same tank.",
            "dose_guidance": "Use label foliar/soil dose based on deficiency.",
        },
        {
            "product": "Seaweed Growth Booster",
            "why": "Supports stress recovery and root activity.",
            "when_to_use": "Post-stress recovery phases and poor vigor periods.",
            "when_not_to_use": "Not a substitute for core nutrient correction.",
            "dose_guidance": "Use low label dose at recommended interval.",
        },
    ],
}


def _build_links(product: str) -> List[Dict[str, str]]:
    query = product.replace(" ", "+")
    return [
        {
            "platform": "Amazon",
            "link": f"https://www.amazon.in/s?k={query}",
        },
        {
            "platform": "Flipkart",
            "link": f"https://www.flipkart.com/search?q={query}",
        },
        {
            "platform": "Agri Stores",
            "link": f"https://www.google.com/search?q={query}+agriculture+store",
        },
    ]


def get_product_links(disease: str, weather: Optional[Dict] = None) -> List[Dict[str, str]]:
    disease_name = _normalize_disease_name(disease)
    selected = PRODUCT_CATALOG.get(
        disease_name,
        [
            {
                "product": "General Crop Protection Kit",
                "why": "Useful starter option when disease-specific mapping is unavailable.",
                "when_to_use": "Use after field scouting and local agronomy confirmation.",
                "when_not_to_use": "Avoid blind application without symptom-based validation.",
                "dose_guidance": "Follow product label and local extension guidance.",
            },
            {
                "product": "Balanced Nutrient Spray",
                "why": "Supports crop recovery and vigor under stress.",
                "when_to_use": "During mild stress with no severe active infection.",
                "when_not_to_use": "Not a replacement for pathogen/vector-specific control.",
                "dose_guidance": "Apply as per label.",
            },
            {
                "product": "Preventive Bio Pesticide",
                "why": "Adds preventive support in integrated crop protection schedules.",
                "when_to_use": "Routine prevention and early symptoms.",
                "when_not_to_use": "Avoid depending on it alone in severe outbreaks.",
                "dose_guidance": "Use formulation-specific label dose.",
            },
        ],
    )

    weather_note = ""
    if isinstance(weather, dict):
        condition = str(weather.get("condition", "")).lower()
        humidity = weather.get("humidity")
        try:
            humidity_value = float(humidity)
        except (TypeError, ValueError):
            humidity_value = None

        if "rain" in condition or "storm" in condition:
            weather_note = "Rainy condition: prioritize products with good retention and spray in next dry window."
        elif humidity_value is not None and humidity_value >= 80:
            weather_note = "High humidity: maintain tighter interval and ensure complete canopy coverage."

    links: List[Dict[str, str]] = []
    for product_meta in selected[:3]:
        product_name = product_meta["product"]
        for link in _build_links(product_name):
            links.append(
                {
                    "product": product_name,
                    "platform": link["platform"],
                    "link": link["link"],
                    "reason": product_meta["why"],
                    "when_to_use": product_meta["when_to_use"],
                    "when_not_to_use": product_meta["when_not_to_use"],
                    "dose_guidance": product_meta["dose_guidance"],
                    "weather_note": weather_note,
                }
            )
    return links
