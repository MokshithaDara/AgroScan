from collections import defaultdict
from datetime import datetime, timezone
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
REQUEST_TIMEOUT_SECONDS = 8
MAX_FORECAST_DAYS = 5


def _risk_level(temp_avg, humidity_avg, rain_total):
    score = 0
    if humidity_avg >= 80:
        score += 2
    elif humidity_avg >= 65:
        score += 1

    if rain_total >= 8:
        score += 2
    elif rain_total > 0:
        score += 1

    if 22 <= temp_avg <= 32:
        score += 1

    if score >= 4:
        return "high"
    if score >= 2:
        return "moderate"
    return "low"


def _preventive_recommendations(level):
    base = [
        "Scout the field daily and isolate symptomatic plants early.",
        "Avoid over-irrigation and improve canopy ventilation.",
    ]
    if level == "high":
        return base + [
            "Apply preventive fungicide/bactericide as per label guidance.",
            "Prioritize drainage and avoid evening irrigation.",
        ]
    if level == "moderate":
        return base + [
            "Prepare preventive spray materials and monitor rainfall windows.",
        ]
    return base + [
        "Maintain routine crop hygiene and continue regular monitoring.",
    ]


def _find_spray_windows(forecast_list):
    windows = []
    for item in forecast_list:
        rain = item.get("rain", {}).get("3h", 0) if isinstance(item.get("rain"), dict) else 0
        wind_kmh = float(item.get("wind", {}).get("speed", 0)) * 3.6
        dt_txt = item.get("dt_txt", "")

        if rain <= 0.2 and wind_kmh <= 18:
            windows.append(
                {
                    "start": dt_txt,
                    "wind_kmh": round(wind_kmh, 1),
                    "rain_mm_3h": round(float(rain), 2),
                    "suitable": True,
                }
            )

    return windows[:6]


def get_forecast_risk(lat, lon, days=3):
    if not API_KEY:
        raise ValueError("OPENWEATHER_API_KEY is not configured")

    days = max(1, min(int(days), MAX_FORECAST_DAYS))

    url = (
        "https://api.openweathermap.org/data/2.5/forecast"
        f"?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
    )
    response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    payload = response.json()
    entries = payload.get("list", [])
    if not entries:
        raise ValueError("Forecast data unavailable")

    grouped = defaultdict(list)
    for item in entries:
        dt_text = item.get("dt_txt")
        if not dt_text:
            continue
        day_key = dt_text.split(" ")[0]
        grouped[day_key].append(item)

    daily = []
    ordered_days = sorted(grouped.keys())[:days]
    for day in ordered_days:
        points = grouped[day]
        temps = [float(p.get("main", {}).get("temp", 0)) for p in points]
        humidity = [float(p.get("main", {}).get("humidity", 0)) for p in points]
        rain_total = sum(
            float(p.get("rain", {}).get("3h", 0))
            for p in points
            if isinstance(p.get("rain"), dict)
        )
        wind_max = max(float(p.get("wind", {}).get("speed", 0)) * 3.6 for p in points)
        risk = _risk_level(sum(temps) / max(len(temps), 1), sum(humidity) / max(len(humidity), 1), rain_total)

        daily.append(
            {
                "date": day,
                "temp_avg_c": round(sum(temps) / max(len(temps), 1), 1),
                "humidity_avg_pct": round(sum(humidity) / max(len(humidity), 1), 1),
                "rain_total_mm": round(rain_total, 1),
                "wind_max_kmh": round(wind_max, 1),
                "risk_level": risk,
                "alerts": [
                    f"{risk.title()} disease pressure expected.",
                    "High humidity/rain can increase fungal spread."
                    if risk != "low"
                    else "No major outbreak signal detected.",
                ],
                "preventive_recommendations": _preventive_recommendations(risk),
            }
        )

    spray_windows = _find_spray_windows(entries)
    generated_at = datetime.now(timezone.utc).isoformat()

    return {
        "days_requested": days,
        "days_available": len(daily),
        "generated_at_utc": generated_at,
        "daily_risk": daily,
        "spray_windows": spray_windows,
        "spray_window_note": (
            "Choose slots with low rain probability and low wind."
            if spray_windows
            else "No ideal spray window found in current forecast horizon."
        ),
    }
