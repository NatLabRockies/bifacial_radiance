"""
Solar Project Management Platform
Main Streamlit Application

A comprehensive platform for utility-scale solar project management integrating:
- Weather data APIs (NREL, Visual Crossing, OpenWeatherMap)
- Performance modeling (PVWatts, PySAM, bifacial_radiance)
- Construction tracking and cost analysis
- Operations monitoring

Author: Solar Platform Team
Version: 1.0.0
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import get_config
from utils.database import init_db

# Page configuration
st.set_page_config(
    page_title="Solar Project Management Platform",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize configuration
config = get_config()

# Initialize database
@st.cache_resource
def initialize_database():
    """Initialize database on first run"""
    try:
        init_db()
        return True
    except Exception as e:
        st.error(f"Database initialization failed: {e}")
        return False

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .feature-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin-bottom: 1rem;
    }
    .metric-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

def main():
    """Main application entry point"""

    # Initialize database
    db_initialized = initialize_database()

    # Header
    st.markdown('<h1 class="main-header">☀️ Solar Project Management Platform</h1>', unsafe_allow_html=True)

    st.markdown("""
    ### Comprehensive Utility Solar Project Management

    Integrate weather data, performance modeling, construction tracking, and cost analysis
    throughout the entire project lifecycle - from design to operations.
    """)

    # Check API key configuration
    st.sidebar.header("⚙️ Configuration Status")

    missing_keys = config.get_missing_keys()

    if missing_keys:
        st.sidebar.warning(f"⚠️ Missing API keys: {', '.join(missing_keys)}")
        st.sidebar.info("Add your API keys to `.env` file or Streamlit secrets")
    else:
        st.sidebar.success("✅ All API keys configured")

    # Navigation guide
    st.sidebar.markdown("---")
    st.sidebar.header("📋 Navigation")
    st.sidebar.markdown("""
    **Design Phase:**
    - New Site Analysis
    - Design Optimizer
    - AgriPV Designer

    **Construction Phase:**
    - Construction Tracking
    - Weather Impact Analysis

    **Operations Phase:**
    - Operations Monitor
    - Performance Analytics

    **Management:**
    - Project Overview
    """)

    # Main content
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 🔬 Design Phase")
        st.markdown("""
        - **Solar Resource Assessment** - NREL NSRDB integration
        - **Performance Modeling** - PVWatts & PySAM
        - **Bifacial Analysis** - bifacial_radiance integration
        - **System Optimization** - Tilt, spacing, configuration
        - **AgriPV Tools** - Specialized agrivoltaic design
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 🏗️ Construction Phase")
        st.markdown("""
        - **Real-time Weather** - OpenWeatherMap integration
        - **Historical Tracking** - Visual Crossing API
        - **Workability Assessment** - Automated delay tracking
        - **Cost Impact Analysis** - Weather delay calculations
        - **Timeline Management** - Forecast-based scheduling
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### ⚡ Operations Phase")
        st.markdown("""
        - **Performance Monitoring** - Actual vs. predicted
        - **Weather Normalization** - PR ratio calculations
        - **Anomaly Detection** - Underperformance alerts
        - **Financial Tracking** - LCOE and ROI monitoring
        - **Portfolio Management** - Multi-project dashboard
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    # Quick Start Guide
    st.markdown("---")
    st.header("🚀 Quick Start Guide")

    tab1, tab2, tab3, tab4 = st.tabs(["📍 Prerequisites", "🔑 API Setup", "📊 Usage", "📚 Resources"])

    with tab1:
        st.markdown("""
        ### Prerequisites

        #### Software Requirements
        - **Python 3.8+** installed
        - **RADIANCE** for bifacial modeling: [Download](https://github.com/NREL/Radiance/releases)
        - **PostgreSQL** (optional, for production deployment)

        #### Python Dependencies
        All dependencies are listed in `requirements.txt`. Install with:
        ```bash
        pip install -r requirements.txt
        ```

        #### Key Packages
        - `streamlit` - Web application framework
        - `bifacial-radiance` - Bifacial PV modeling
        - `pvlib` - PV system modeling
        - `NREL-PySAM` - System Advisor Model
        - `plotly` - Interactive visualizations
        - `sqlalchemy` - Database ORM
        """)

    with tab2:
        st.markdown("""
        ### API Key Setup

        #### Required API Keys (All Free Tiers Available)

        **1. NREL Developer API** (Free)
        - Sign up: https://developer.nrel.gov/signup/
        - Provides: NSRDB solar data, PVWatts API
        - Limits: 1,000 requests/hour

        **2. Visual Crossing Weather** (Free tier: 1,000 records/day)
        - Sign up: https://www.visualcrossing.com/
        - Provides: Historical weather, forecasts
        - Free tier: 1,000 records/day

        **3. OpenWeatherMap** (Free tier: 1,000 calls/day)
        - Sign up: https://openweathermap.org/api
        - Provides: Real-time weather conditions
        - Free tier: 1,000 calls/day

        #### Configuration Methods

        **Option 1: .env File (Recommended for local)**
        ```bash
        cp .env.example .env
        # Edit .env with your actual API keys
        ```

        **Option 2: Streamlit Secrets (Recommended for deployment)**
        Create `.streamlit/secrets.toml`:
        ```toml
        [api_keys]
        nrel_api_key = "your_key_here"
        visual_crossing_key = "your_key_here"
        openweather_key = "your_key_here"
        ```
        """)

    with tab3:
        st.markdown("""
        ### Platform Usage

        #### Design Phase Workflow
        1. Navigate to **New Site Analysis**
        2. Enter site coordinates (latitude/longitude)
        3. Configure system parameters
        4. Run performance estimate with PVWatts
        5. Optional: Run detailed bifacial analysis
        6. Export results and reports

        #### Construction Phase Workflow
        1. Create project in **Project Overview**
        2. Navigate to **Construction Tracking**
        3. Monitor real-time weather conditions
        4. Track daily workability
        5. Analyze weather delay impacts
        6. Generate cost impact reports

        #### Operations Phase Workflow
        1. Upload production data in **Operations Monitor**
        2. Compare actual vs. predicted performance
        3. View weather-normalized PR ratios
        4. Identify underperformance issues
        5. Generate monthly/annual reports

        #### AgriPV Design Workflow
        1. Navigate to **AgriPV Designer**
        2. Define clearance height and crop type
        3. Optimize row spacing for dual use
        4. Analyze ground-level irradiance
        5. Calculate land use efficiency
        """)

    with tab4:
        st.markdown("""
        ### Resources & Documentation

        #### NREL Tools Documentation
        - [NSRDB Documentation](https://nsrdb.nrel.gov/)
        - [PVWatts API Docs](https://developer.nrel.gov/docs/solar/pvwatts/)
        - [bifacial_radiance Docs](https://bifacial-radiance.readthedocs.io/)
        - [PySAM Documentation](https://nrel-pysam.readthedocs.io/)

        #### Weather API Documentation
        - [Visual Crossing API](https://www.visualcrossing.com/resources/documentation/weather-api/)
        - [OpenWeatherMap API](https://openweathermap.org/api)
        - [NOAA CDO API](https://www.ncei.noaa.gov/support/access-data-service-api-user-documentation)

        #### Solar Industry Resources
        - [PVLIB Python](https://pvlib-python.readthedocs.io/)
        - [SAM Help](https://sam.nrel.gov/support.html)
        - [Solar Energy Research](https://www.nrel.gov/solar/)

        #### Platform Documentation
        See `README.md` in the `solar_platform/` directory for:
        - Installation guide
        - Configuration options
        - Code examples
        - Testing procedures
        """)

    # System Status
    st.markdown("---")
    st.header("🔧 System Status")

    status_col1, status_col2, status_col3, status_col4 = st.columns(4)

    with status_col1:
        st.metric("Database", "✅ Ready" if db_initialized else "❌ Error")

    with status_col2:
        api_status = len(missing_keys) == 0
        st.metric("API Keys", f"{'✅' if api_status else '⚠️'} {3 - len(missing_keys)}/3")

    with status_col3:
        st.metric("Environment", config.app.app_env.title())

    with status_col4:
        st.metric("Cache", "Enabled" if config.app.cache_enabled else "Disabled")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        Solar Project Management Platform v1.0.0 | Powered by NREL bifacial_radiance, PVWatts, and PySAM
        <br>
        <small>For support or questions, contact the development team</small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
