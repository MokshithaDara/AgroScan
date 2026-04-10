import requests

API_KEY = "49954bebd2163025ef42b71310bc8345"

def get_coordinates(location):

    url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={API_KEY}"

    r = requests.get(url)
    data = r.json()

    lat = data[0]["lat"]
    lon = data[0]["lon"]

    return lat, lon