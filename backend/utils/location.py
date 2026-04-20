from dotenv import load_dotenv
import os
import requests

load_dotenv()  # loads .env file

API_KEY = os.getenv("OPENWEATHER_API_KEY")
REQUEST_TIMEOUT_SECONDS = 8

def get_coordinates(location):
    if not API_KEY:
        raise ValueError("OPENWEATHER_API_KEY is not configured")

    url = f"https://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={API_KEY}"
    r = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    r.raise_for_status()
    data = r.json()

    if not data:
        raise ValueError("Location not found")

    return data[0]["lat"], data[0]["lon"]


def get_city_from_coordinates(lat, lon):
    """Reverse geocoding: Get city name from latitude and longitude"""
    if not API_KEY:
        raise ValueError("OPENWEATHER_API_KEY is not configured")

    url = f"https://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={API_KEY}"
    r = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    r.raise_for_status()
    data = r.json()

    if not data:
        raise ValueError("Location not found for coordinates")

    return data[0].get("name", "Unknown")
