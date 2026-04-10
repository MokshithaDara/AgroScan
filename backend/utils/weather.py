import requests

API_KEY = "49954bebd2163025ef42b71310bc8345"

def get_weather(lat, lon):

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    r = requests.get(url)
    data = r.json()

    weather = {
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["description"],
        "wind": data["wind"]["speed"],
        "rain": data.get("rain", {}).get("1h", 0)
    }

    return weather