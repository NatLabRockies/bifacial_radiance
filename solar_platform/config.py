"""
Configuration management for Solar Project Management Platform
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field

# Load environment variables
load_dotenv()

class APIKeys(BaseSettings):
    """API Keys configuration"""
    nrel_api_key: str = Field(default="", alias="NREL_API_KEY")
    visual_crossing_key: str = Field(default="", alias="VISUAL_CROSSING_KEY")
    openweather_key: str = Field(default="", alias="OPENWEATHER_KEY")
    noaa_token: Optional[str] = Field(default=None, alias="NOAA_TOKEN")

    class Config:
        env_file = ".env"
        case_sensitive = False


class DatabaseConfig(BaseSettings):
    """Database configuration"""
    database_url: str = Field(
        default="sqlite:///solar_projects.db",
        alias="DATABASE_URL"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False


class AppConfig(BaseSettings):
    """Application configuration"""
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Cache settings
    cache_enabled: bool = Field(default=True, alias="CACHE_ENABLED")
    cache_ttl_hours: int = Field(default=24, alias="CACHE_TTL_HOURS")
    cache_dir: str = Field(default=".cache", alias="CACHE_DIR")

    # Weather API configuration
    weather_primary_source: str = Field(default="nsrdb", alias="WEATHER_PRIMARY_SOURCE")
    weather_construction_source: str = Field(default="visual_crossing", alias="WEATHER_CONSTRUCTION_SOURCE")
    weather_realtime_source: str = Field(default="openweather", alias="WEATHER_REALTIME_SOURCE")

    # Rate limiting
    api_rate_limit_per_minute: int = Field(default=60, alias="API_RATE_LIMIT_PER_MINUTE")
    api_rate_limit_per_day: int = Field(default=10000, alias="API_RATE_LIMIT_PER_DAY")

    # Simulation defaults
    default_bifacial_ratio: float = Field(default=0.70, alias="DEFAULT_BIFACIAL_RATIO")
    default_system_losses: float = Field(default=14, alias="DEFAULT_SYSTEM_LOSSES")
    default_dc_ac_ratio: float = Field(default=1.2, alias="DEFAULT_DC_AC_RATIO")
    default_module_efficiency: float = Field(default=0.20, alias="DEFAULT_MODULE_EFFICIENCY")

    # File storage
    upload_folder: str = Field(default="uploads", alias="UPLOAD_FOLDER")
    report_folder: str = Field(default="reports", alias="REPORT_FOLDER")
    max_upload_size_mb: int = Field(default=100, alias="MAX_UPLOAD_SIZE_MB")

    # Feature flags
    enable_agripv: bool = Field(default=True, alias="ENABLE_AGRIPV")
    enable_cost_analysis: bool = Field(default=True, alias="ENABLE_COST_ANALYSIS")
    enable_weather_alerts: bool = Field(default=True, alias="ENABLE_WEATHER_ALERTS")
    enable_pdf_reports: bool = Field(default=True, alias="ENABLE_PDF_REPORTS")

    # External services
    radiance_bin_path: str = Field(default="/usr/local/radiance/bin", alias="RADIANCE_BIN_PATH")
    temp_simulation_dir: str = Field(default="/tmp/bifacial_radiance_sims", alias="TEMP_SIMULATION_DIR")

    # Performance settings
    max_concurrent_simulations: int = Field(default=3, alias="MAX_CONCURRENT_SIMULATIONS")
    simulation_timeout_seconds: int = Field(default=300, alias="SIMULATION_TIMEOUT_SECONDS")

    class Config:
        env_file = ".env"
        case_sensitive = False


class Config:
    """Main configuration class"""

    def __init__(self):
        self.api_keys = APIKeys()
        self.database = DatabaseConfig()
        self.app = AppConfig()

        # Create necessary directories
        self._ensure_directories()

    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.app.cache_dir,
            self.app.upload_folder,
            self.app.report_folder,
            self.app.temp_simulation_dir,
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.app.app_env.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.app.app_env.lower() == "development"

    def validate_api_keys(self) -> dict:
        """Validate that required API keys are present"""
        validation = {
            'nrel': bool(self.api_keys.nrel_api_key),
            'visual_crossing': bool(self.api_keys.visual_crossing_key),
            'openweather': bool(self.api_keys.openweather_key),
        }
        return validation

    def get_missing_keys(self) -> list:
        """Get list of missing API keys"""
        validation = self.validate_api_keys()
        return [key for key, valid in validation.items() if not valid]


# Singleton instance
config = Config()


def get_config() -> Config:
    """Get configuration instance"""
    return config


# Weather API URLs
NREL_NSRDB_BASE_URL = "https://developer.nrel.gov/api/nsrdb/v2/solar"
NREL_PVWATTS_BASE_URL = "https://developer.nrel.gov/api/pvwatts/v8.json"
VISUAL_CROSSING_BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"
NOAA_BASE_URL = "https://www.ncei.noaa.gov/access/services/data/v1"


# Construction workability thresholds
WORKABILITY_THRESHOLDS = {
    'max_precipitation_mm': 5.0,
    'max_wind_speed_ms': 15.0,  # ~34 mph
    'min_temperature_c': -10.0,
    'max_temperature_c': 40.0,
    'max_wind_speed_high_work_ms': 10.0,  # For elevated work
}


# Cost assumptions (can be overridden per project)
DEFAULT_COSTS = {
    'daily_crew_cost': 5000,
    'daily_equipment_cost': 2000,
    'daily_overhead': 1000,
    'weekly_extended_overhead': 10000,
}


# Module types for bifacial modeling
MODULE_TYPES = {
    'standard_mono': {
        'x': 1.0,  # width in meters
        'y': 2.0,  # height in meters
        'bifaciality': 0.0,
        'efficiency': 0.20,
    },
    'bifacial_mono': {
        'x': 1.0,
        'y': 2.0,
        'bifaciality': 0.70,
        'efficiency': 0.21,
    },
    'bifacial_perc': {
        'x': 1.0,
        'y': 2.0,
        'bifaciality': 0.75,
        'efficiency': 0.22,
    },
}


# System loss categories
SYSTEM_LOSSES = {
    'soiling': 2.0,
    'shading': 3.0,
    'snow': 0.0,
    'mismatch': 2.0,
    'wiring': 2.0,
    'connections': 0.5,
    'lid': 1.5,  # Light-induced degradation
    'nameplate': 1.0,
    'age': 0.0,
    'availability': 3.0,
}
