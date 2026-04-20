from typing import Dict, List, Optional


def _normalize_disease_name(disease: str) -> str:
    text = str(disease or "")
    for token in ("Ã¢â‚¬â€œ", "â€“", "–", "—"):
        text = text.replace(token, "-")
    if "-" in text:
        text = text.split("-", 1)[-1].strip()
    return text.replace("_", " ")


PRODUCT_CATALOG: Dict[str, List[Dict[str, str]]] = {
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
