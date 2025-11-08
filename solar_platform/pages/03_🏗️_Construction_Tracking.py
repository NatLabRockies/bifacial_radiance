"""
Construction Tracking Page - Weather monitoring and delay analysis
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_config
from modules.weather_service import WeatherService, WeatherAPIError
from modules.cost_analysis import ConstructionCostAnalyzer
from modules.visualization import SolarVisualizer

st.set_page_config(page_title="Construction Tracking", page_icon="🏗️", layout="wide")

config = get_config()
visualizer = SolarVisualizer()

# Check API keys
missing_keys = config.get_missing_keys()
if 'visual_crossing' in missing_keys and 'openweather' in missing_keys:
    st.warning("⚠️ Weather API keys recommended for full functionality. Configure in `.env` or secrets.")

weather_service = WeatherService()
cost_analyzer = ConstructionCostAnalyzer(weather_service)

st.title("🏗️ Construction Weather Tracking")
st.markdown("Monitor weather conditions, track delays, and analyze cost impacts during construction")

# Tabs
tab1, tab2, tab3 = st.tabs(["🌦️ Current Conditions", "📊 Historical Analysis", "💰 Cost Impact"])

with tab1:
    st.header("Real-Time Site Conditions")

    col1, col2 = st.columns(2)

    with col1:
        rt_lat = st.number_input("Site Latitude", -90.0, 90.0, 37.5, format="%.6f", key="rt_lat")
        rt_lon = st.number_input("Site Longitude", -180.0, 180.0, -77.6, format="%.6f", key="rt_lon")

    with col2:
        if st.button("🔄 Get Current Conditions", type="primary"):
            if 'openweather' not in missing_keys:
                with st.spinner("Fetching current weather..."):
                    try:
                        conditions = weather_service.get_current_conditions(rt_lat, rt_lon)

                        st.success(f"📍 Current conditions at {rt_lat:.4f}, {rt_lon:.4f}")

                        # Display metrics
                        cond_col1, cond_col2, cond_col3, cond_col4 = st.columns(4)

                        with cond_col1:
                            st.metric("Temperature", f"{conditions['temperature']:.1f}°C")

                        with cond_col2:
                            st.metric("Wind Speed", f"{conditions['wind_speed']:.1f} m/s")

                        with cond_col3:
                            st.metric("Humidity", f"{conditions['humidity']}%")

                        with cond_col4:
                            st.metric("Conditions", conditions['conditions'].title())

                        # Safety assessment
                        if conditions['safe_for_work']:
                            st.success("✅ **CONDITIONS SAFE FOR OUTDOOR WORK**")
                        else:
                            st.error("⚠️ **UNSAFE CONDITIONS - CONSIDER SUSPENDING WORK**")

                            # Explain why unsafe
                            reasons = []
                            if conditions['wind_speed'] > 15:
                                reasons.append(f"High winds ({conditions['wind_speed']:.1f} m/s)")
                            if conditions['rain_1h'] > 2:
                                reasons.append(f"Heavy rain ({conditions['rain_1h']:.1f} mm/hr)")
                            if conditions['temperature'] < -10:
                                reasons.append(f"Extreme cold ({conditions['temperature']:.1f}°C)")
                            if conditions['temperature'] > 40:
                                reasons.append(f"Extreme heat ({conditions['temperature']:.1f}°C)")

                            if reasons:
                                st.warning("**Unsafe factors:**\n- " + "\n- ".join(reasons))

                        # Detailed conditions
                        with st.expander("📋 Detailed Conditions"):
                            detail_col1, detail_col2 = st.columns(2)

                            with detail_col1:
                                st.write(f"**Feels Like:** {conditions['feels_like']:.1f}°C")
                                st.write(f"**Pressure:** {conditions['pressure']} hPa")
                                st.write(f"**Cloud Cover:** {conditions['cloudiness']}%")

                            with detail_col2:
                                if conditions.get('wind_deg'):
                                    st.write(f"**Wind Direction:** {conditions['wind_deg']}°")
                                if conditions.get('visibility'):
                                    st.write(f"**Visibility:** {conditions['visibility']/1000:.1f} km")
                                st.write(f"**Updated:** {conditions['timestamp'].strftime('%Y-%m-%d %H:%M')}")

                    except WeatherAPIError as e:
                        st.error(f"Error fetching weather: {e}")
            else:
                st.error("OpenWeatherMap API key required for real-time conditions")

with tab2:
    st.header("Historical Weather Analysis")

    # Project/date selection
    col1, col2, col3 = st.columns(3)

    with col1:
        hist_lat = st.number_input("Site Latitude", -90.0, 90.0, 37.5, format="%.6f", key="hist_lat")
        hist_lon = st.number_input("Site Longitude", -180.0, 180.0, -77.6, format="%.6f", key="hist_lon")

    with col2:
        start_date = st.date_input(
            "Construction Start Date",
            value=datetime.now() - timedelta(days=90),
            max_value=datetime.now()
        )

    with col3:
        end_date = st.date_input(
            "Analysis End Date",
            value=datetime.now(),
            max_value=datetime.now()
        )

    if st.button("📊 Analyze Weather History", type="primary"):
        if 'visual_crossing' not in missing_keys:
            with st.spinner("Analyzing weather data..."):
                try:
                    weather_data = weather_service.get_historical_weather(
                        hist_lat,
                        hist_lon,
                        start_date.strftime('%Y-%m-%d'),
                        end_date.strftime('%Y-%m-%d'),
                        include_solar=True
                    )

                    st.success(f"✅ Analyzed {len(weather_data)} days of weather data")

                    # Summary metrics
                    total_days = len(weather_data)
                    workable_days = weather_data['workable_day'].sum()
                    delay_days = total_days - workable_days

                    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

                    with metric_col1:
                        st.metric("Total Days", total_days)

                    with metric_col2:
                        st.metric("Workable Days", int(workable_days))

                    with metric_col3:
                        st.metric(
                            "Weather Delays",
                            int(delay_days),
                            delta=f"-{delay_days/total_days*100:.0f}%",
                            delta_color="inverse"
                        )

                    with metric_col4:
                        st.metric(
                            "Workability",
                            f"{workable_days/total_days*100:.1f}%"
                        )

                    # Timeline chart
                    st.subheader("Construction Timeline")
                    timeline_fig = visualizer.plot_construction_timeline(weather_data)
                    st.plotly_chart(timeline_fig, use_container_width=True)

                    # Delay breakdown
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("Weather Summary")

                        summary_data = {
                            'Metric': [
                                'Total Precipitation',
                                'Average Temperature',
                                'Max Wind Speed',
                                'Days with Rain',
                            ],
                            'Value': [
                                f"{weather_data['precip_mm'].sum():.1f} mm",
                                f"{weather_data['temp_avg'].mean():.1f}°C",
                                f"{weather_data['windspeed_ms'].max():.1f} m/s",
                                f"{(weather_data['precip_mm'] > 0).sum()} days",
                            ]
                        }

                        st.dataframe(
                            pd.DataFrame(summary_data),
                            use_container_width=True,
                            hide_index=True
                        )

                    with col2:
                        st.subheader("Delay Factors")

                        unworkable = weather_data[~weather_data['workable_day']]
                        if len(unworkable) > 0:
                            precip_days = (unworkable['precip_mm'] > 5).sum()
                            wind_days = (unworkable['windspeed_ms'] > 15).sum()
                            temp_days = ((unworkable['temp_avg'] < -10) | (unworkable['temp_avg'] > 40)).sum()

                            delay_data = {
                                'Factor': ['Heavy Rain', 'High Winds', 'Extreme Temps'],
                                'Days': [int(precip_days), int(wind_days), int(temp_days)]
                            }

                            st.dataframe(
                                pd.DataFrame(delay_data),
                                use_container_width=True,
                                hide_index=True
                            )
                        else:
                            st.info("No weather delays during this period!")

                    # Download data
                    st.subheader("📥 Export Data")
                    csv = weather_data.to_csv(index=False)
                    st.download_button(
                        "Download Weather Data (CSV)",
                        data=csv,
                        file_name=f"weather_data_{start_date}_{end_date}.csv",
                        mime="text/csv"
                    )

                except WeatherAPIError as e:
                    st.error(f"Error fetching historical weather: {e}")
        else:
            st.error("Visual Crossing API key required for historical analysis")

with tab3:
    st.header("Cost Impact Analysis")

    st.markdown("""
    Calculate the financial impact of weather delays on your construction timeline.
    """)

    # Input section
    cost_col1, cost_col2 = st.columns(2)

    with cost_col1:
        st.subheader("Project Details")
        project_id = st.text_input("Project ID", value="SOLAR-001")
        cost_lat = st.number_input("Latitude", -90.0, 90.0, 37.5, format="%.6f", key="cost_lat")
        cost_lon = st.number_input("Longitude", -180.0, 180.0, -77.6, format="%.6f", key="cost_lon")

        cost_start = st.date_input(
            "Construction Start",
            value=datetime.now() - timedelta(days=90),
            key="cost_start"
        )
        cost_end = st.date_input(
            "Analysis End Date",
            value=datetime.now(),
            key="cost_end"
        )

    with cost_col2:
        st.subheader("Cost Assumptions")
        daily_crew = st.number_input("Daily Crew Cost ($)", 0, 50000, 5000, 500)
        daily_equipment = st.number_input("Daily Equipment Cost ($)", 0, 20000, 2000, 200)
        daily_overhead = st.number_input("Daily Overhead ($)", 0, 10000, 1000, 100)
        weekly_extended = st.number_input("Weekly Extended Overhead ($)", 0, 50000, 10000, 1000)

    if st.button("💰 Calculate Cost Impact", type="primary"):
        if 'visual_crossing' not in missing_keys:
            with st.spinner("Calculating cost impact..."):
                try:
                    cost_assumptions = {
                        'daily_crew_cost': daily_crew,
                        'daily_equipment_cost': daily_equipment,
                        'daily_overhead': daily_overhead,
                        'weekly_extended_overhead': weekly_extended,
                    }

                    impact = cost_analyzer.calculate_weather_delays(
                        project_id=project_id,
                        planned_start=cost_start.strftime('%Y-%m-%d'),
                        planned_end=cost_end.strftime('%Y-%m-%d'),
                        lat=cost_lat,
                        lon=cost_lon,
                        cost_assumptions=cost_assumptions,
                    )

                    st.success("✅ Cost analysis complete")

                    # Cost metrics
                    st.subheader("💵 Financial Impact")

                    impact_col1, impact_col2, impact_col3, impact_col4 = st.columns(4)

                    with impact_col1:
                        st.metric(
                            "Total Weather Impact",
                            f"${impact['cost_impact']['total_weather_impact']:,.0f}"
                        )

                    with impact_col2:
                        st.metric(
                            "Direct Delay Cost",
                            f"${impact['cost_impact']['direct_delay_cost']:,.0f}"
                        )

                    with impact_col3:
                        st.metric(
                            "Extended Timeline Cost",
                            f"${impact['cost_impact']['extended_timeline_cost']:,.0f}"
                        )

                    with impact_col4:
                        st.metric(
                            "Cost per Delay Day",
                            f"${impact['cost_impact']['cost_per_delay_day']:,.0f}"
                        )

                    # Detailed breakdown
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("Delay Summary")
                        delay_summary = {
                            'Metric': [
                                'Total Days',
                                'Workable Days',
                                'Weather Delays',
                                'Partial Productivity Days',
                                'Workability %',
                            ],
                            'Value': [
                                impact['analysis_period']['total_days'],
                                impact['delay_summary']['workable_days'],
                                impact['delay_summary']['delay_days'],
                                impact['delay_summary']['partial_productivity_days'],
                                f"{impact['delay_summary']['workability_percentage']:.1f}%",
                            ]
                        }
                        st.dataframe(pd.DataFrame(delay_summary), hide_index=True, use_container_width=True)

                    with col2:
                        st.subheader("Delay Categories")
                        breakdown = impact['delay_breakdown']
                        category_data = {
                            'Category': list(breakdown.keys()),
                            'Days': list(breakdown.values())
                        }
                        st.dataframe(pd.DataFrame(category_data), hide_index=True, use_container_width=True)

                    # Monthly breakdown
                    st.subheader("Monthly Workability")
                    monthly_summary = impact['monthly_summary']
                    st.dataframe(monthly_summary, use_container_width=True, hide_index=True)

                except Exception as e:
                    st.error(f"Error calculating cost impact: {e}")
        else:
            st.error("Visual Crossing API key required for cost analysis")

# Sidebar
st.sidebar.header("📊 Construction Metrics")
st.sidebar.info("""
**Workability Thresholds:**
- Max Precipitation: 5mm/day
- Max Wind Speed: 15 m/s
- Temperature Range: -10°C to 40°C

**Cost Components:**
- Direct delay costs (crew, equipment)
- Extended timeline overhead
- Partial productivity losses
""")

st.sidebar.markdown("---")
st.sidebar.header("💡 Tips")
st.sidebar.markdown("""
- Check conditions daily before work
- Review 7-day forecast for planning
- Document weather delays
- Track actual vs. planned timeline
""")
