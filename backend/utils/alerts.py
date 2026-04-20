def generate_alerts(disease, weather):
    temp = weather.get("temperature", 0)
    humidity = weather.get("humidity", 0)

    try:
        humidity = float(humidity)
    except (TypeError, ValueError):
        humidity = 0

    rain = weather.get("rain", 0)
    wind = weather.get("wind", 0)

    alerts = []

    # Extract disease name from values like "Crop – Disease".
    disease_name = disease
    normalized = disease_name
    for token in ("â€“", "–", "—"):
        normalized = normalized.replace(token, "-")
    if "-" in normalized:
        disease_name = normalized.split("-", 1)[-1].strip()

    # ---------- FUNGAL DISEASES ----------
    if disease_name in ["Anthracnose", "Sigatoka", "Cordana", "Pestalotiopsis", "Downy", "Mildew", "Leaf", "Spot", "Rust"]:
        if humidity > 80:
            alerts.append("High humidity may accelerate fungal disease spread.")
        if rain > 0:
            alerts.append("Rain may spread fungal spores between plants.")

    # ---------- BACTERIAL DISEASES ----------
    if disease_name in ["Bacterial", "Rot"]:
        if rain > 0:
            alerts.append("Rain splashes may spread bacterial infection.")
        if wind > 10:
            alerts.append("Wind may spread bacteria between plants.")

    # ---------- VIRUS DISEASES ----------
    if disease_name in ["Virus", "Curl"]:
        if temp > 30:
            alerts.append("Warm weather increases insect vectors spreading viruses.")
        if wind > 10:
            alerts.append("Wind may help spread insect carriers.")

    # ---------- INSECT PEST ----------
    if disease_name in ["Whitefly", "Beetle", "Pest"]:
        if temp > 30:
            alerts.append("High temperature favors pest population growth.")
        if humidity < 40:
            alerts.append("Dry weather increases pest activity.")

    # ---------- GENERAL WEATHER ALERTS ----------
    if temp > 35:
        alerts.append("Extreme temperature stress detected for crops.")
    if wind > 20:
        alerts.append("Strong winds may damage crops and spread disease.")

    # ---------- HEALTHY ----------
    if "Healthy" in disease:
        alerts.append("Crop appears healthy.")

    return alerts
