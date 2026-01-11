import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

# Configure logger
logger = logging.getLogger(__name__)

class NHTSAClient:
    """
    A professional-grade API client for the NHTSA vPIC database.
    Includes automatic retries, timeouts, and error handling.
    """
    BASE_URL = "https://vpic.nhtsa.dot.gov/api/vehicles"

    def __init__(self, timeout=5, retries=3):
        self.timeout = timeout
        self.session = requests.Session()

        # Configure robust retry logic (exponential backoff)
        retry_strategy = Retry(
            total=retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def decode_vin(self, vin: str) -> dict:
        """
        Decodes a VIN using the NHTSA flat format API.
        Returns a normalized dictionary of vehicle attributes or None on failure.
        """
        url = f"{self.BASE_URL}/DecodeVinValues/{vin}"
        params = {'format': 'json'}

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            results = data.get('Results', [])

            if not results:
                logger.warning(f"No results found for VIN: {vin}")
                return None

            vehicle = results[0]

            # Normalize the output for our application
            return {
                "year": vehicle.get('ModelYear'),
                "make": vehicle.get('Make'),
                "model": vehicle.get('Model'),
                "body": vehicle.get('BodyClass'),
                "plant": vehicle.get('PlantCity'),
                "fuel_type": vehicle.get('FuelTypePrimary'),
                "manufacturer": vehicle.get('Manufacturer'),
                "raw": vehicle  # Keep raw data just in case
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"NHTSA API Request failed: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Data parsing error: {e}")
            return None
