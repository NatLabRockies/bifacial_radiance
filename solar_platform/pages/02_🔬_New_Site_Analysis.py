"""
New Site Analysis Page - Solar resource assessment and performance modeling
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_config
from modules.weather_service import WeatherService, WeatherAPIError
from modules.visualization import SolarVisualizer

st.set_page_config(page_title="New Site Analysis", page_icon="🔬", layout="wide")

config = get_config()
visualizer = SolarVisualizer()

# Check if API keys are configured
missing_keys = config.get_missing_keys()
if 'nrel' in missing_keys:
    st.error("⚠️ NREL API key is required for site analysis. Please configure in `.env` or Streamlit secrets.")
    st.stop()

weather_service = WeatherService()

st.title("🔬 New Site Analysis")
st.markdown("Perform solar resource assessment and energy production estimates for new sites")

# Input section
st.header("📍 Site Configuration")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Location")
    latitude = st.number_input(
        "Latitude",
        min_value=-90.0,
        max_value=90.0,
        value=37.5,
        format="%.6f",
        help="Site latitude in decimal degrees"
    )
    longitude = st.number_input(
        "Longitude",
        min_value=-180.0,
        max_value=180.0,
        value=-77.6,
        format="%.6f",
        help="Site longitude in decimal degrees"
    )

    location_name = st.text_input("Location Name (optional)", value="Richmond, VA")

with col2:
    st.subheader("System Configuration")
    system_capacity = st.number_input(
        "System Capacity (kW DC)",
        min_value=10.0,
        max_value=1000000.0,
        value=5000.0,
        step=100.0,
        help="DC system size in kilowatts"
    )

    system_type = st.selectbox(
        "System Type",
        ["Fixed Tilt", "Single-Axis Tracking", "Bifacial Fixed Tilt"],
        help="Select array type"
    )

# Advanced settings in expander
with st.expander("⚙️ Advanced Settings"):
    adv_col1, adv_col2 = st.columns(2)

    with adv_col1:
        if system_type == "Fixed Tilt":
            tilt = st.slider("Tilt Angle (degrees)", 0, 90, int(abs(latitude)), help="Module tilt angle")
            azimuth = st.slider("Azimuth (degrees)", 0, 360, 180, help="180 = South")
            array_type = 0
        else:
            tilt = abs(latitude)
            azimuth = 180
            array_type = 1
            st.info("Tracking system: Tilt and azimuth auto-configured")

    with adv_col2:
        module_type = st.selectbox("Module Type", ["Standard", "Premium", "Thin Film"], index=1)
        module_type_code = {"Standard": 0, "Premium": 1, "Thin Film": 2}[module_type]

        losses = st.slider("System Losses (%)", 5, 30, 14, help="Total system losses")
        dc_ac_ratio = st.number_input("DC/AC Ratio", 1.0, 2.0, 1.2, 0.1, help="Inverter loading ratio")

# Run analysis button
st.markdown("---")
if st.button("🚀 Run Performance Analysis", type="primary"):
    with st.spinner("Fetching solar resource data and running analysis..."):
        try:
            # Get PVWatts estimate
            results = weather_service.estimate_annual_production(
                system_capacity_kw=system_capacity,
                lat=latitude,
                lon=longitude,
                tilt=tilt,
                azimuth=azimuth,
                array_type=array_type,
                module_type=module_type_code,
                losses=losses,
                dc_ac_ratio=dc_ac_ratio,
            )

            st.success("✅ Analysis complete!")

            # Results section
            st.header("📊 Analysis Results")

            # Key metrics
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

            with metric_col1:
                st.metric(
                    "Annual Production",
                    f"{results['annual_ac_kwh']:,.0f} kWh",
                    help="Estimated annual AC energy production"
                )

            with metric_col2:
                st.metric(
                    "Capacity Factor",
                    f"{results['capacity_factor']:.1f}%",
                    help="Ratio of actual to theoretical maximum output"
                )

            with metric_col3:
                specific_yield = results['annual_ac_kwh'] / system_capacity
                st.metric(
                    "Specific Yield",
                    f"{specific_yield:,.0f} kWh/kW",
                    help="Annual production per kW installed"
                )

            with metric_col4:
                st.metric(
                    "Solar Resource",
                    f"{results['solrad_annual']:.1f} kWh/m²/day",
                    help="Average daily solar radiation on array"
                )

            # Monthly production chart
            st.subheader("Monthly Energy Production")
            monthly_fig = visualizer.plot_monthly_production(
                results['monthly_ac_kwh'],
                title=f"Monthly AC Energy Production - {location_name}"
            )
            st.plotly_chart(monthly_fig, use_container_width=True)

            # Detailed results
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Monthly Summary")
                months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

                monthly_df = pd.DataFrame({
                    'Month': months,
                    'AC Energy (kWh)': [f"{val:,.0f}" for val in results['monthly_ac_kwh']],
                    'Solar Resource (kWh/m²)': [f"{val:.1f}" for val in results['solrad_monthly']],
                    'POA Irradiance (kWh/m²)': [f"{val:.1f}" for val in results['poa_monthly']],
                })

                st.dataframe(monthly_df, use_container_width=True, hide_index=True)

            with col2:
                st.subheader("System Configuration")
                config_data = {
                    'Parameter': [
                        'System Capacity',
                        'System Type',
                        'Module Type',
                        'Tilt Angle',
                        'Azimuth',
                        'DC/AC Ratio',
                        'System Losses',
                        'Location',
                    ],
                    'Value': [
                        f"{system_capacity:,.0f} kW DC",
                        system_type,
                        module_type,
                        f"{tilt}°",
                        f"{azimuth}° ({('North' if azimuth < 45 or azimuth > 315 else 'East' if azimuth < 135 else 'South' if azimuth < 225 else 'West')})",
                        f"{dc_ac_ratio:.2f}",
                        f"{losses}%",
                        f"{latitude:.4f}, {longitude:.4f}",
                    ]
                }
                st.dataframe(pd.DataFrame(config_data), use_container_width=True, hide_index=True)

            # Financial quick estimate
            st.markdown("---")
            st.subheader("💰 Quick Financial Estimate")

            fin_col1, fin_col2, fin_col3 = st.columns(3)

            with fin_col1:
                install_cost_per_watt = st.number_input(
                    "Installed Cost ($/W DC)",
                    min_value=0.5,
                    max_value=5.0,
                    value=1.35,
                    step=0.05,
                    help="Total installed cost per watt"
                )

            with fin_col2:
                ppa_price = st.number_input(
                    "PPA Price ($/kWh)",
                    min_value=0.01,
                    max_value=0.50,
                    value=0.07,
                    step=0.01,
                    format="%.3f",
                    help="Power purchase agreement price"
                )

            with fin_col3:
                om_cost_per_kw = st.number_input(
                    "O&M Cost ($/kW/year)",
                    min_value=0.0,
                    max_value=50.0,
                    value=20.0,
                    step=5.0,
                    help="Annual operations and maintenance cost"
                )

            # Calculate financial metrics
            total_cost = system_capacity * 1000 * install_cost_per_watt
            annual_revenue = results['annual_ac_kwh'] * ppa_price
            annual_om_cost = system_capacity * om_cost_per_kw
            annual_net = annual_revenue - annual_om_cost

            # Simple LCOE
            degradation = 0.005
            discount_rate = 0.055
            lifetime = 25
            years = np.arange(1, lifetime + 1)
            production = results['annual_ac_kwh'] * (1 - degradation) ** (years - 1)
            discounts = 1 / (1 + discount_rate) ** years
            total_energy_pv = (production * discounts).sum()
            om_pv = (annual_om_cost * discounts).sum()
            lcoe = (total_cost + om_pv) / total_energy_pv

            fin_result_col1, fin_result_col2, fin_result_col3, fin_result_col4 = st.columns(4)

            with fin_result_col1:
                st.metric("Total Installed Cost", f"${total_cost:,.0f}")

            with fin_result_col2:
                st.metric("First Year Revenue", f"${annual_revenue:,.0f}")

            with fin_result_col3:
                simple_payback = total_cost / annual_net if annual_net > 0 else None
                st.metric("Simple Payback", f"{simple_payback:.1f} years" if simple_payback else "N/A")

            with fin_result_col4:
                st.metric("LCOE (Estimated)", f"${lcoe:.3f}/kWh")

            # Export results
            st.markdown("---")
            st.subheader("📥 Export Results")

            export_col1, export_col2 = st.columns(2)

            with export_col1:
                # Prepare CSV export
                export_df = monthly_df.copy()
                export_df['System_Capacity_kW'] = system_capacity
                export_df['Annual_Production_kWh'] = results['annual_ac_kwh']
                export_df['Capacity_Factor'] = results['capacity_factor']

                csv = export_df.to_csv(index=False)
                st.download_button(
                    label="📄 Download CSV Report",
                    data=csv,
                    file_name=f"solar_analysis_{location_name.replace(' ', '_')}_{latitude}_{longitude}.csv",
                    mime="text/csv"
                )

            with export_col2:
                if st.button("💾 Save to Project Database"):
                    st.info("🚧 Save to project feature coming soon! Use 'Project Overview' to create project first.")

        except WeatherAPIError as e:
            st.error(f"❌ API Error: {e}")
            st.info("Please check your API key configuration and try again.")

        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            st.exception(e)

# Help section
st.sidebar.header("💡 Quick Tips")
st.sidebar.info("""
**Solar Resource Assessment:**

1. Enter site coordinates
2. Configure system parameters
3. Click "Run Performance Analysis"
4. Review results and export

**System Types:**
- **Fixed Tilt**: Stationary modules
- **Single-Axis**: East-west tracking
- **Bifacial**: Rear-side production

**Metrics:**
- **Capacity Factor**: Higher is better (typical: 15-25%)
- **Specific Yield**: kWh per kW installed
- **LCOE**: Cost per kWh over project life
""")

st.sidebar.markdown("---")
st.sidebar.header("📚 Resources")
st.sidebar.markdown("""
- [PVWatts Calculator](https://pvwatts.nrel.gov/)
- [NSRDB Data](https://nsrdb.nrel.gov/)
- [NREL API Docs](https://developer.nrel.gov/docs/)
""")
