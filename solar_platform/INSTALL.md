# Installation Guide
Solar Project Management Platform

## Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- pip package manager
- Git
- RADIANCE (optional, for bifacial modeling)

### 2. Install Bifacial Radiance

From the parent directory:

```bash
cd /path/to/bifacial_radiance
pip install -e .
```

### 3. Install Platform Dependencies

```bash
cd solar_platform
pip install -r requirements.txt
```

### 4. Configure API Keys

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```
NREL_API_KEY=your_key_here
VISUAL_CROSSING_KEY=your_key_here
OPENWEATHER_KEY=your_key_here
```

### 5. Initialize Database

```bash
python -c "from utils.database import init_db; init_db()"
```

### 6. Run the Application

```bash
streamlit run app.py
```

Navigate to `http://localhost:8501` in your browser.

## Detailed Installation

### API Key Registration

#### NREL Developer API (Free)
1. Visit https://developer.nrel.gov/signup/
2. Register with email
3. Copy API key to `.env`

#### Visual Crossing (Free tier: 1,000 records/day)
1. Visit https://www.visualcrossing.com/sign-up
2. Create free account
3. Copy API key to `.env`

#### OpenWeatherMap (Free tier: 1,000 calls/day)
1. Visit https://openweathermap.org/api
2. Sign up for free account
3. Copy API key to `.env`

### Optional: RADIANCE Installation

For bifacial modeling with bifacial_radiance:

**Linux:**
```bash
sudo apt-get install radiance
```

**macOS:**
```bash
brew install radiance
```

**Windows:**
Download from https://github.com/NREL/Radiance/releases

### Database Options

**Development (SQLite - Default):**
No additional setup required.

**Production (PostgreSQL):**
1. Install PostgreSQL
2. Create database:
   ```sql
   CREATE DATABASE solar_projects;
   ```
3. Update `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost/solar_projects
   ```

## Troubleshooting

### Import Errors

```bash
# Make sure bifacial_radiance is installed
pip install -e /path/to/bifacial_radiance

# Install missing dependencies
pip install -r requirements.txt
```

### API Key Issues

Check configuration:
```python
from config import get_config
config = get_config()
print(config.validate_api_keys())
```

### Database Errors

Reinitialize database:
```bash
python -c "from utils.database import drop_db, init_db; drop_db(); init_db()"
```

## Testing

Run tests:
```bash
pytest tests/
```

## Deployment

### Streamlit Cloud

1. Push to GitHub
2. Connect at https://streamlit.io/cloud
3. Add secrets in dashboard settings
4. Deploy

### Docker (Coming Soon)

Build and run:
```bash
docker-compose up
```

## Support

For issues, see README.md or contact the development team.
