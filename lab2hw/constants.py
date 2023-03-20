from typing import Final, List
from dataclasses import dataclass


GEOCODE_API_URL: Final[str] = "https://nominatim.openstreetmap.org/search?q={location}&format=jsonv2&limit=1"
WEATHER_HISTORICAL_DATA_API_URL: Final[str] = "https://archive-api.open-meteo.com/v1/era5?" \
                                              "latitude={latitude}&longitude={longitude}" \
                                              "&start_date={startdate}&end_date={enddate}&{weatherinterval}="
WEATHER_FORECAST_API_URL: Final[str] = "https://api.open-meteo.com/v1/forecast?" \
                                       "latitude={latitude}&longitude={longitude}&forecast_days={forecastdays}" \
                                       "&{weatherinterval}="

WEATHER_INTERVAL: Final[str] = "hourly"
WEATHER_DATES: Final[str] = "time"
WEATHER_UNITS: Final[str] = f"{WEATHER_INTERVAL}_units"
WEATHER_FEATURES: Final[List[str]] = [
    "temperature_2m",
    "relativehumidity_2m"
]


@dataclass
class Weather:
    historical_avg_temp: float
    historical_max_temp: float
    historical_max_temp_date: str
    historical_min_temp: float
    historical_min_temp_date: str

    historical_avg_humidity: float
    historical_max_humidity: float
    historical_max_humidity_date: str
    historical_min_humidity: float
    historical_min_humidity_date: str

    forecast_avg_temp: float
    forecast_max_temp: float
    forecast_max_temp_date: str
    forecast_min_temp: float
    forecast_min_temp_date: str

    forecast_avg_humidity: float
    forecast_max_humidity: float
    forecast_max_humidity_date: str
    forecast_min_humidity: float
    forecast_min_humidity_date: str

    temp_unit: str
    humidity_unit: str
