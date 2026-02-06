"""
Exchange Rate Tool - Get currency exchange rates
"""

import requests
from typing import Dict, Any
from tools import BaseTool


class ExchangeRateTool(BaseTool):
    """Tool for getting currency exchange rates"""
    
    def __init__(self):
        """Initialize Exchange Rate tool"""
        super().__init__(
            name="exchange_rate",
            description="Get current exchange rates between currencies (e.g., USD to EUR, GBP to JPY)",
            parameters={
                "from_currency": {
                    "type": "string",
                    "description": "Source currency code (e.g., 'USD', 'EUR', 'GBP')"
                },
                "to_currency": {
                    "type": "string",
                    "description": "Target currency code (e.g., 'USD', 'EUR', 'GBP')"
                },
                "amount": {
                    "type": "number",
                    "description": "Amount to convert (default: 1)",
                    "default": 1
                }
            }
        )
        
        # Using exchangerate-api.com free tier (no API key required)
        self.base_url = "https://api.exchangerate-api.com/v4/latest"
    
    def execute(
        self,
        from_currency: str,
        to_currency: str,
        amount: float = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get exchange rate and convert amount
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            amount: Amount to convert
            
        Returns:
            Exchange rate and converted amount
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        try:
            # Get exchange rates for source currency
            url = f"{self.base_url}/{from_currency}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if to_currency not in data["rates"]:
                return {
                    "success": False,
                    "error": f"Currency code '{to_currency}' not found"
                }
            
            rate = data["rates"][to_currency]
            converted_amount = amount * rate
            
            return {
                "success": True,
                "from_currency": from_currency,
                "to_currency": to_currency,
                "exchange_rate": rate,
                "amount": amount,
                "converted_amount": round(converted_amount, 2),
                "conversion": f"{amount} {from_currency} = {converted_amount:.2f} {to_currency}",
                "last_updated": data["date"]
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Unable to fetch exchange rates: {str(e)}"
            }
