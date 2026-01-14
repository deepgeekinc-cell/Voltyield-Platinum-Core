import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class NHTSAClient:
    BASE_URL = "https://vpic.nhtsa.dot.gov/api/vehicles"

    def __init__(self, timeout=5, retries=3):
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=Retry(total=retries, backoff_factor=1, status_forcelist=[500, 502, 503]))
        self.session.mount("https://", adapter)

    def decode_vin(self, vin: str) -> dict:
        try:
            url = f"{self.BASE_URL}/DecodeVinValues/{vin}"
            resp = self.session.get(url, params={'format': 'json'}, timeout=5)
            data = resp.json()
            results = data.get('Results', [])
            if not results: return None
            v = results[0]
            return {"year": v.get('ModelYear'), "make": v.get('Make'), "model": v.get('Model'), "plant": v.get('PlantCity')}
        except Exception:
            return None
