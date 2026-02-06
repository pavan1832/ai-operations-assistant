"""
Weather Tool - Get current weather information for cities
"""

import os
import requests
from typing import Dict, Any
from tools import BaseTool


class WeatherTool(BaseTool):
    """Tool for getting weather information"""
    
    def __init__(self):
        """Initialize Weather tool"""
        super().__init__(
            name="weather",
            description="Get current weather information for any city including temperature, conditions, humidity, and wind speed",
            parameters={
                "city": {
                    "type": "string",
                    "description": "City name (e.g., 'London', 'New York', 'Tokyo')"
                },
                "units": {
                    "type": "string",
                    "description": "Temperature units: 'metric' (Celsius) or 'imperial' (Fahrenheit)",
                    "default": "metric",
                    "enum": ["metric", "imperial"]
                }
            }
        )
        
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    def execute(self, city: str, units: str = "metric", **kwargs) -> Dict[str, Any]:
        """
        Get current weather for a city
        
        Args:
            city: City name
            units: Temperature units (metric/imperial)
            
        Returns:
            Weather information
        """
        if not self.api_key:
            # Fallback: Use free weather API (wttr.in) if OpenWeather API key not available
            return self._get_weather_fallback(city, units)
        
        params = {
            "q": city,
            "appid": self.api_key,
            "units": units
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            temp_unit = "°C" if units == "metric" else "°F"
            speed_unit = "m/s" if units == "metric" else "mph"
            
            return {
                "success": True,
                "city": data["name"],
                "country": data["sys"]["country"],
                "weather": {
                    "condition": data["weather"][0]["main"],
                    "description": data["weather"][0]["description"],
                    "temperature": f"{data['main']['temp']}{temp_unit}",
                    "feels_like": f"{data['main']['feels_like']}{temp_unit}",
                    "temp_min": f"{data['main']['temp_min']}{temp_unit}",
                    "temp_max": f"{data['main']['temp_max']}{temp_unit}",
                    "humidity": f"{data['main']['humidity']}%",
                    "pressure": f"{data['main']['pressure']} hPa",
                    "wind_speed": f"{data['wind']['speed']} {speed_unit}",
                    "clouds": f"{data['clouds']['all']}%"
                }
            }
            
        except requests.exceptions.RequestException as e:
            return self._get_weather_fallback(city, units)
    
    def _get_weather_fallback(self, city: str, units: str = "metric") -> Dict[str, Any]:
        """
        Fallback weather API using wttr.in (no API key required)
        
        Args:
            city: City name
            units: Temperature units
            
        Returns:
            Weather information
        """
        try:
            # wttr.in provides free weather data
            url = f"https://wttr.in/{city}?format=j1"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            current = data["current_condition"][0]
            
            # Convert to requested units
            temp_c = float(current["temp_C"])
            if units == "imperial":
                temp = (temp_c * 9/5) + 32
                temp_unit = "°F"
                speed_unit = "mph"
                wind_speed = float(current["windspeedMiles"])
            else:
                temp = temp_c
                temp_unit = "°C"
                speed_unit = "km/h"
                wind_speed = float(current["windspeedKmph"])
            
            return {
                "success": True,
                "city": city,
                "country": data["nearest_area"][0]["country"][0]["value"],
                "weather": {
                    "condition": current["weatherDesc"][0]["value"],
                    "description": current["weatherDesc"][0]["value"],
                    "temperature": f"{temp:.1f}{temp_unit}",
                    "feels_like": f"{temp:.1f}{temp_unit}",
                    "humidity": f"{current['humidity']}%",
                    "pressure": f"{current['pressure']} hPa",
                    "wind_speed": f"{wind_speed} {speed_unit}",
                    "clouds": f"{current['cloudcover']}%",
                    "visibility": f"{current['visibility']} km"
                },
                "source": "wttr.in (fallback)"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Unable to fetch weather data: {str(e)}",
                "message": "Weather API is unavailable. Please add OPENWEATHER_API_KEY to .env or check your internet connection."
            }
