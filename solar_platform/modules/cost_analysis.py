"""
Cost Analysis Module - Weather impact and financial tracking

Calculates weather-related delays, cost impacts, and financial metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

from config import get_config, DEFAULT_COSTS, WORKABILITY_THRESHOLDS
from modules.weather_service import WeatherService

logger = logging.getLogger(__name__)


class ConstructionCostAnalyzer:
    """
    Analyze weather impact on construction timeline and costs
    """

    def __init__(self, weather_service: Optional[WeatherService] = None, config=None):
        self.weather = weather_service or WeatherService()
        self.config = config or get_config()

    def calculate_weather_delays(
        self,
        project_id: str,
        planned_start: str,
        planned_end: str,
        lat: float,
        lon: float,
        cost_assumptions: Optional[Dict] = None,
    ) -> Dict:
        """
        Calculate weather-related delays and cost impact

        Args:
            project_id: Project identifier
            planned_start: Start date 'YYYY-MM-DD'
            planned_end: End date 'YYYY-MM-DD'
            lat, lon: Site coordinates
            cost_assumptions: Custom cost assumptions (optional)

        Returns:
            Dictionary with delay analysis and cost impacts
        """
        logger.info(f"Analyzing weather delays for project {project_id}")

        # Get actual weather during construction
        weather_data = self.weather.get_historical_weather(
            lat, lon, planned_start, planned_end, include_solar=False
        )

        # Count delay days
        total_days = len(weather_data)
        workable_days = weather_data['workable_day'].sum()
        delay_days = total_days - workable_days

        # Use provided costs or defaults
        costs = cost_assumptions or DEFAULT_COSTS

        # Calculate direct costs
        direct_delay_cost = delay_days * (
            costs['daily_crew_cost'] +
            costs['daily_equipment_cost'] +
            costs['daily_overhead']
        )

        # Calculate extended timeline costs
        extended_weeks = delay_days / 5  # Work weeks
        extended_cost = extended_weeks * costs['weekly_extended_overhead']

        # Categorize delays
        delay_breakdown = self._categorize_delays(weather_data)

        # Calculate productivity impact
        partial_day_losses = self._calculate_partial_productivity(weather_data)

        total_cost_impact = direct_delay_cost + extended_cost + partial_day_losses['cost']

        return {
            'project_id': project_id,
            'analysis_period': {
                'start': planned_start,
                'end': planned_end,
                'total_days': total_days,
            },
            'delay_summary': {
                'workable_days': int(workable_days),
                'delay_days': int(delay_days),
                'workability_percentage': (workable_days / total_days * 100),
                'partial_productivity_days': partial_day_losses['days'],
            },
            'cost_impact': {
                'direct_delay_cost': direct_delay_cost,
                'extended_timeline_cost': extended_cost,
                'partial_productivity_cost': partial_day_losses['cost'],
                'total_weather_impact': total_cost_impact,
                'cost_per_delay_day': total_cost_impact / delay_days if delay_days > 0 else 0,
            },
            'delay_breakdown': delay_breakdown,
            'monthly_summary': self._summarize_by_month(weather_data),
            'weather_data': weather_data,
        }

    def _categorize_delays(self, weather_data: pd.DataFrame) -> Dict:
        """
        Break down delays by weather type

        Args:
            weather_data: DataFrame with weather and workability data

        Returns:
            Dictionary with delay counts by category
        """
        unworkable = weather_data[~weather_data['workable_day']].copy()

        if unworkable.empty:
            return {
                'precipitation_days': 0,
                'high_wind_days': 0,
                'extreme_cold_days': 0,
                'extreme_heat_days': 0,
                'multiple_factors_days': 0,
            }

        # Count delay reasons (a day can have multiple reasons)
        precip_days = (unworkable['precip_mm'] > WORKABILITY_THRESHOLDS['max_precipitation_mm']).sum()
        wind_days = (unworkable['windspeed_ms'] > WORKABILITY_THRESHOLDS['max_wind_speed_ms']).sum()
        cold_days = (unworkable['temp_avg'] < WORKABILITY_THRESHOLDS['min_temperature_c']).sum()
        heat_days = (unworkable['temp_avg'] > WORKABILITY_THRESHOLDS['max_temperature_c']).sum()

        # Days with multiple factors
        unworkable['factor_count'] = 0
        unworkable.loc[unworkable['precip_mm'] > WORKABILITY_THRESHOLDS['max_precipitation_mm'], 'factor_count'] += 1
        unworkable.loc[unworkable['windspeed_ms'] > WORKABILITY_THRESHOLDS['max_wind_speed_ms'], 'factor_count'] += 1
        unworkable.loc[unworkable['temp_avg'] < WORKABILITY_THRESHOLDS['min_temperature_c'], 'factor_count'] += 1
        unworkable.loc[unworkable['temp_avg'] > WORKABILITY_THRESHOLDS['max_temperature_c'], 'factor_count'] += 1

        multiple_days = (unworkable['factor_count'] > 1).sum()

        return {
            'precipitation_days': int(precip_days),
            'high_wind_days': int(wind_days),
            'extreme_cold_days': int(cold_days),
            'extreme_heat_days': int(heat_days),
            'multiple_factors_days': int(multiple_days),
        }

    def _calculate_partial_productivity(self, weather_data: pd.DataFrame) -> Dict:
        """
        Calculate cost impact of reduced productivity on marginal days

        Args:
            weather_data: Weather DataFrame

        Returns:
            Dictionary with partial productivity impact
        """
        # Days that were workable but with challenging conditions
        workable = weather_data[weather_data['workable_day']].copy()

        # Define marginal conditions (not unworkable but not ideal)
        marginal_conditions = (
            ((workable['precip_mm'] > 1) & (workable['precip_mm'] <= WORKABILITY_THRESHOLDS['max_precipitation_mm'])) |
            ((workable['windspeed_ms'] > 10) & (workable['windspeed_ms'] <= WORKABILITY_THRESHOLDS['max_wind_speed_ms'])) |
            ((workable['temp_avg'] < 5) | (workable['temp_avg'] > 30))
        )

        marginal_days = marginal_conditions.sum()

        # Assume 30% productivity loss on marginal days
        productivity_loss = 0.30
        cost_per_day = (
            DEFAULT_COSTS['daily_crew_cost'] +
            DEFAULT_COSTS['daily_equipment_cost'] +
            DEFAULT_COSTS['daily_overhead']
        )

        partial_cost = marginal_days * cost_per_day * productivity_loss

        return {
            'days': int(marginal_days),
            'cost': partial_cost,
            'productivity_loss_pct': productivity_loss * 100,
        }

    def _summarize_by_month(self, weather_data: pd.DataFrame) -> pd.DataFrame:
        """
        Summarize workability by month

        Args:
            weather_data: Weather DataFrame

        Returns:
            Monthly summary DataFrame
        """
        df = weather_data.copy()
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M')

        monthly = df.groupby('month').agg({
            'workable_day': ['sum', 'count'],
            'precip_mm': 'sum',
            'temp_avg': 'mean',
        }).round(2)

        monthly.columns = ['workable_days', 'total_days', 'total_precip_mm', 'avg_temp']
        monthly['workability_pct'] = (monthly['workable_days'] / monthly['total_days'] * 100).round(1)

        return monthly.reset_index()

    def forecast_completion_date(
        self,
        remaining_work_days: int,
        lat: float,
        lon: float,
        start_date: Optional[str] = None,
    ) -> Dict:
        """
        Forecast completion date accounting for expected weather delays

        Args:
            remaining_work_days: Remaining work days needed
            lat, lon: Site coordinates
            start_date: Start date for forecast (default: today)

        Returns:
            Dictionary with completion forecast
        """
        if start_date is None:
            start_date = datetime.now().strftime('%Y-%m-%d')

        # Get weather forecast for next 15 days
        try:
            forecast = self.weather.get_weather_forecast(lat, lon, days=15)
            forecast_workable_days = forecast['workable_day'].sum()
        except:
            # If forecast unavailable, use historical average
            logger.warning("Could not get forecast, using historical average")
            forecast_workable_days = 10  # Assume ~70% workability

        # Calculate expected completion
        if forecast_workable_days >= remaining_work_days:
            # Can complete within forecast period
            days_to_completion = self._calculate_days_to_workdays(
                remaining_work_days, forecast
            )
            completion_date = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=days_to_completion)
            confidence = 'high'
        else:
            # Need to extrapolate beyond forecast
            # Assume 70% workability rate
            estimated_calendar_days = remaining_work_days / 0.7
            completion_date = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=estimated_calendar_days)
            confidence = 'medium'

        return {
            'remaining_work_days': remaining_work_days,
            'start_date': start_date,
            'estimated_completion': completion_date.strftime('%Y-%m-%d'),
            'calendar_days_needed': (completion_date - datetime.strptime(start_date, '%Y-%m-%d')).days,
            'confidence_level': confidence,
            'forecast_workable_days': int(forecast_workable_days),
        }

    def _calculate_days_to_workdays(
        self, work_days_needed: int, forecast_df: pd.DataFrame
    ) -> int:
        """
        Calculate calendar days needed to achieve work days

        Args:
            work_days_needed: Number of workable days needed
            forecast_df: Forecast DataFrame with workability

        Returns:
            Number of calendar days needed
        """
        cumulative_work_days = forecast_df['workable_day'].cumsum()
        try:
            days_needed_idx = (cumulative_work_days >= work_days_needed).idxmax()
            return days_needed_idx + 1
        except:
            return len(forecast_df)


class FinancialAnalyzer:
    """
    Financial analysis for solar projects
    """

    def __init__(self, config=None):
        self.config = config or get_config()

    def calculate_lcoe(
        self,
        capital_cost: float,
        annual_production_kwh: float,
        annual_om_cost: float,
        lifetime_years: int = 25,
        discount_rate: float = 0.055,
        degradation_rate: float = 0.005,
    ) -> Dict:
        """
        Calculate Levelized Cost of Energy (LCOE)

        Args:
            capital_cost: Total installed cost ($)
            annual_production_kwh: First year production (kWh)
            annual_om_cost: Annual O&M cost ($/year)
            lifetime_years: Project lifetime
            discount_rate: Real discount rate
            degradation_rate: Annual degradation rate

        Returns:
            Dictionary with LCOE and related metrics
        """
        # Calculate lifetime production with degradation
        years = np.arange(1, lifetime_years + 1)
        production_factors = (1 - degradation_rate) ** (years - 1)
        annual_production = annual_production_kwh * production_factors

        # Discount factors
        discount_factors = 1 / (1 + discount_rate) ** years

        # Present value of costs
        pv_capital = capital_cost
        pv_om = (annual_om_cost * discount_factors).sum()
        total_pv_cost = pv_capital + pv_om

        # Present value of energy
        total_pv_energy = (annual_production * discount_factors).sum()

        # LCOE
        lcoe = total_pv_cost / total_pv_energy

        return {
            'lcoe_per_kwh': lcoe,
            'lcoe_per_mwh': lcoe * 1000,
            'lifetime_production_kwh': annual_production.sum(),
            'present_value_production_kwh': total_pv_energy,
            'present_value_costs': total_pv_cost,
            'capital_cost': capital_cost,
            'pv_om_costs': pv_om,
        }

    def calculate_project_irr(
        self,
        capital_cost: float,
        annual_production_kwh: float,
        ppa_price_per_kwh: float,
        annual_om_cost: float,
        lifetime_years: int = 25,
        degradation_rate: float = 0.005,
    ) -> Dict:
        """
        Calculate project Internal Rate of Return (IRR)

        Args:
            capital_cost: Total installed cost
            annual_production_kwh: First year production
            ppa_price_per_kwh: Revenue per kWh
            annual_om_cost: Annual O&M cost
            lifetime_years: Project lifetime
            degradation_rate: Annual degradation

        Returns:
            Dictionary with IRR and NPV
        """
        # Cash flows
        cash_flows = [-capital_cost]  # Year 0

        years = np.arange(1, lifetime_years + 1)
        production_factors = (1 - degradation_rate) ** (years - 1)

        for year in years:
            production = annual_production_kwh * production_factors[year - 1]
            revenue = production * ppa_price_per_kwh
            cash_flow = revenue - annual_om_cost
            cash_flows.append(cash_flow)

        # Calculate IRR
        try:
            irr = np.irr(cash_flows)
        except:
            irr = None

        # Calculate NPV at 7% discount rate
        npv_7 = np.npv(0.07, cash_flows)

        # Simple payback
        cumulative_cf = np.cumsum(cash_flows)
        try:
            payback_years = np.where(cumulative_cf > 0)[0][0]
        except:
            payback_years = None

        return {
            'irr': irr * 100 if irr is not None else None,
            'npv_at_7pct': npv_7,
            'simple_payback_years': payback_years,
            'lifetime_revenue': sum(cash_flows[1:]),
            'lifetime_costs': capital_cost + (annual_om_cost * lifetime_years),
        }

    def calculate_capacity_factor(
        self, annual_production_kwh: float, system_capacity_kw: float
    ) -> float:
        """
        Calculate capacity factor

        Args:
            annual_production_kwh: Annual production
            system_capacity_kw: System capacity

        Returns:
            Capacity factor (%)
        """
        hours_per_year = 8760
        max_production = system_capacity_kw * hours_per_year
        capacity_factor = (annual_production_kwh / max_production) * 100
        return capacity_factor
