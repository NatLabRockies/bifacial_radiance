# Solar Project Management Platform

A comprehensive Streamlit-based platform for utility-scale solar project management, integrating weather data, performance modeling, construction tracking, and cost analysis.

## 🌟 Features

### Design Phase
- **Solar Resource Assessment** - NREL NSRDB integration for TMY data
- **Performance Modeling** - PVWatts and PySAM integration for energy estimates
- **Bifacial Analysis** - Full bifacial_radiance integration for advanced modeling
- **System Optimization** - Tilt, azimuth, and row spacing optimization
- **AgriPV Designer** - Specialized tools for agrivoltaic systems

### Construction Phase
- **Real-time Weather Monitoring** - OpenWeatherMap integration
- **Historical Weather Tracking** - Visual Crossing API for delay analysis
- **Weather Impact Analysis** - Automatic workability assessment
- **Cost Impact Calculation** - Weather delay cost tracking
- **Construction Timeline Management** - Forecast-based scheduling

### Operations Phase
- **Performance Monitoring** - Actual vs. predicted analysis
- **Weather-Normalized Performance** - PR ratio calculations
- **Anomaly Detection** - Underperformance alerts
- **Financial Tracking** - LCOE and ROI monitoring

## 📋 Prerequisites

### API Keys Required
- **NREL Developer API** (free): https://developer.nrel.gov/signup/
- **Visual Crossing Weather** (free tier available): https://www.visualcrossing.com/
- **OpenWeatherMap** (free tier available): https://openweathermap.org/api

### Software Dependencies
- Python 3.8+
- RADIANCE (for bifacial_radiance): https://github.com/NREL/Radiance/releases
- PostgreSQL (optional, for production deployment)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
cd solar_platform

# Install dependencies
pip install -r requirements.txt

# Install bifacial_radiance (from parent directory)
cd ..
pip install -e .
cd solar_platform
```

### 2. Configuration

Create a `.env` file with your API keys:

```bash
cp .env.example .env
# Edit .env with your actual API keys
```

Or use Streamlit secrets (`.streamlit/secrets.toml`):

```toml
[api_keys]
nrel_api_key = "your_nrel_key"
visual_crossing_key = "your_vc_key"
openweather_key = "your_ow_key"

[database]
db_url = "sqlite:///solar_projects.db"
```

### 3. Run the Application

```bash
streamlit run app.py
```

Navigate to `http://localhost:8501` in your browser.

## 📁 Project Structure

```
solar_platform/
├── app.py                          # Main Streamlit application
├── config.py                       # Configuration management
├── requirements.txt                # Python dependencies
├── modules/                        # Core modules
│   ├── weather_service.py         # Weather API integrations
│   ├── bifacial_wrapper.py        # bifacial_radiance wrapper
│   ├── data_management.py         # Database operations
│   ├── visualization.py           # Plotly charts and visualizations
│   ├── report_generator.py        # PDF report generation
│   └── cost_analysis.py           # Financial calculations
├── pages/                          # Streamlit pages
│   ├── 01_Project_Overview.py     # Portfolio dashboard
│   ├── 02_New_Site_Analysis.py    # Design tools
│   ├── 03_Design_Optimizer.py     # Optimization algorithms
│   ├── 04_Construction_Tracking.py# Construction monitoring
│   ├── 05_Operations_Monitor.py   # O&M dashboard
│   └── 06_AgriPV_Designer.py      # AgriPV tools
├── utils/                          # Utility functions
│   ├── database.py                # Database models
│   ├── calculations.py            # Engineering calculations
│   └── helpers.py                 # Helper functions
├── models/                         # Data models
│   └── schemas.py                 # Pydantic schemas
├── data/                           # Sample data
│   └── sample_projects.json
└── tests/                          # Unit tests
    └── test_weather_service.py
```

## 🔧 Configuration Options

### Weather Data Sources
Configure in `config.py`:

```python
WEATHER_CONFIG = {
    'design_phase': 'nsrdb',           # NREL NSRDB for TMY data
    'construction': 'visual_crossing',  # Visual Crossing for historical
    'operations': 'openweather',        # OpenWeather for real-time
    'cache_enabled': True,
    'cache_ttl_hours': 24
}
```

### Database Options
- **Development**: SQLite (default)
- **Production**: PostgreSQL (recommended)

## 📊 Usage Examples

### 1. Site Performance Estimate

```python
from modules.weather_service import WeatherService
from modules.bifacial_wrapper import BifacialSimulator

# Initialize services
weather = WeatherService(config)
sim = BifacialSimulator()

# Quick estimate
result = weather.estimate_annual_production(
    system_size_kw=5000,
    lat=37.5,
    lon=-77.6,
    tilt=25
)

print(f"Annual Production: {result['annual_ac_kwh']:,.0f} kWh")
print(f"Capacity Factor: {result['capacity_factor']:.1f}%")
```

### 2. Construction Weather Impact

```python
from modules.cost_analysis import ConstructionCostAnalyzer

analyzer = ConstructionCostAnalyzer(weather)

impact = analyzer.calculate_weather_delays(
    project_id='SOLAR-001',
    planned_start='2024-01-01',
    planned_end='2024-06-30',
    lat=37.5,
    lon=-77.6
)

print(f"Weather Delay Days: {impact['delay_days']}")
print(f"Cost Impact: ${impact['total_weather_impact']:,.0f}")
```

### 3. Bifacial Analysis

```python
from modules.bifacial_wrapper import BifacialSimulator

sim = BifacialSimulator()

# Run bifacial simulation
results = sim.run_fixed_tilt_simulation(
    lat=37.5,
    lon=-77.6,
    tilt=25,
    azimuth=180,
    module_type='bifacial_module',
    albedo=0.25,
    pitch=7.0,
    hub_height=2.0
)

print(f"Front Irradiance: {results['front_irradiance']:.1f} kWh/m²")
print(f"Rear Irradiance: {results['rear_irradiance']:.1f} kWh/m²")
print(f"Bifacial Gain: {results['bifacial_gain']:.1f}%")
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_weather_service.py

# Run with coverage
pytest --cov=modules tests/
```

## 📈 Performance Optimization

### Caching Strategy
- Weather data cached for 24 hours
- TMY data cached indefinitely (doesn't change)
- Simulation results cached by input parameters

### Database Optimization
- Indexes on project_id, location coordinates
- Periodic cleanup of old cache entries
- Connection pooling for concurrent users

## 🔐 Security Notes

- Never commit `.env` file with real API keys
- Use environment variables in production
- Implement rate limiting for API calls
- Sanitize user inputs for database queries

## 📚 Documentation

### Key Concepts

**EPW Files**: EnergyPlus Weather files containing hourly meteorological data including GHI, DNI, DHI, temperature, wind, etc.

**TMY Data**: Typical Meteorological Year - synthesized year of weather representing long-term conditions.

**Performance Ratio (PR)**: Actual energy output divided by theoretical maximum, accounting for losses.

**Weather-Normalized Performance**: Adjusting performance metrics to account for actual weather vs. typical year.

## 🤝 Contributing

This is an internal tool for review. See main platform repository for contribution guidelines.

## 📄 License

Proprietary - Internal Use Only

## 🙏 Acknowledgments

- NREL for bifacial_radiance and data APIs
- Visual Crossing for weather data access
- OpenWeatherMap for real-time data

## 📞 Support

For questions or issues, contact the development team.

---

**Version**: 1.0.0
**Last Updated**: 2024
**Status**: Development/Review
