import json
import requests
from app.config import DEV_MODE

# === 🌄 WEATHER DATA ===
def get_weather_data(lat, lon, resort_slug):
    if DEV_MODE:
        try:
            with open(f"mock_data/mock_weather_{resort_slug}.json", "r") as f:
                print(f"[DEV MODE] Loaded mock weather for {resort_slug}")
                return json.load(f)
        except FileNotFoundError:
            print(f"[DEV MODE] No mock weather file found for {resort_slug}")
            return {}
    else:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
            "daily": "snowfall_sum,snow_depth_max",
            "timezone": "America/New_York"
        }
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[LIVE MODE] Failed to load weather data for {resort_slug}: {e}")
            return {}

# === 🚡 LIFT STATUS DATA ===
def get_lift_data(resort_slug, dev_mode=False):
    if dev_mode:
        # Load mock data from local file
        try:
            with open(f"mock_data/mock_liftie_{resort_slug.replace('-', '')}.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    else:
        # Try fetching live data
        try:
            url = f"https://liftie.info/api/resort/{resort_slug}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None
