import re
from typing import Dict, List, Optional


def _normalize_disease_label(disease: str) -> str:
    text = str(disease or "")
    for token in ("Ã¢â‚¬â€œ", "â€“", "–", "—"):
        text = text.replace(token, "-")
    if "-" in text:
        text = text.split("-", 1)[-1].strip()
    return text.replace(" ", "_")


DISEASE_MANAGEMENT: Dict[str, Dict[str, List[str] | str]] = {
    "Yellow_and_Black_Sigatoka": {
        "summary": "Remove heavily infected leaves and begin protectant + systemic fungicide rotation.",
        "steps": [
            "Apply propiconazole/triazole fungicide at 7-10 day interval as label permits.",
            "Alternate with mancozeb protectant to reduce resistance pressure.",
            "Open canopy and avoid overhead irrigation to reduce leaf wetness."
        ],
        "dose": "Typical foliar dose range is 1.0-2.0 ml/l (systemic) or 2.0-2.5 g/l (protectant); follow product label exactly.",
        "interval": "7-10 days during active pressure; tighten interval after continuous wet spells.",
    },
    "Anthracnose": {
        "summary": "Remove infected tissues and protect new growth with contact fungicide coverage.",
        "steps": [
            "Remove and destroy infected fruits/shoots before spray.",
            "Spray mancozeb/copper fungicide on both leaf surfaces and fruits.",
            "Improve drainage and spacing to keep canopy drier."
        ],
        "dose": "Common range: 2.0-2.5 g/l for protectant fungicide, per label and crop stage.",
        "interval": "7 days in humid/rainy spells; 10 days in stable weather.",
    },
    "Leaf_Curl": {
        "summary": "Control whitefly vectors quickly and reduce source plants to limit viral spread.",
        "steps": [
            "Install yellow sticky traps across the field and monitor vector load.",
            "Apply neem-based or registered systemic whitefly control at threshold.",
            "Remove severely curled plants/shoots from field edges first."
        ],
        "dose": "Use label dose of selected whitefly control; avoid over-concentration.",
        "interval": "Repeat 5-7 days while vector pressure remains above threshold.",
    },
    "Whitefly": {
        "summary": "Reduce vector population using integrated trap + targeted spray approach.",
        "steps": [
            "Place yellow sticky traps and inspect underside of leaves every 2 days.",
            "Use neem/systemic spray early morning or late afternoon.",
            "Control weeds and alternate hosts around field border."
        ],
        "dose": "Use recommended label dose for selected whitefly product.",
        "interval": "5-7 days if active colonies persist.",
    },
    "Mosaic_Virus": {
        "summary": "No curative spray exists; remove infected plants early and control vectors aggressively.",
        "steps": [
            "Rogue infected plants immediately to reduce field inoculum.",
            "Control aphid/whitefly vectors with trap + selective spray strategy.",
            "Disinfect tools and avoid handling plants when foliage is wet."
        ],
        "dose": "Focus on vector control product label dose; do not rely on curative claims for viruses.",
        "interval": "Vector checks every 48h during active spread periods.",
    },
    "Rust": {
        "summary": "Start rust-specific fungicide at first pustule and maintain follow-up cover.",
        "steps": [
            "Use propiconazole/tebuconazole group fungicide at first visible pustules.",
            "Remove heavily infected lower leaves where practical.",
            "Maintain airflow and avoid irrigation that prolongs leaf wetness."
        ],
        "dose": "Common systemic range around 0.8-1.0 ml/l (label dependent).",
        "interval": "7-10 days based on severity and weather.",
    },
    "Early_Leaf_Spot": {
        "summary": "Begin spot management early with protectant fungicide and canopy sanitation.",
        "steps": [
            "Spray chlorothalonil/mancozeb at first detectable lesions.",
            "Remove lower diseased leaves and maintain row ventilation.",
            "Track disease progression after each rain event."
        ],
        "dose": "Protectant dose typically 2.0-2.5 g/l, as per label.",
        "interval": "7-10 days; shorten in persistent humidity.",
    },
    "Late_Leaf_Spot": {
        "summary": "Use immediate fungicide rotation and continue weather-triggered follow-up.",
        "steps": [
            "Start systemic + protectant alternation without delay.",
            "Maintain strict residue sanitation and avoid dense canopy.",
            "Inspect lower canopy where infection appears first."
        ],
        "dose": "Follow registered dose for selected fungicide chemistry.",
        "interval": "7 days in high humidity; up to 10 days in stable dry periods.",
    },
    "Downy_Mildew": {
        "summary": "Target downy pressure early and reduce prolonged canopy moisture.",
        "steps": [
            "Apply anti-downy fungicide (for example metalaxyl-based) as per label.",
            "Avoid late-evening irrigation and improve spacing.",
            "Prioritize morning scouting after cloudy/humid nights."
        ],
        "dose": "Use label-recommended dose for anti-downy product.",
        "interval": "5-7 days in conducive conditions; extend when pressure drops.",
    },
    "Downey_Mildew": {
        "summary": "Target downy pressure early and reduce prolonged canopy moisture.",
        "steps": [
            "Apply anti-downy fungicide (for example metalaxyl-based) as per label.",
            "Avoid late-evening irrigation and improve spacing.",
            "Prioritize morning scouting after cloudy/humid nights."
        ],
        "dose": "Use label-recommended dose for anti-downy product.",
        "interval": "5-7 days in conducive conditions; extend when pressure drops.",
    },
    "Black_Rot": {
        "summary": "Use sanitation-first bacterial management with clean water and copper bactericide support.",
        "steps": [
            "Remove infected leaves and avoid water splash across rows.",
            "Apply copper bactericide at label interval.",
            "Sanitize tools and avoid field operations on wet foliage."
        ],
        "dose": "Follow crop-specific copper bactericide label dose.",
        "interval": "7 days in wet periods; monitor new infection front.",
    },
    "Bacterial_Spot": {
        "summary": "Limit bacterial spread with sanitation and protective bactericide coverage.",
        "steps": [
            "Remove infected leaves and reduce splash dispersal.",
            "Use copper-based bactericide as per registered guidance.",
            "Improve ventilation and avoid handling plants while wet."
        ],
        "dose": "Use registered copper/bactericide dose on label.",
        "interval": "7-10 days depending on weather pressure.",
    },
    "Flea_Beetle": {
        "summary": "Protect young crop stage with threshold-based beetle suppression and scouting.",
        "steps": [
            "Inspect seedling/young plants for shot-hole injury.",
            "Use neem or recommended insecticide when threshold is crossed.",
            "Keep border weeds low to reduce beetle migration."
        ],
        "dose": "Use product label dose for beetle-targeting formulation.",
        "interval": "5-7 days while feeding pressure is active.",
    },
    "Nutrition_Deficiency": {
        "summary": "Correct nutrient imbalance using soil-test guided feeding and split application.",
        "steps": [
            "Use balanced NPK + micronutrient correction based on deficiency pattern.",
            "Apply in split doses to improve uptake and reduce losses.",
            "Review irrigation uniformity and root-zone conditions."
        ],
        "dose": "Follow soil-test and label guidance for foliar/soil dose.",
        "interval": "Reassess response in 10-14 days and adjust.",
    },
}


