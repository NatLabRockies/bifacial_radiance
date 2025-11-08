"""
String Sizing Page - Calculate optimal module strings for inverters
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.string_sizing import (
    StringSizer,
    COMMON_MODULES,
    COMMON_INVERTERS,
)
from modules.visualization import SolarVisualizer

st.set_page_config(page_title="String Sizing Calculator", page_icon="🔌", layout="wide")

visualizer = SolarVisualizer()

st.title("🔌 String Sizing Calculator")
st.markdown("""
Calculate the optimal number of PV modules per string based on module specifications,
inverter MPPT voltage windows, and site temperature conditions.
""")

# Create tabs
tab1, tab2, tab3 = st.tabs(["🔧 Quick Sizing", "⚙️ Custom Configuration", "📊 System Design"])

with tab1:
    st.header("Quick String Sizing")
    st.markdown("Use pre-configured modules and inverters for quick calculations")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Module Selection")
        module_preset = st.selectbox(
            "Select Module",
            list(COMMON_MODULES.keys()),
            help="Choose from common module types"
        )

        module_params = COMMON_MODULES[module_preset].copy()

        # Display module specs
        with st.expander("📋 Module Specifications"):
            spec_col1, spec_col2 = st.columns(2)
            with spec_col1:
                st.metric("Voc (STC)", f"{module_params['v_oc']} V")
                st.metric("Vmp (STC)", f"{module_params['v_mp']} V")
                st.metric("Isc (STC)", f"{module_params['i_sc']} A")
            with spec_col2:
                st.metric("Imp (STC)", f"{module_params['i_mp']} A")
                st.metric("Power (STC)", f"{module_params['v_mp'] * module_params['i_mp']:.0f} W")
                st.metric("Cells in Series", module_params['cells_in_series'])

    with col2:
        st.subheader("Inverter Selection")
        inverter_preset = st.selectbox(
            "Select Inverter",
            list(COMMON_INVERTERS.keys()),
            help="Choose from common inverter types"
        )

        inverter_params = COMMON_INVERTERS[inverter_preset].copy()

        # Display inverter specs
        with st.expander("📋 Inverter Specifications"):
            inv_col1, inv_col2 = st.columns(2)
            with inv_col1:
                st.metric("MPPT Min", f"{inverter_params['mppt_min_voltage']} V")
                st.metric("MPPT Max", f"{inverter_params['mppt_max_voltage']} V")
                st.metric("Vdc Max", f"{inverter_params['vdc_max']} V")
            with inv_col2:
                st.metric("Idc Max", f"{inverter_params['idc_max']} A")
                st.metric("Max DC Power", f"{inverter_params['max_power']/1000:.0f} kW")
                st.metric("AC Power", f"{inverter_params['ac_power']/1000:.0f} kW")

    # Site conditions
    st.subheader("Site Conditions")
    site_col1, site_col2, site_col3 = st.columns(3)

    with site_col1:
        min_temp = st.number_input(
            "Minimum Temperature (°C)",
            min_value=-40.0,
            max_value=40.0,
            value=-10.0,
            help="Coldest expected ambient temperature (NEC 690.7)"
        )

    with site_col2:
        max_temp = st.number_input(
            "Maximum Temperature (°C)",
            min_value=0.0,
            max_value=60.0,
            value=40.0,
            help="Hottest expected ambient temperature"
        )

    with site_col3:
        elevation = st.number_input(
            "Elevation (m)",
            min_value=0.0,
            max_value=5000.0,
            value=0.0,
            step=100.0,
            help="Site elevation above sea level"
        )

    site_params = {
        'min_temp': min_temp,
        'max_temp': max_temp,
        'elevation': elevation,
    }

    # Calculate button
    if st.button("🔢 Calculate String Size", type="primary"):
        try:
            sizer = StringSizer()

            results = sizer.calculate_string_size(
                module_params=module_params,
                inverter_params=inverter_params,
                site_params=site_params,
                safety_factor=1.0,
            )

            # Display results
            st.success("✅ String sizing calculation complete!")

            # Main metrics
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

            with metric_col1:
                st.metric(
                    "Minimum Modules",
                    results['min_modules_per_string'],
                    help="Minimum modules to stay above MPPT min voltage"
                )

            with metric_col2:
                st.metric(
                    "Maximum Modules",
                    results['max_modules_per_string'],
                    help="Maximum modules to stay below Vdc max"
                )

            with metric_col3:
                st.metric(
                    "Recommended",
                    results['recommended_modules_per_string'],
                    help="Recommended modules per string"
                )

            with metric_col4:
                range_pct = ((results['max_modules_per_string'] - results['min_modules_per_string']) /
                            results['recommended_modules_per_string'] * 100)
                st.metric(
                    "Range",
                    f"±{range_pct:.0f}%",
                    help="Flexibility in string configuration"
                )

            # Voltage analysis
            st.subheader("📊 Voltage Analysis")

            volt_col1, volt_col2 = st.columns(2)

            with volt_col1:
                st.markdown("**String Voltage at Different Conditions:**")

                voltage_data = {
                    'Condition': [
                        f'Voc at Cold ({min_temp}°C)',
                        'Voc at STC (25°C)',
                        f'Vmp at Cold ({min_temp}°C)',
                        'Vmp at STC (25°C)',
                        f'Vmp at Hot ({max_temp}°C)',
                    ],
                    f'{results["min_modules_per_string"]} Modules': [
                        f"{results['min_modules_per_string'] * results['voltages']['v_oc_cold']:.1f} V",
                        f"{results['min_modules_per_string'] * results['voltages']['v_oc_stc']:.1f} V",
                        f"{results['min_modules_per_string'] * results['voltages']['v_mp_cold']:.1f} V",
                        f"{results['min_modules_per_string'] * results['voltages']['v_mp_stc']:.1f} V",
                        f"{results['min_modules_per_string'] * results['voltages']['v_mp_hot']:.1f} V",
                    ],
                    f'{results["max_modules_per_string"]} Modules': [
                        f"{results['max_modules_per_string'] * results['voltages']['v_oc_cold']:.1f} V",
                        f"{results['max_modules_per_string'] * results['voltages']['v_oc_stc']:.1f} V",
                        f"{results['max_modules_per_string'] * results['voltages']['v_mp_cold']:.1f} V",
                        f"{results['max_modules_per_string'] * results['voltages']['v_mp_stc']:.1f} V",
                        f"{results['max_modules_per_string'] * results['voltages']['v_mp_hot']:.1f} V",
                    ],
                }

                st.dataframe(pd.DataFrame(voltage_data), hide_index=True, use_container_width=True)

            with volt_col2:
                st.markdown("**Inverter Voltage Limits:**")

                limit_data = {
                    'Parameter': [
                        'MPPT Minimum',
                        'MPPT Maximum',
                        'Absolute Max (Vdc)',
                        'Operating Range',
                    ],
                    'Value': [
                        f"{inverter_params['mppt_min_voltage']} V",
                        f"{inverter_params['mppt_max_voltage']} V",
                        f"{inverter_params['vdc_max']} V",
                        f"{inverter_params['mppt_max_voltage'] - inverter_params['mppt_min_voltage']} V",
                    ]
                }

                st.dataframe(pd.DataFrame(limit_data), hide_index=True, use_container_width=True)

                # Limiting factors
                st.markdown("**Limiting Factors:**")
                st.write(f"- **Max modules:** Limited by {results['limiting_factor_max']}")
                st.write(f"- **Min modules:** Limited by {results['limiting_factor_min']}")

            # Configuration table
            st.subheader("📋 All Valid Configurations")
            config_table = sizer.generate_configuration_table(
                module_params, inverter_params, site_params
            )

            if not config_table.empty:
                st.dataframe(config_table, hide_index=True, use_container_width=True)
            else:
                st.error("No valid configurations found!")

            # Warnings
            if results['warnings']:
                st.subheader("⚠️ Warnings")
                for warning in results['warnings']:
                    st.warning(warning)

        except Exception as e:
            st.error(f"Error calculating string size: {e}")
            st.exception(e)

with tab2:
    st.header("Custom Module & Inverter Configuration")
    st.markdown("Enter custom module and inverter specifications")

    # Custom module inputs
    st.subheader("Module Specifications")
    mod_col1, mod_col2, mod_col3 = st.columns(3)

    with mod_col1:
        custom_voc = st.number_input("Voc (V)", 0.0, 100.0, 49.5, 0.1, key="custom_voc")
        custom_vmp = st.number_input("Vmp (V)", 0.0, 100.0, 41.7, 0.1, key="custom_vmp")

    with mod_col2:
        custom_isc = st.number_input("Isc (A)", 0.0, 20.0, 10.8, 0.1, key="custom_isc")
        custom_imp = st.number_input("Imp (A)", 0.0, 20.0, 9.6, 0.1, key="custom_imp")

    with mod_col3:
        custom_temp_voc = st.number_input("Temp Coeff Voc (%/°C)", -1.0, 0.0, -0.28, 0.01, key="custom_temp_voc")
        custom_temp_vmp = st.number_input("Temp Coeff Vmp (%/°C)", -1.0, 0.0, -0.37, 0.01, key="custom_temp_vmp")

    custom_module_params = {
        'v_oc': custom_voc,
        'v_mp': custom_vmp,
        'i_sc': custom_isc,
        'i_mp': custom_imp,
        'temp_coeff_v_oc': custom_temp_voc,
        'temp_coeff_v_mp': custom_temp_vmp,
        'cells_in_series': 144,
    }

    # Custom inverter inputs
    st.subheader("Inverter Specifications")
    inv_col1, inv_col2, inv_col3 = st.columns(3)

    with inv_col1:
        custom_mppt_min = st.number_input("MPPT Min (V)", 0, 2000, 450, 10, key="custom_mppt_min")
        custom_mppt_max = st.number_input("MPPT Max (V)", 0, 2000, 800, 10, key="custom_mppt_max")

    with inv_col2:
        custom_vdc_max = st.number_input("Vdc Max (V)", 0, 2000, 1000, 10, key="custom_vdc_max")
        custom_idc_max = st.number_input("Idc Max (A)", 0, 5000, 280, 10, key="custom_idc_max")

    with inv_col3:
        custom_max_power = st.number_input("Max DC Power (kW)", 0, 2000, 137, 1, key="custom_max_power") * 1000
        custom_ac_power = st.number_input("AC Power (kW)", 0, 2000, 100, 1, key="custom_ac_power") * 1000

    custom_inverter_params = {
        'mppt_min_voltage': custom_mppt_min,
        'mppt_max_voltage': custom_mppt_max,
        'vdc_max': custom_vdc_max,
        'idc_max': custom_idc_max,
        'max_power': custom_max_power,
        'ac_power': custom_ac_power,
    }

    # Site conditions for custom
    st.subheader("Site Conditions")
    custom_site_col1, custom_site_col2, custom_site_col3 = st.columns(3)

    with custom_site_col1:
        custom_min_temp = st.number_input("Min Temp (°C)", -40.0, 40.0, -10.0, key="custom_min_temp")

    with custom_site_col2:
        custom_max_temp = st.number_input("Max Temp (°C)", 0.0, 60.0, 40.0, key="custom_max_temp")

    with custom_site_col3:
        custom_elevation = st.number_input("Elevation (m)", 0.0, 5000.0, 0.0, 100.0, key="custom_elevation")

    custom_site_params = {
        'min_temp': custom_min_temp,
        'max_temp': custom_max_temp,
        'elevation': custom_elevation,
    }

    if st.button("🔢 Calculate Custom Configuration", type="primary", key="custom_calc"):
        try:
            sizer = StringSizer()

            results = sizer.calculate_string_size(
                module_params=custom_module_params,
                inverter_params=custom_inverter_params,
                site_params=custom_site_params,
            )

            st.success("✅ Custom calculation complete!")

            # Display same results as tab 1
            result_col1, result_col2, result_col3 = st.columns(3)

            with result_col1:
                st.metric("Min Modules", results['min_modules_per_string'])

            with result_col2:
                st.metric("Max Modules", results['max_modules_per_string'])

            with result_col3:
                st.metric("Recommended", results['recommended_modules_per_string'])

            # Configuration table
            config_table = sizer.generate_configuration_table(
                custom_module_params, custom_inverter_params, custom_site_params
            )

            if not config_table.empty:
                st.subheader("Valid Configurations")
                st.dataframe(config_table, hide_index=True, use_container_width=True)

            if results['warnings']:
                for warning in results['warnings']:
                    st.warning(warning)

        except Exception as e:
            st.error(f"Error: {e}")

with tab3:
    st.header("Complete System Design")
    st.markdown("Design a complete system with multiple inverters")

    # System size input
    design_col1, design_col2 = st.columns(2)

    with design_col1:
        target_size_kw = st.number_input(
            "Target System Size (kW DC)",
            min_value=10.0,
            max_value=100000.0,
            value=5000.0,
            step=100.0,
            help="Total DC system capacity"
        )

        design_module = st.selectbox(
            "Module Type",
            list(COMMON_MODULES.keys()),
            key="design_module"
        )

    with design_col2:
        design_inverter = st.selectbox(
            "Inverter Type",
            list(COMMON_INVERTERS.keys()),
            key="design_inverter"
        )

        fixed_modules_per_string = st.number_input(
            "Modules per String (0=auto)",
            min_value=0,
            max_value=50,
            value=0,
            help="Leave at 0 for automatic calculation"
        )

    # Site params
    design_site_col1, design_site_col2 = st.columns(2)

    with design_site_col1:
        design_min_temp = st.number_input("Min Temp (°C)", -40.0, 40.0, -10.0, key="design_min_temp")
        design_max_temp = st.number_input("Max Temp (°C)", 0.0, 60.0, 40.0, key="design_max_temp")

    with design_site_col2:
        design_elevation = st.number_input("Elevation (m)", 0.0, 5000.0, 0.0, 100.0, key="design_elevation")

    if st.button("🏗️ Design Complete System", type="primary"):
        try:
            sizer = StringSizer()

            design_module_params = COMMON_MODULES[design_module]
            design_inverter_params = COMMON_INVERTERS[design_inverter]
            design_site_params = {
                'min_temp': design_min_temp,
                'max_temp': design_max_temp,
                'elevation': design_elevation,
            }

            modules_per_string = fixed_modules_per_string if fixed_modules_per_string > 0 else None

            config = sizer.calculate_system_configuration(
                system_size_kw=target_size_kw,
                module_params=design_module_params,
                inverter_params=design_inverter_params,
                site_params=design_site_params,
                modules_per_string=modules_per_string,
            )

            if 'error' in config:
                st.error(config['error'])
            else:
                st.success("✅ System design complete!")

                # System summary
                st.subheader("📊 System Configuration")

                sys_col1, sys_col2, sys_col3, sys_col4 = st.columns(4)

                sys_config = config['system_configuration']

                with sys_col1:
                    st.metric("Total Modules", f"{sys_config['total_modules']:,}")
                    st.metric("Modules per String", sys_config['modules_per_string'])

                with sys_col2:
                    st.metric("Total Strings", sys_config['total_strings'])
                    st.metric("Number of Inverters", sys_config['num_inverters'])

                with sys_col3:
                    st.metric("Actual System Size", f"{sys_config['actual_size_kw']:,.1f} kW")
                    st.metric("DC:AC Ratio", f"{sys_config['dc_ac_ratio']:.2f}")

                with sys_col4:
                    st.metric("Strings per Inverter", sys_config['strings_per_inverter'])
                    if sys_config['extra_strings'] > 0:
                        st.info(f"+{sys_config['extra_strings']} inverter(s) with extra string")

                # Power summary
                st.subheader("⚡ Power Summary")

                power_summary = config['power_summary']

                power_col1, power_col2, power_col3 = st.columns(3)

                with power_col1:
                    st.metric("Module Power", f"{power_summary['module_power_w']:.0f} W")

                with power_col2:
                    st.metric("String Power", f"{power_summary['string_power_w']/1000:.1f} kW")

                with power_col3:
                    st.metric("Total DC Power", f"{power_summary['total_dc_power_kw']:,.1f} kW")

                # Detailed breakdown
                st.subheader("📋 System Details")

                detail_data = {
                    'Parameter': [
                        'Target Size',
                        'Actual Size',
                        'Total Modules',
                        'Modules per String',
                        'Total Strings',
                        'Number of Inverters',
                        'Strings per Inverter (typical)',
                        'String Power (STC)',
                        'Total DC Power',
                        'Total AC Power',
                        'DC:AC Ratio',
                    ],
                    'Value': [
                        f"{sys_config['target_size_kw']:,.0f} kW",
                        f"{sys_config['actual_size_kw']:,.1f} kW",
                        f"{sys_config['total_modules']:,}",
                        sys_config['modules_per_string'],
                        sys_config['total_strings'],
                        sys_config['num_inverters'],
                        sys_config['strings_per_inverter'],
                        f"{power_summary['string_power_w']/1000:.2f} kW",
                        f"{power_summary['total_dc_power_kw']:,.1f} kW",
                        f"{power_summary['total_ac_power_kw']:,.1f} kW",
                        f"{sys_config['dc_ac_ratio']:.2f}",
                    ]
                }

                st.dataframe(pd.DataFrame(detail_data), hide_index=True, use_container_width=True)

        except Exception as e:
            st.error(f"Error designing system: {e}")
            st.exception(e)

# Sidebar
st.sidebar.header("📘 String Sizing Guide")
st.sidebar.markdown("""
**String sizing** determines how many solar modules can be connected in series based on:

**Voltage Constraints:**
- **MPPT Min**: Minimum voltage for inverter to operate
- **MPPT Max**: Maximum voltage in normal operation
- **Vdc Max**: Absolute maximum voltage (NEC 690.7)

**Temperature Effects:**
- **Cold**: Voltage increases (Voc limit)
- **Hot**: Voltage decreases (MPPT min limit)

**Key Formulas:**
- Max modules = Vdc_max / Voc_cold
- Min modules = MPPT_min / Vmp_hot

**NEC 690.7:**
Must calculate Voc at lowest expected temperature, including elevation correction.
""")

st.sidebar.markdown("---")
st.sidebar.header("💡 Tips")
st.sidebar.markdown("""
- Use mid-range configurations for flexibility
- Account for local temperature extremes
- Verify current limits for parallel strings
- Consider DC:AC ratio (typically 1.2-1.3)
- Check inverter datasheet for exact specs
""")
