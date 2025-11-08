"""
Weather Service Module - Unified weather data access across all APIs

Supports:
- NREL NSRDB for solar resource data (TMY)
- NREL PVWatts for quick PV estimates
- Visual Crossing for historical and forecast weather
- OpenWeatherMap for real-time conditions
- NOAA CDO for long-term historical data (optional)
"""

import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json
import time
from functools import lru_cache
import logging

from config import (
    get_config,
    NREL_NSRDB_BASE_URL,
    NREL_PVWATTS_BASE_URL,
    VISUAL_CROSSING_BASE_URL,
    OPENWEATHER_BASE_URL,
    NOAA_BASE_URL,
    WORKABILITY_THRESHOLDS,
)

logger = logging.getLogger(__name__)


class WeatherAPIError(Exception):
    """Custom exception for weather API errors"""
    pass


class WeatherService:
    """
    Unified weather service for all project phases
    """

    def __init__(self, config=None):
        self.config = config or get_config()
        self.api_keys = self.config.api_keys
        self._cache = {}
        self._cache_dir = Path(self.config.app.cache_dir) / "weather"
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    # ========== NREL NSRDB METHODS ==========

    def get_nsrdb_tmy_data(
        self, lat: float, lon: float, attributes: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Get Typical Meteorological Year (TMY) data from NREL NSRDB

        Args:
            lat: Latitude
            lon: Longitude
            attributes: List of attributes to retrieve (default: all solar)

        Returns:
            DataFrame with hourly TMY data
        """
        cache_key = f"nsrdb_tmy_{lat}_{lon}"

        # Check cache
        if self.config.app.cache_enabled:
            cached_data = self._load_from_cache(cache_key)
            if cached_data is not None:
                logger.info(f"Loaded NSRDB TMY data from cache for {lat}, {lon}")
                return cached_data

        if not attributes:
            attributes = ['ghi', 'dni', 'dhi', 'wind_speed', 'air_temperature', 'solar_zenith_angle']

        url = f"{NREL_NSRDB_BASE_URL}/psm3-tmy-download.csv"

        params = {
            'api_key': self.api_keys.nrel_api_key,
            'wkt': f'POINT({lon} {lat})',
            'names': 'tmy',
            'attributes': ','.join(attributes),
            'leap_day': 'false',
            'utc': 'false',
            'interval': '60',
            'email': 'api@example.com',  # Required but not validated
        }

        try:
            logger.info(f"Fetching NSRDB TMY data for {lat}, {lon}")
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()

            # Parse CSV (skip first 2 header lines)
            from io import StringIO
            df = pd.read_csv(StringIO(response.text), skiprows=2)

            # Cache the data
            if self.config.app.cache_enabled:
                self._save_to_cache(cache_key, df)

            logger.info(f"Successfully fetched {len(df)} rows of NSRDB TMY data")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"NSRDB API error: {e}")
            raise WeatherAPIError(f"Failed to fetch NSRDB data: {e}")

    def get_nsrdb_historical(
        self,
        lat: float,
        lon: float,
        year: int,
        attributes: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Get historical solar data for a specific year from NSRDB

        Args:
            lat: Latitude
            lon: Longitude
            year: Year (1998-2023)
            attributes: List of attributes to retrieve

        Returns:
            DataFrame with hourly historical data
        """
        cache_key = f"nsrdb_historical_{lat}_{lon}_{year}"

        if self.config.app.cache_enabled:
            cached_data = self._load_from_cache(cache_key)
            if cached_data is not None:
                return cached_data

        if not attributes:
            attributes = ['ghi', 'dni', 'dhi', 'wind_speed', 'air_temperature']

        url = f"{NREL_NSRDB_BASE_URL}/psm3-download.csv"

        params = {
            'api_key': self.api_keys.nrel_api_key,
            'wkt': f'POINT({lon} {lat})',
            'names': str(year),
            'attributes': ','.join(attributes),
            'leap_day': 'false',
            'utc': 'false',
            'interval': '60',
            'email': 'api@example.com',
        }

        try:
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()

            from io import StringIO
            df = pd.read_csv(StringIO(response.text), skiprows=2)

            if self.config.app.cache_enabled:
                self._save_to_cache(cache_key, df)

            return df

        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"Failed to fetch NSRDB historical data: {e}")

    # ========== PVWATTS METHODS ==========

    def estimate_annual_production(
        self,
        system_capacity_kw: float,
        lat: float,
        lon: float,
        tilt: Optional[float] = None,
        azimuth: float = 180,
        array_type: int = 1,
        module_type: int = 1,
        losses: float = 14,
        dc_ac_ratio: Optional[float] = None,
    ) -> Dict:
        """
        Get annual energy production estimate using PVWatts

        Args:
            system_capacity_kw: DC system size in kW
            lat, lon: Site coordinates
            tilt: Array tilt (defaults to latitude)
            azimuth: 180=south, 90=east, 270=west
            array_type: 0=Fixed, 1=1-axis, 2=2-axis, 3=Azimuth, 4=1-axis backtrack
            module_type: 0=Standard, 1=Premium, 2=Thin film
            losses: System losses (%)
            dc_ac_ratio: DC to AC ratio (default 1.2)

        Returns:
            Dictionary with production estimates
        """
        url = NREL_PVWATTS_BASE_URL

        if tilt is None:
            tilt = abs(lat)

        if dc_ac_ratio is None:
            dc_ac_ratio = self.config.app.default_dc_ac_ratio

        params = {
            'api_key': self.api_keys.nrel_api_key,
            'system_capacity': system_capacity_kw,
            'module_type': module_type,
            'losses': losses,
            'array_type': array_type,
            'tilt': tilt,
            'azimuth': azimuth,
            'lat': lat,
            'lon': lon,
            'dataset': 'nsrdb',
            'radius': 0,
            'timeframe': 'monthly',
            'dc_ac_ratio': dc_ac_ratio,
        }

        try:
            logger.info(f"Calling PVWatts API for {system_capacity_kw}kW system at {lat}, {lon}")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            result = response.json()

            if 'errors' in result:
                raise WeatherAPIError(f"PVWatts API error: {result['errors']}")

            outputs = result['outputs']

            return {
                'annual_ac_kwh': outputs['ac_annual'],
                'monthly_ac_kwh': outputs['ac_monthly'],
                'solrad_monthly': outputs['solrad_monthly'],
                'solrad_annual': outputs['solrad_annual'],
                'capacity_factor': outputs['capacity_factor'],
                'ac_monthly': outputs['ac_monthly'],
                'poa_monthly': outputs['poa_monthly'],
                'dc_monthly': outputs['dc_monthly'],
            }

        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"PVWatts API request failed: {e}")

    # ========== VISUAL CROSSING METHODS ==========

    def get_historical_weather(
        self,
        lat: float,
        lon: float,
        start_date: str,
        end_date: str,
        include_solar: bool = True,
    ) -> pd.DataFrame:
        """
        Get historical weather data from Visual Crossing

        Args:
            lat, lon: Coordinates
            start_date: Start date 'YYYY-MM-DD'
            end_date: End date 'YYYY-MM-DD'
            include_solar: Include solar radiation data

        Returns:
            DataFrame with daily weather data
        """
        cache_key = f"vc_historical_{lat}_{lon}_{start_date}_{end_date}"

        if self.config.app.cache_enabled:
            cached_data = self._load_from_cache(cache_key, max_age_hours=24)
            if cached_data is not None:
                return cached_data

        url = f"{VISUAL_CROSSING_BASE_URL}/{lat},{lon}/{start_date}/{end_date}"

        elements = ['datetime', 'temp', 'humidity', 'precip', 'preciptype',
                   'windspeed', 'cloudcover', 'conditions']

        if include_solar:
            elements.extend(['solarradiation', 'solarenergy'])

        params = {
            'key': self.api_keys.visual_crossing_key,
            'unitGroup': 'metric',
            'include': 'days',
            'elements': ','.join(elements),
            'contentType': 'json',
        }

        try:
            logger.info(f"Fetching Visual Crossing data for {start_date} to {end_date}")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            days_data = []

            for day in data['days']:
                days_data.append({
                    'date': day['datetime'],
                    'temp_avg': day.get('temp'),
                    'humidity': day.get('humidity'),
                    'precip_mm': day.get('precip', 0),
                    'preciptype': day.get('preciptype'),
                    'windspeed_ms': day.get('windspeed', 0) * 0.277778,  # km/h to m/s
                    'cloudcover': day.get('cloudcover'),
                    'solar_radiation': day.get('solarradiation'),
                    'solar_energy_kwh_m2': day.get('solarenergy'),
                    'conditions': day.get('conditions'),
                })

            df = pd.DataFrame(days_data)
            df['date'] = pd.to_datetime(df['date'])

            # Add workability assessment
            df['workable_day'] = df.apply(self._assess_workability, axis=1)

            if self.config.app.cache_enabled:
                self._save_to_cache(cache_key, df)

            logger.info(f"Successfully fetched {len(df)} days of weather data")
            return df

        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"Visual Crossing API error: {e}")

    def get_weather_forecast(
        self,
        lat: float,
        lon: float,
        days: int = 7
    ) -> pd.DataFrame:
        """
        Get weather forecast from Visual Crossing

        Args:
            lat, lon: Coordinates
            days: Number of days to forecast (1-15)

        Returns:
            DataFrame with daily forecast
        """
        today = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')

        return self.get_historical_weather(lat, lon, today, end_date, include_solar=True)

    # ========== OPENWEATHERMAP METHODS ==========

    def get_current_conditions(
        self,
        lat: float,
        lon: float
    ) -> Dict:
        """
        Get current weather conditions from OpenWeatherMap

        Args:
            lat, lon: Coordinates

        Returns:
            Dictionary with current conditions
        """
        url = "https://api.openweathermap.org/data/2.5/weather"  # Using 2.5 API (free tier)

        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_keys.openweather_key,
            'units': 'metric',
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            return {
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data['wind']['speed'],
                'wind_deg': data['wind'].get('deg'),
                'cloudiness': data['clouds']['all'],
                'conditions': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'visibility': data.get('visibility'),
                'rain_1h': data.get('rain', {}).get('1h', 0),
                'snow_1h': data.get('snow', {}).get('1h', 0),
                'timestamp': datetime.fromtimestamp(data['dt']),
                'safe_for_work': self._assess_safety(data),
            }

        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"OpenWeatherMap API error: {e}")

    # ========== UTILITY METHODS ==========

    def _assess_workability(self, row: pd.Series) -> bool:
        """
        Determine if a day is suitable for construction work

        Args:
            row: DataFrame row with weather data

        Returns:
            True if workable, False otherwise
        """
        precip = row.get('precip_mm', 0)
        windspeed = row.get('windspeed_ms', 0)
        temp = row.get('temp_avg', 20)

        if precip > WORKABILITY_THRESHOLDS['max_precipitation_mm']:
            return False
        if windspeed > WORKABILITY_THRESHOLDS['max_wind_speed_ms']:
            return False
        if temp < WORKABILITY_THRESHOLDS['min_temperature_c']:
            return False
        if temp > WORKABILITY_THRESHOLDS['max_temperature_c']:
            return False

        return True

    def _assess_safety(self, weather_data: Dict) -> bool:
        """
        Determine if current conditions are safe for outdoor work

        Args:
            weather_data: OpenWeatherMap data

        Returns:
            True if safe, False otherwise
        """
        wind_speed = weather_data['wind']['speed']
        rain = weather_data.get('rain', {}).get('1h', 0)
        temp = weather_data['main']['temp']

        if wind_speed > WORKABILITY_THRESHOLDS['max_wind_speed_ms']:
            return False
        if rain > 2:  # More than 2mm in last hour
            return False
        if temp < WORKABILITY_THRESHOLDS['min_temperature_c']:
            return False
        if temp > WORKABILITY_THRESHOLDS['max_temperature_c']:
            return False

        return True

    def _save_to_cache(self, key: str, data: pd.DataFrame):
        """Save data to cache"""
        try:
            cache_file = self._cache_dir / f"{key}.pkl"
            data.to_pickle(cache_file)
            logger.debug(f"Saved data to cache: {cache_file}")
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

    def _load_from_cache(
        self,
        key: str,
        max_age_hours: Optional[int] = None
    ) -> Optional[pd.DataFrame]:
        """Load data from cache if valid"""
        try:
            cache_file = self._cache_dir / f"{key}.pkl"

            if not cache_file.exists():
                return None

            # Check age
            if max_age_hours is not None:
                file_age = time.time() - cache_file.stat().st_mtime
                if file_age > max_age_hours * 3600:
                    logger.debug(f"Cache expired: {cache_file}")
                    return None

            data = pd.read_pickle(cache_file)
            logger.debug(f"Loaded data from cache: {cache_file}")
            return data

        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            return None

    def download_epw_file(
        self,
        lat: float,
        lon: float,
        output_path: Optional[str] = None
    ) -> str:
        """
        Download EPW weather file for a location

        Args:
            lat, lon: Coordinates
            output_path: Path to save EPW file

        Returns:
            Path to downloaded EPW file
        """
        # This would integrate with climate.onebuilding.org or similar
        # For now, we'll use NSRDB data and note that EPW conversion would be needed
        logger.warning("EPW file download not fully implemented - use NSRDB CSV data")

        if output_path is None:
            output_path = f"weather_{lat}_{lon}.epw"

        # TODO: Implement EPW file download/conversion
        raise NotImplementedError("EPW file download coming soon")


class WeatherDataCache:
    """Simple disk-based cache for weather data"""

    def __init__(self, cache_dir: str = ".cache/weather"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str, max_age_seconds: Optional[int] = None) -> Optional[any]:
        """Get item from cache"""
        cache_file = self.cache_dir / f"{key}.json"

        if not cache_file.exists():
            return None

        if max_age_seconds:
            age = time.time() - cache_file.stat().st_mtime
            if age > max_age_seconds:
                return None

        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except:
            return None

    def set(self, key: str, value: any):
        """Set item in cache"""
        cache_file = self.cache_dir / f"{key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(value, f)
        except Exception as e:
            logger.warning(f"Failed to cache data: {e}")
