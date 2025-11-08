"""
Visualization Module - Charts and plots using Plotly

Provides reusable visualization functions for the Streamlit dashboard
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class SolarVisualizer:
    """
    Visualization utilities for solar project data
    """

    def __init__(self):
        self.color_scheme = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#ff9800',
            'danger': '#d32f2f',
            'info': '#17a2b8',
        }

    def plot_monthly_production(
        self,
        monthly_data: List[float],
        title: str = "Monthly Energy Production"
    ) -> go.Figure:
        """
        Plot monthly energy production

        Args:
            monthly_data: List of 12 monthly values
            title: Chart title

        Returns:
            Plotly figure
        """
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=months,
            y=monthly_data,
            marker_color=self.color_scheme['primary'],
            text=[f"{val:,.0f}" for val in monthly_data],
            textposition='outside',
        ))

        fig.update_layout(
            title=title,
            xaxis_title="Month",
            yaxis_title="Energy Production (kWh)",
            hovermode='x unified',
            template='plotly_white',
        )

        return fig

    def plot_irradiance_comparison(
        self,
        front_irrad: float,
        rear_irrad: float,
        title: str = "Front vs. Rear Irradiance"
    ) -> go.Figure:
        """
        Plot front vs rear irradiance comparison

        Args:
            front_irrad: Front irradiance value
            rear_irrad: Rear irradiance value
            title: Chart title

        Returns:
            Plotly figure
        """
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=['Front', 'Rear'],
            y=[front_irrad, rear_irrad],
            marker_color=[self.color_scheme['primary'], self.color_scheme['secondary']],
            text=[f"{front_irrad:.1f} W/m²", f"{rear_irrad:.1f} W/m²"],
            textposition='outside',
        ))

        bifacial_gain = (rear_irrad / front_irrad * 100) if front_irrad > 0 else 0

        fig.update_layout(
            title=f"{title}<br><sub>Bifacial Gain: {bifacial_gain:.1f}%</sub>",
            yaxis_title="Irradiance (W/m²)",
            template='plotly_white',
            showlegend=False,
        )

        return fig

    def plot_tilt_optimization(
        self,
        results_df: pd.DataFrame,
        optimal_tilt: float
    ) -> go.Figure:
        """
        Plot tilt angle optimization results

        Args:
            results_df: DataFrame with tilt and irradiance columns
            optimal_tilt: Optimal tilt angle

        Returns:
            Plotly figure
        """
        fig = go.Figure()

        # Total irradiance line
        fig.add_trace(go.Scatter(
            x=results_df['tilt'],
            y=results_df['total_irradiance'],
            mode='lines+markers',
            name='Total Irradiance',
            line=dict(color=self.color_scheme['primary'], width=3),
            marker=dict(size=8),
        ))

        # Highlight optimal point
        optimal_row = results_df[results_df['tilt'] == optimal_tilt].iloc[0]
        fig.add_trace(go.Scatter(
            x=[optimal_tilt],
            y=[optimal_row['total_irradiance']],
            mode='markers',
            name='Optimal',
            marker=dict(
                size=15,
                color=self.color_scheme['success'],
                symbol='star',
            ),
        ))

        fig.update_layout(
            title=f"Tilt Angle Optimization<br><sub>Optimal: {optimal_tilt}°</sub>",
            xaxis_title="Tilt Angle (degrees)",
            yaxis_title="Total Irradiance (W/m²)",
            hovermode='x unified',
            template='plotly_white',
        )

        return fig

    def plot_construction_timeline(
        self,
        weather_df: pd.DataFrame,
        title: str = "Construction Weather Timeline"
    ) -> go.Figure:
        """
        Plot construction timeline with workability

        Args:
            weather_df: DataFrame with date, workable_day, temp, precip
            title: Chart title

        Returns:
            Plotly figure
        """
        fig = go.Figure()

        # Workable days (green) and unworkable days (red)
        workable = weather_df[weather_df['workable_day']]
        unworkable = weather_df[~weather_df['workable_day']]

        fig.add_trace(go.Scatter(
            x=workable['date'],
            y=[1] * len(workable),
            mode='markers',
            name='Workable',
            marker=dict(color=self.color_scheme['success'], size=8, symbol='circle'),
        ))

        fig.add_trace(go.Scatter(
            x=unworkable['date'],
            y=[1] * len(unworkable),
            mode='markers',
            name='Weather Delay',
            marker=dict(color=self.color_scheme['danger'], size=8, symbol='x'),
        ))

        # Add precipitation bars
        fig.add_trace(go.Bar(
            x=weather_df['date'],
            y=weather_df['precip_mm'],
            name='Precipitation',
            marker_color=self.color_scheme['info'],
            opacity=0.3,
            yaxis='y2',
        ))

        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis=dict(title="Workability", showticklabels=False),
            yaxis2=dict(title="Precipitation (mm)", overlaying='y', side='right'),
            hovermode='x unified',
            template='plotly_white',
            height=400,
        )

        return fig

    def plot_weather_delays_breakdown(
        self,
        delay_breakdown: Dict
    ) -> go.Figure:
        """
        Plot pie chart of weather delay causes

        Args:
            delay_breakdown: Dictionary with delay categories

        Returns:
            Plotly figure
        """
        labels = []
        values = []

        for key, value in delay_breakdown.items():
            if value > 0:
                label = key.replace('_', ' ').title().replace('Days', '')
                labels.append(label)
                values.append(value)

        if not values:
            # No delays
            labels = ['No Weather Delays']
            values = [1]

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker=dict(colors=px.colors.qualitative.Set3),
        )])

        fig.update_layout(
            title="Weather Delay Breakdown",
            template='plotly_white',
        )

        return fig

    def plot_performance_ratio(
        self,
        dates: List,
        actual_production: List[float],
        expected_production: List[float]
    ) -> go.Figure:
        """
        Plot actual vs expected performance

        Args:
            dates: List of dates
            actual_production: Actual production values
            expected_production: Expected production values

        Returns:
            Plotly figure
        """
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=dates,
            y=expected_production,
            mode='lines',
            name='Expected',
            line=dict(color=self.color_scheme['primary'], dash='dash', width=2),
        ))

        fig.add_trace(go.Scatter(
            x=dates,
            y=actual_production,
            mode='lines+markers',
            name='Actual',
            line=dict(color=self.color_scheme['success'], width=3),
            marker=dict(size=6),
        ))

        # Calculate PR
        pr = np.array(actual_production) / np.array(expected_production) * 100
        avg_pr = np.mean(pr[~np.isnan(pr)])

        fig.update_layout(
            title=f"Performance Monitoring<br><sub>Average PR: {avg_pr:.1f}%</sub>",
            xaxis_title="Date",
            yaxis_title="Energy Production (kWh)",
            hovermode='x unified',
            template='plotly_white',
        )

        return fig

    def plot_site_map(
        self,
        lat: float,
        lon: float,
        project_name: str
    ) -> go.Figure:
        """
        Plot site location on map

        Args:
            lat: Latitude
            lon: Longitude
            project_name: Project name

        Returns:
            Plotly figure
        """
        fig = go.Figure(go.Scattermapbox(
            lat=[lat],
            lon=[lon],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=14,
                color='red',
            ),
            text=[project_name],
        ))

        fig.update_layout(
            mapbox=dict(
                style='open-street-map',
                center=dict(lat=lat, lon=lon),
                zoom=10,
            ),
            margin={"r":0, "t":0, "l":0, "b":0},
            height=400,
        )

        return fig

    def create_metrics_summary(
        self,
        annual_production: float,
        capacity_factor: float,
        bifacial_gain: float,
        lcoe: float
    ) -> Dict[str, str]:
        """
        Create formatted metrics for Streamlit metrics display

        Args:
            annual_production: Annual production in kWh
            capacity_factor: Capacity factor in %
            bifacial_gain: Bifacial gain in %
            lcoe: LCOE in $/kWh

        Returns:
            Dictionary with formatted metric strings
        """
        return {
            'annual_production': f"{annual_production:,.0f} kWh",
            'capacity_factor': f"{capacity_factor:.1f}%",
            'bifacial_gain': f"{bifacial_gain:.1f}%",
            'lcoe': f"${lcoe:.3f}/kWh",
        }

    def plot_cost_waterfall(
        self,
        cost_breakdown: Dict[str, float],
        title: str = "Project Cost Breakdown"
    ) -> go.Figure:
        """
        Create waterfall chart for cost breakdown

        Args:
            cost_breakdown: Dictionary with cost categories
            title: Chart title

        Returns:
            Plotly figure
        """
        categories = list(cost_breakdown.keys())
        values = list(cost_breakdown.values())

        fig = go.Figure(go.Waterfall(
            name="Costs",
            orientation="v",
            measure=["relative"] * (len(categories) - 1) + ["total"],
            x=categories,
            textposition="outside",
            text=[f"${v:,.0f}" for v in values],
            y=values,
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))

        fig.update_layout(
            title=title,
            showlegend=False,
            yaxis_title="Cost ($)",
            template='plotly_white',
        )

        return fig


def create_summary_table(data: Dict) -> pd.DataFrame:
    """
    Create formatted summary table

    Args:
        data: Dictionary with summary data

    Returns:
        Formatted DataFrame
    """
    df = pd.DataFrame(data.items(), columns=['Metric', 'Value'])
    return df