def _build_weather_cautions(weather: Optional[Dict]) -> List[str]:
    if not isinstance(weather, dict):
        return []

    cautions: List[str] = []
    humidity_raw = weather.get("humidity")
    temp_raw = weather.get("temperature")
    condition = str(weather.get("condition", "")).lower()

    humidity = None
    temp = None
    try:
        humidity = float(humidity_raw)
    except (TypeError, ValueError):
        pass
    try:
        temp = float(temp_raw)
    except (TypeError, ValueError):
        pass

    if humidity is not None and humidity >= 80:
        cautions.append(
            f"Humidity is {humidity:.0f}%: use tighter follow-up interval and prioritize protectant coverage."
        )
    elif humidity is not None and humidity <= 40:
        cautions.append(
            f"Humidity is {humidity:.0f}%: avoid phytotoxic over-spraying and protect crop from moisture stress."
        )

    if "rain" in condition or "storm" in condition or "drizzle" in condition:
        cautions.append(
            "Rainy signal detected: avoid spray just before rain and target first stable dry window."
        )
    elif "cloud" in condition and humidity is not None and humidity >= 70:
        cautions.append(
            "Cloudy-humid conditions may extend leaf wetness; prioritize morning sprays and scouting."
        )

    if temp is not None and temp >= 34:
        cautions.append(
            f"Temperature is {temp:.1f} C: avoid peak-afternoon spray to reduce evaporation and leaf stress."
        )
    elif temp is not None and temp <= 18:
        cautions.append(
            f"Temperature is {temp:.1f} C: morning drying may be slow; monitor fungal progression closely."
        )

    return cautions


def get_treatment_plan(disease: str, weather: Optional[Dict] = None) -> Dict:
    disease_key = _normalize_disease_label(disease)
    base = DISEASE_MANAGEMENT.get(
        disease_key,
        {
            "summary": "Isolate affected plants, improve sanitation, and follow crop-specific integrated management.",
            "steps": [
                "Inspect field every 48 hours and mark progression zones.",
                "Remove heavily affected tissue and sanitize tools between rows.",
                "Use registered crop-specific product according to label guidance."
            ],
            "dose": "Use only registered input and label dose for crop and growth stage.",
            "interval": "Reassess in 3-5 days and continue based on observed severity.",
        },
    )

    weather_cautions = _build_weather_cautions(weather)
    steps = list(base["steps"])
    if weather_cautions:
        steps.extend(weather_cautions[:2])

    summary = str(base["summary"])
    if weather_cautions:
        summary = f"{summary} Weather-aware caution: {weather_cautions[0]}"

    return {
        "summary": summary,
        "steps": steps,
        "dose_guidance": base["dose"],
        "interval_guidance": base["interval"],
        "weather_cautions": weather_cautions,
    }


def get_treatment(disease: str, weather: Optional[Dict] = None) -> str:
    plan = get_treatment_plan(disease, weather=weather)
    parts = list(plan["steps"][:3])
    if plan["dose_guidance"]:
        parts.append(f"Dose guidance: {plan['dose_guidance']}")
    if plan["interval_guidance"]:
        parts.append(f"Interval: {plan['interval_guidance']}")
    return ". ".join(parts)
