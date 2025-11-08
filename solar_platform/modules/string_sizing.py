"""
String Sizing Module - Calculate optimal module strings for inverters

Provides string sizing calculations based on:
- Module voltage/current characteristics
- Inverter voltage windows (MPPT range, Voc max, Vdc min)
- Temperature effects (NEC requirements)
- Multiple configuration options

Uses pvlib-python for calculations
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

try:
    import pvlib
    from pvlib import pvsystem, temperature
except ImportError:
    pvlib = None
    logging.warning("pvlib not installed - string sizing unavailable")

logger = logging.getLogger(__name__)


class StringSizer:
    """
    Calculate optimal string sizes for PV systems
    """

    def __init__(self):
        if pvlib is None:
            raise ImportError("pvlib-python required for string sizing. Install with: pip install pvlib")

    def calculate_string_size(
        self,
        module_params: Dict,
        inverter_params: Dict,
        site_params: Dict,
        safety_factor: float = 1.0,
    ) -> Dict:
        """
        Calculate min/max modules per string based on voltage constraints

        Args:
            module_params: Module specifications
                - v_oc: Open circuit voltage at STC (V)
                - v_mp: Voltage at max power at STC (V)
                - i_sc: Short circuit current at STC (A)
                - i_mp: Current at max power at STC (A)
                - temp_coeff_v_oc: Temperature coefficient of Voc (%/°C)
                - temp_coeff_v_mp: Temperature coefficient of Vmp (%/°C)
                - cells_in_series: Number of cells in series (typically 60, 72, 144)

            inverter_params: Inverter specifications
                - mppt_min_voltage: Minimum MPPT voltage (V)
                - mppt_max_voltage: Maximum MPPT voltage (V)
                - vdc_max: Maximum DC input voltage (V)
                - idc_max: Maximum DC input current (A)
                - max_power: Maximum DC power (W)

            site_params: Site environmental parameters
                - min_temp: Minimum expected temperature (°C)
                - max_temp: Maximum expected temperature (°C)
                - elevation: Site elevation (m)

            safety_factor: Voltage safety factor (default 1.0 = no extra margin)

        Returns:
            Dictionary with string sizing results
        """
        logger.info("Calculating string size...")

        # Extract parameters
        v_oc_stc = module_params['v_oc']
        v_mp_stc = module_params['v_mp']
        i_sc_stc = module_params['i_sc']
        i_mp_stc = module_params['i_mp']

        temp_coeff_voc = module_params.get('temp_coeff_v_oc', -0.29) / 100  # Convert %/°C to fraction
        temp_coeff_vmp = module_params.get('temp_coeff_v_mp', -0.35) / 100

        min_temp = site_params['min_temp']
        max_temp = site_params['max_temp']

        mppt_min = inverter_params['mppt_min_voltage']
        mppt_max = inverter_params['mppt_max_voltage']
        vdc_max = inverter_params['vdc_max']

        # Calculate voltage at minimum temperature (coldest - highest Voc)
        # Voc(T) = Voc(STC) * [1 + temp_coeff * (T - 25)]
        delta_t_cold = min_temp - 25
        v_oc_cold = v_oc_stc * (1 + temp_coeff_voc * delta_t_cold)

        # Calculate voltage at maximum temperature (hottest - lowest Vmp)
        delta_t_hot = max_temp - 25
        v_mp_hot = v_mp_stc * (1 + temp_coeff_vmp * delta_t_hot)

        # NEC 690.7: Voc at lowest expected temperature
        # Apply elevation correction if needed (approx 1% per 300m above sea level)
        elevation = site_params.get('elevation', 0)
        elevation_factor = 1 + (elevation / 300) * 0.01

        v_oc_cold_corrected = v_oc_cold * elevation_factor * safety_factor

        # Calculate maximum modules per string (limited by Voc max)
        max_modules_voc = int(np.floor(vdc_max / v_oc_cold_corrected))

        # Calculate maximum modules per string (limited by MPPT max)
        # Use Vmp at cold temp (conservative)
        v_mp_cold = v_mp_stc * (1 + temp_coeff_vmp * delta_t_cold)
        max_modules_mppt = int(np.floor(mppt_max / v_mp_cold))

        # The limiting factor is the smaller of the two
        max_modules = min(max_modules_voc, max_modules_mppt)

        # Calculate minimum modules per string (limited by MPPT min)
        # Use Vmp at hot temp (lowest Vmp)
        min_modules = int(np.ceil(mppt_min / v_mp_hot))

        # Ensure minimum is at least 1
        min_modules = max(1, min_modules)

        # Check current constraints
        if 'idc_max' in inverter_params:
            idc_max = inverter_params['idc_max']
            # Calculate max strings based on current
            # String current = module current (series doesn't change current)
            max_strings_current = int(np.floor(idc_max / i_mp_stc))
        else:
            max_strings_current = None

        # Check power constraints
        if 'max_power' in inverter_params:
            max_power = inverter_params['max_power']
            module_power_stc = v_mp_stc * i_mp_stc
            max_modules_power = int(np.floor(max_power / module_power_stc))
        else:
            max_modules_power = None

        # Calculate string voltages at different conditions
        voltages = {
            'v_oc_cold': v_oc_cold_corrected,
            'v_oc_stc': v_oc_stc,
            'v_mp_cold': v_mp_cold,
            'v_mp_stc': v_mp_stc,
            'v_mp_hot': v_mp_hot,
        }

        # Recommended string size (middle of range)
        recommended = int(np.round((min_modules + max_modules) / 2))

        results = {
            'min_modules_per_string': min_modules,
            'max_modules_per_string': max_modules,
            'recommended_modules_per_string': recommended,
            'limiting_factor_max': 'Voc_max' if max_modules_voc < max_modules_mppt else 'MPPT_max',
            'limiting_factor_min': 'MPPT_min',
            'voltages': voltages,
            'string_voltage_range': {
                'min': min_modules * v_mp_hot,
                'max': max_modules * v_mp_cold,
                'recommended': recommended * v_mp_stc,
            },
            'max_strings_per_inverter_current': max_strings_current,
            'max_modules_power_limit': max_modules_power,
            'warnings': [],
        }

        # Add warnings
        if min_modules > max_modules:
            results['warnings'].append(
                "WARNING: No valid string configuration! "
                f"Min modules ({min_modules}) > Max modules ({max_modules}). "
                "Module and inverter are incompatible."
            )

        if max_modules < 2:
            results['warnings'].append(
                "WARNING: Maximum string size is very small. "
                "Consider using a different inverter or module."
            )

        if min_modules * v_mp_hot < mppt_min:
            results['warnings'].append(
                f"WARNING: Minimum string voltage ({min_modules * v_mp_hot:.1f}V) "
                f"may be below MPPT minimum ({mppt_min}V) at high temperatures."
            )

        logger.info(f"String sizing complete: {min_modules}-{max_modules} modules per string")
        return results

    def calculate_system_configuration(
        self,
        system_size_kw: float,
        module_params: Dict,
        inverter_params: Dict,
        site_params: Dict,
        modules_per_string: Optional[int] = None,
    ) -> Dict:
        """
        Calculate complete system configuration (strings, inverters)

        Args:
            system_size_kw: Target system size in kW DC
            module_params: Module specifications
            inverter_params: Inverter specifications
            site_params: Site parameters
            modules_per_string: Fixed modules per string (optional)

        Returns:
            System configuration with inverter count and string count
        """
        # Calculate string sizing first
        string_results = self.calculate_string_size(
            module_params, inverter_params, site_params
        )

        if string_results['warnings'] and "No valid string" in string_results['warnings'][0]:
            return {
                'error': 'Module and inverter are incompatible',
                'string_results': string_results
            }

        # Determine modules per string
        if modules_per_string is None:
            modules_per_string = string_results['recommended_modules_per_string']
        elif modules_per_string < string_results['min_modules_per_string']:
            modules_per_string = string_results['min_modules_per_string']
        elif modules_per_string > string_results['max_modules_per_string']:
            modules_per_string = string_results['max_modules_per_string']

        # Calculate module power
        module_power_w = module_params['v_mp'] * module_params['i_mp']

        # Calculate total modules needed
        total_modules = int(np.round(system_size_kw * 1000 / module_power_w))

        # Calculate strings needed
        total_strings = int(np.ceil(total_modules / modules_per_string))

        # Calculate actual modules (accounting for rounding)
        actual_modules = total_strings * modules_per_string

        # Calculate power per string
        power_per_string = modules_per_string * module_power_w

        # Calculate strings per inverter
        inverter_max_power = inverter_params.get('max_power', float('inf'))
        max_strings_per_inverter_power = int(np.floor(inverter_max_power / power_per_string))

        if string_results['max_strings_per_inverter_current']:
            max_strings_per_inverter = min(
                max_strings_per_inverter_power,
                string_results['max_strings_per_inverter_current']
            )
        else:
            max_strings_per_inverter = max_strings_per_inverter_power

        # Calculate number of inverters needed
        num_inverters = int(np.ceil(total_strings / max_strings_per_inverter))

        # Distribute strings across inverters
        strings_per_inverter = total_strings // num_inverters
        extra_strings = total_strings % num_inverters

        # Calculate actual system size
        actual_system_size_kw = actual_modules * module_power_w / 1000

        # Calculate DC:AC ratio
        total_inverter_power_kw = num_inverters * inverter_params.get('ac_power', inverter_max_power/1000)
        dc_ac_ratio = actual_system_size_kw / total_inverter_power_kw if total_inverter_power_kw > 0 else None

        return {
            'system_configuration': {
                'target_size_kw': system_size_kw,
                'actual_size_kw': actual_system_size_kw,
                'total_modules': actual_modules,
                'modules_per_string': modules_per_string,
                'total_strings': total_strings,
                'num_inverters': num_inverters,
                'strings_per_inverter': strings_per_inverter,
                'extra_strings': extra_strings,  # Some inverters will have +1 string
                'dc_ac_ratio': dc_ac_ratio,
            },
            'string_details': string_results,
            'power_summary': {
                'module_power_w': module_power_w,
                'string_power_w': power_per_string,
                'total_dc_power_kw': actual_system_size_kw,
                'total_ac_power_kw': total_inverter_power_kw,
            },
            'configuration_valid': True,
        }

    def generate_configuration_table(
        self,
        module_params: Dict,
        inverter_params: Dict,
        site_params: Dict,
    ) -> pd.DataFrame:
        """
        Generate table showing all valid string configurations

        Args:
            module_params: Module specifications
            inverter_params: Inverter specifications
            site_params: Site parameters

        Returns:
            DataFrame with all valid configurations
        """
        string_results = self.calculate_string_size(
            module_params, inverter_params, site_params
        )

        min_modules = string_results['min_modules_per_string']
        max_modules = string_results['max_modules_per_string']

        if min_modules > max_modules:
            return pd.DataFrame()

        configurations = []

        for modules in range(min_modules, max_modules + 1):
            v_mp_hot = string_results['voltages']['v_mp_hot']
            v_mp_stc = string_results['voltages']['v_mp_stc']
            v_mp_cold = string_results['voltages']['v_mp_cold']
            v_oc_cold = string_results['voltages']['v_oc_cold']

            config = {
                'Modules per String': modules,
                'String Voc (cold)': f"{modules * v_oc_cold:.1f} V",
                'String Vmp (cold)': f"{modules * v_mp_cold:.1f} V",
                'String Vmp (STC)': f"{modules * v_mp_stc:.1f} V",
                'String Vmp (hot)': f"{modules * v_mp_hot:.1f} V",
                'String Power (STC)': f"{modules * module_params['v_mp'] * module_params['i_mp'] / 1000:.2f} kW",
                'Within MPPT Range': 'Yes' if (modules * v_mp_hot >= inverter_params['mppt_min'] and
                                                modules * v_mp_cold <= inverter_params['mppt_max']) else 'No',
            }
            configurations.append(config)

        return pd.DataFrame(configurations)


# Utility functions for temperature corrections

def calculate_voc_at_temperature(v_oc_stc: float, temperature: float, temp_coeff: float) -> float:
    """
    Calculate Voc at given temperature

    Args:
        v_oc_stc: Voc at STC (25°C)
        temperature: Cell temperature in °C
        temp_coeff: Temperature coefficient of Voc (%/°C)

    Returns:
        Voc at given temperature
    """
    return v_oc_stc * (1 + (temp_coeff / 100) * (temperature - 25))


def calculate_vmp_at_temperature(v_mp_stc: float, temperature: float, temp_coeff: float) -> float:
    """
    Calculate Vmp at given temperature

    Args:
        v_mp_stc: Vmp at STC (25°C)
        temperature: Cell temperature in °C
        temp_coeff: Temperature coefficient of Vmp (%/°C)

    Returns:
        Vmp at given temperature
    """
    return v_mp_stc * (1 + (temp_coeff / 100) * (temperature - 25))


def estimate_cell_temperature(
    ambient_temp: float,
    irradiance: float = 1000,
    wind_speed: float = 1.0,
    mounting: str = 'open_rack'
) -> float:
    """
    Estimate cell temperature using SAPM model

    Args:
        ambient_temp: Ambient temperature (°C)
        irradiance: Plane of array irradiance (W/m²)
        wind_speed: Wind speed (m/s)
        mounting: Mounting configuration ('open_rack', 'close_roof', 'insulated_back')

    Returns:
        Estimated cell temperature (°C)
    """
    # SAPM temperature model parameters
    temp_models = {
        'open_rack': {'a': -3.47, 'b': -0.0594, 'deltaT': 3},
        'close_roof': {'a': -2.98, 'b': -0.0471, 'deltaT': 1},
        'insulated_back': {'a': -2.81, 'b': -0.0455, 'deltaT': 0},
    }

    params = temp_models.get(mounting, temp_models['open_rack'])

    # Simplified SAPM cell temperature
    # T_cell = T_ambient + (E / E0) * deltaT + E * exp(a + b * wind_speed)
    E0 = 1000  # Reference irradiance
    cell_temp = (
        ambient_temp +
        (irradiance / E0) * params['deltaT'] +
        irradiance * np.exp(params['a'] + params['b'] * wind_speed) / 1000
    )

    return cell_temp


# Pre-defined module database (common modules)
COMMON_MODULES = {
    'Generic 400W Mono': {
        'v_oc': 49.5,
        'v_mp': 41.7,
        'i_sc': 10.8,
        'i_mp': 9.6,
        'temp_coeff_v_oc': -0.28,
        'temp_coeff_v_mp': -0.37,
        'cells_in_series': 144,
    },
    'Generic 500W Mono': {
        'v_oc': 49.8,
        'v_mp': 41.9,
        'i_sc': 13.5,
        'i_mp': 11.9,
        'temp_coeff_v_oc': -0.26,
        'temp_coeff_v_mp': -0.35,
        'cells_in_series': 144,
    },
    'Generic 600W Bifacial': {
        'v_oc': 50.2,
        'v_mp': 42.1,
        'i_sc': 16.1,
        'i_mp': 14.3,
        'temp_coeff_v_oc': -0.25,
        'temp_coeff_v_mp': -0.34,
        'cells_in_series': 144,
    },
}

# Pre-defined inverter database (common inverters)
COMMON_INVERTERS = {
    'Generic String 100kW': {
        'mppt_min_voltage': 450,
        'mppt_max_voltage': 800,
        'vdc_max': 1000,
        'idc_max': 280,
        'max_power': 137000,
        'ac_power': 100000,
    },
    'Generic String 150kW': {
        'mppt_min_voltage': 500,
        'mppt_max_voltage': 850,
        'vdc_max': 1100,
        'idc_max': 400,
        'max_power': 205000,
        'ac_power': 150000,
    },
    'Generic Central 1MW': {
        'mppt_min_voltage': 600,
        'mppt_max_voltage': 900,
        'vdc_max': 1100,
        'idc_max': 2500,
        'max_power': 1200000,
        'ac_power': 1000000,
    },
    'Generic String 1500V': {
        'mppt_min_voltage': 875,
        'mppt_max_voltage': 1300,
        'vdc_max': 1500,
        'idc_max': 280,
        'max_power': 250000,
        'ac_power': 185000,
    },
}
