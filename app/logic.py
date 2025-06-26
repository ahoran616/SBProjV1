import json
import requests
from app.config import DEV_MODE, MOCK_LIFT_FILE, LIFTIE_URL

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
