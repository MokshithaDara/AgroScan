from dotenv import load_dotenv
import os
import requests

load_dotenv()  # loads .env file

API_KEY = os.getenv("OPENWEATHER_API_KEY")
REQUEST_TIMEOUT_SECONDS = 8

def get_weather(lat, lon):
    if not API_KEY:
        raise ValueError("OPENWEATHER_API_KEY is not configured")

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
    r = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    r.raise_for_status()
    data = r.json()

    if "main" not in data:
        raise ValueError("Weather API failed")

    return {
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["main"]
    }
