import requests
import os
from typing import Dict, Optional

class ExchangeRateClient:
    @classmethod
    def get_latest_rates(cls, base_currency: str, target_currencies: Optional[str] = None) -> Dict:
        # Obtain all environment variables
        BASE_URL = os.getenv('EXCHANGE_RATE_BASE_URL')
        API_KEY = os.getenv('EXCHANGE_RATE_API_KEY')
        # Error handling if environment variables not loaded properly
        if not all([BASE_URL, API_KEY]):
            raise ValueError("Missing required environment variables: EXCHANGE_RATE_BASE_URL and EXCHANGE_RATE_API_KEY")
        # params = {
        #     'base': base_currency
        # }
        
        # if target_currencies:
        #     params['symbols'] = target_currencies
        response = requests.get(f"{BASE_URL}/{API_KEY}/latest/{base_currency}")
        response.raise_for_status()
        return response.json()

    @classmethod
    def convert_amount(cls, base_currency: str, exchange_currency: str, amount: float) -> float:
        rates = cls.get_latest_rates(base_currency, exchange_currency)
        rate = rates['conversion_rates'][exchange_currency]
        return amount * rate