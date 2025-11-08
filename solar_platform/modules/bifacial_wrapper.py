"""
Bifacial Radiance Wrapper - Simplified interface to bifacial_radiance

Provides easy-to-use methods for common bifacial PV modeling tasks
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import logging

try:
    import bifacial_radiance as br
except ImportError:
    br = None
    logging.warning("bifacial_radiance not installed")

from config import get_config, MODULE_TYPES

logger = logging.getLogger(__name__)


class BifacialSimulator:
    """
    Wrapper class for bifacial_radiance simulations
    """

    def __init__(self, config=None):
        self.config = config or get_config()
        self.sim_counter = 0

        if br is None:
            raise ImportError("bifacial_radiance must be installed")

    def run_fixed_tilt_simulation(
        self,
        lat: float,
        lon: float,
        tilt: float,
        azimuth: float,
        module_config: Dict,
        scene_config: Dict,
        albedo: float = 0.25,
        weather_file: Optional[str] = None,
        simulation_name: Optional[str] = None,
    ) -> Dict:
        """
        Run a fixed-tilt bifacial simulation

        Args:
            lat, lon: Site coordinates
            tilt: Module tilt angle (degrees)
            azimuth: Module azimuth (degrees, 180=south)
            module_config: Module configuration dict
            scene_config: Scene configuration dict
            albedo: Ground albedo (0-1)
            weather_file: Path to EPW file (optional, will download if None)
            simulation_name: Name for simulation

        Returns:
            Dictionary with simulation results
        """
        # Create temporary directory for simulation
        sim_name = simulation_name or f"fixed_tilt_sim_{self.sim_counter}"
        self.sim_counter += 1

        temp_dir = Path(self.config.app.temp_simulation_dir) / sim_name
        temp_dir.mkdir(parents=True, exist_ok=True)

        try:
            logger.info(f"Starting fixed-tilt simulation: {sim_name}")

            # Create RadianceObj
            demo = br.RadianceObj(sim_name, str(temp_dir))

            # Set ground albedo
            demo.setGround(albedo)

            # Get or download weather file
            if weather_file is None:
                epw_file = demo.getEPW(lat=lat, lon=lon)
            else:
                epw_file = weather_file

            # Read weather file
            metdata = demo.readWeatherFile(epw_file, coerce_year=2021)

            # Generate cumulative sky
            demo.genCumSky()

            # Make module
            module_name = module_config.get('name', 'default_module')
            demo.makeModule(
                name=module_name,
                x=module_config.get('x', 1.0),
                y=module_config.get('y', 2.0),
                bifi=module_config.get('bifaciality', 0.7),
                numpanels=module_config.get('numpanels', 1),
            )

            # Create scene
            scene_dict = {
                'tilt': tilt,
                'azimuth': azimuth,
                'nMods': scene_config.get('nMods', 20),
                'nRows': scene_config.get('nRows', 3),
                'hub_height': scene_config.get('hub_height', 2.0),
                'pitch': scene_config.get('pitch', 5.0),
            }

            scene = demo.makeScene(module_name, sceneDict=scene_dict)

            # Combine scene
            octfile = demo.makeOct()

            # Run analysis
            analysis = br.AnalysisObj(octfile, demo.basename)

            # Front scan
            frontscan, backscan = analysis.moduleAnalysis(scene)

            # Get results
            results = analysis.analysis(octfile, demo.basename, frontscan, backscan)

            # Calculate summary statistics
            front_irrad = np.mean(results['Wm2Front'])
            back_irrad = np.mean(results['Wm2Back'])
            bifacial_gain = (back_irrad / front_irrad) * 100 if front_irrad > 0 else 0

            summary = {
                'simulation_name': sim_name,
                'front_irradiance': front_irrad,
                'rear_irradiance': back_irrad,
                'bifacial_gain': bifacial_gain,
                'total_irradiance': front_irrad + back_irrad,
                'num_sensors': len(results),
                'results_df': pd.DataFrame(results),
                'scene_info': scene_dict,
                'module_info': module_config,
            }

            logger.info(f"Simulation complete - Bifacial gain: {bifacial_gain:.1f}%")
            return summary

        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            raise

        finally:
            # Cleanup (optional - keep for debugging if needed)
            if self.config.app.app_env == 'production':
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass

    def run_tracking_simulation(
        self,
        lat: float,
        lon: float,
        module_config: Dict,
        tracker_config: Dict,
        albedo: float = 0.25,
        start_date: str = '01/01',
        end_date: str = '12/31',
        weather_file: Optional[str] = None,
        simulation_name: Optional[str] = None,
    ) -> Dict:
        """
        Run a single-axis tracking simulation

        Args:
            lat, lon: Site coordinates
            module_config: Module configuration
            tracker_config: Tracker configuration (gcr, hub_height, etc.)
            albedo: Ground albedo
            start_date: Start date MM/DD
            end_date: End date MM/DD
            weather_file: Path to weather file
            simulation_name: Simulation name

        Returns:
            Dictionary with tracking simulation results
        """
        sim_name = simulation_name or f"tracking_sim_{self.sim_counter}"
        self.sim_counter += 1

        temp_dir = Path(self.config.app.temp_simulation_dir) / sim_name
        temp_dir.mkdir(parents=True, exist_ok=True)

        try:
            logger.info(f"Starting tracking simulation: {sim_name}")

            demo = br.RadianceObj(sim_name, str(temp_dir))
            demo.setGround(albedo)

            if weather_file is None:
                epw_file = demo.getEPW(lat=lat, lon=lon)
            else:
                epw_file = weather_file

            metdata = demo.readWeatherFile(epw_file, coerce_year=2021)

            # Make module
            module_name = module_config.get('name', 'tracking_module')
            demo.makeModule(
                name=module_name,
                x=module_config.get('x', 1.0),
                y=module_config.get('y', 2.0),
                bifi=module_config.get('bifaciality', 0.7),
            )

            # Generate daylit skies for tracking
            trackerdict = demo.gendaylit1axis(
                startdate=start_date,
                enddate=end_date,
                gcr=tracker_config.get('gcr', 0.33),
                hub_height=tracker_config.get('hub_height', 2.0),
                limit_angle=tracker_config.get('limit_angle', 60),
                backtrack=tracker_config.get('backtrack', True),
            )

            # Make scene for each timestamp
            trackerdict = demo.makeScene1axis(
                trackerdict=trackerdict,
                moduletype=module_name,
                sceneDict={
                    'nMods': tracker_config.get('nMods', 20),
                    'nRows': tracker_config.get('nRows', 3),
                    'hub_height': tracker_config.get('hub_height', 2.0),
                },
            )

            # Generate oct files
            trackerdict = demo.makeOct1axis(trackerdict=trackerdict)

            # Run analysis
            trackerdict = demo.analysis1axis(trackerdict=trackerdict)

            # Compile results
            results_df = demo.compileResults(trackerdict=trackerdict)

            # Calculate annual summary
            summary = {
                'simulation_name': sim_name,
                'annual_front_irrad': results_df['Wm2Front'].sum(),
                'annual_rear_irrad': results_df['Wm2Back'].sum(),
                'avg_bifacial_gain': (results_df['Wm2Back'].mean() / results_df['Wm2Front'].mean() * 100),
                'results_df': results_df,
                'trackerdict': trackerdict,
                'tracker_config': tracker_config,
            }

            logger.info(f"Tracking simulation complete")
            return summary

        except Exception as e:
            logger.error(f"Tracking simulation failed: {e}")
            raise

        finally:
            if self.config.app.app_env == 'production':
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass

    def optimize_tilt(
        self,
        lat: float,
        lon: float,
        module_config: Dict,
        scene_config: Dict,
        tilt_range: Tuple[int, int] = (10, 50),
        tilt_step: int = 5,
        albedo: float = 0.25,
    ) -> Dict:
        """
        Optimize tilt angle for maximum energy production

        Args:
            lat, lon: Site coordinates
            module_config: Module configuration
            scene_config: Scene configuration
            tilt_range: (min_tilt, max_tilt) to test
            tilt_step: Step size for tilt angles
            albedo: Ground albedo

        Returns:
            Dictionary with optimization results
        """
        logger.info(f"Starting tilt optimization from {tilt_range[0]}° to {tilt_range[1]}°")

        results = []
        tilts = range(tilt_range[0], tilt_range[1] + 1, tilt_step)

        for tilt in tilts:
            try:
                sim_result = self.run_fixed_tilt_simulation(
                    lat=lat,
                    lon=lon,
                    tilt=tilt,
                    azimuth=180,  # South-facing
                    module_config=module_config,
                    scene_config=scene_config,
                    albedo=albedo,
                    simulation_name=f"tilt_opt_{tilt}",
                )

                results.append({
                    'tilt': tilt,
                    'total_irradiance': sim_result['total_irradiance'],
                    'front_irradiance': sim_result['front_irradiance'],
                    'rear_irradiance': sim_result['rear_irradiance'],
                    'bifacial_gain': sim_result['bifacial_gain'],
                })

                logger.info(f"Tilt {tilt}°: {sim_result['total_irradiance']:.0f} W/m²")

            except Exception as e:
                logger.error(f"Failed to simulate tilt {tilt}°: {e}")
                continue

        if not results:
            raise ValueError("No successful simulations in tilt optimization")

        results_df = pd.DataFrame(results)
        optimal_idx = results_df['total_irradiance'].idxmax()
        optimal = results_df.loc[optimal_idx]

        optimization_summary = {
            'optimal_tilt': optimal['tilt'],
            'optimal_total_irradiance': optimal['total_irradiance'],
            'optimal_bifacial_gain': optimal['bifacial_gain'],
            'all_results': results_df,
            'improvement_vs_latitude': (
                (optimal['total_irradiance'] - results_df[results_df['tilt'] == abs(int(lat))]['total_irradiance'].iloc[0])
                / results_df[results_df['tilt'] == abs(int(lat))]['total_irradiance'].iloc[0] * 100
                if abs(int(lat)) in results_df['tilt'].values else None
            ),
        }

        logger.info(f"Optimal tilt: {optimal['tilt']}°")
        return optimization_summary

    def optimize_row_spacing(
        self,
        lat: float,
        lon: float,
        module_config: Dict,
        tilt: float,
        hub_height: float,
        pitch_range: Tuple[float, float] = (4.0, 8.0),
        pitch_step: float = 0.5,
        albedo: float = 0.25,
    ) -> Dict:
        """
        Optimize row spacing (pitch) for maximum energy vs. land use

        Args:
            lat, lon: Site coordinates
            module_config: Module configuration
            tilt: Fixed tilt angle
            hub_height: Hub height
            pitch_range: (min_pitch, max_pitch) in meters
            pitch_step: Step size for pitch
            albedo: Ground albedo

        Returns:
            Dictionary with optimization results
        """
        logger.info(f"Starting row spacing optimization from {pitch_range[0]}m to {pitch_range[1]}m")

        results = []
        pitches = np.arange(pitch_range[0], pitch_range[1] + pitch_step, pitch_step)

        for pitch in pitches:
            try:
                scene_config = {
                    'nMods': 20,
                    'nRows': 3,
                    'hub_height': hub_height,
                    'pitch': pitch,
                }

                sim_result = self.run_fixed_tilt_simulation(
                    lat=lat,
                    lon=lon,
                    tilt=tilt,
                    azimuth=180,
                    module_config=module_config,
                    scene_config=scene_config,
                    albedo=albedo,
                    simulation_name=f"pitch_opt_{pitch:.1f}",
                )

                # Calculate GCR (ground coverage ratio)
                module_width = module_config['y'] * np.cos(np.radians(tilt))
                gcr = module_width / pitch

                results.append({
                    'pitch': pitch,
                    'gcr': gcr,
                    'total_irradiance': sim_result['total_irradiance'],
                    'front_irradiance': sim_result['front_irradiance'],
                    'rear_irradiance': sim_result['rear_irradiance'],
                    'bifacial_gain': sim_result['bifacial_gain'],
                    'irradiance_per_gcr': sim_result['total_irradiance'] / gcr,
                })

                logger.info(f"Pitch {pitch:.1f}m (GCR {gcr:.2f}): {sim_result['total_irradiance']:.0f} W/m²")

            except Exception as e:
                logger.error(f"Failed to simulate pitch {pitch:.1f}m: {e}")
                continue

        if not results:
            raise ValueError("No successful simulations in pitch optimization")

        results_df = pd.DataFrame(results)

        # Find optimal based on different criteria
        max_irrad_idx = results_df['total_irradiance'].idxmax()
        max_efficiency_idx = results_df['irradiance_per_gcr'].idxmax()

        return {
            'max_total_irradiance': {
                'pitch': results_df.loc[max_irrad_idx, 'pitch'],
                'gcr': results_df.loc[max_irrad_idx, 'gcr'],
                'total_irradiance': results_df.loc[max_irrad_idx, 'total_irradiance'],
            },
            'max_land_efficiency': {
                'pitch': results_df.loc[max_efficiency_idx, 'pitch'],
                'gcr': results_df.loc[max_efficiency_idx, 'gcr'],
                'irradiance_per_gcr': results_df.loc[max_efficiency_idx, 'irradiance_per_gcr'],
            },
            'all_results': results_df,
        }

    def run_agripv_simulation(
        self,
        lat: float,
        lon: float,
        module_config: Dict,
        clearance_height: float,
        row_spacing: float,
        tilt: float = 15,
        azimuth: float = 180,
        albedo: float = 0.20,
        crop_height: float = 1.0,
    ) -> Dict:
        """
        Run AgriPV simulation with elevated modules over crops

        Args:
            lat, lon: Site coordinates
            module_config: Module configuration
            clearance_height: Height above ground (meters)
            row_spacing: Spacing between rows (meters)
            tilt: Module tilt angle
            azimuth: Module azimuth
            albedo: Ground/crop albedo
            crop_height: Height of crops (meters)

        Returns:
            Dictionary with AgriPV simulation results including ground irradiance
        """
        logger.info(f"Starting AgriPV simulation with {clearance_height}m clearance")

        scene_config = {
            'nMods': 20,
            'nRows': 3,
            'hub_height': clearance_height + (module_config['y'] / 2 * np.sin(np.radians(tilt))),
            'pitch': row_spacing,
        }

        # Run module simulation
        module_results = self.run_fixed_tilt_simulation(
            lat=lat,
            lon=lon,
            tilt=tilt,
            azimuth=azimuth,
            module_config=module_config,
            scene_config=scene_config,
            albedo=albedo,
            simulation_name=f"agripv_{clearance_height}m",
        )

        # Calculate ground-level irradiance (simplified - would need ground sensors in real impl)
        # This is a placeholder for actual ground irradiance analysis
        estimated_ground_irradiance = module_results['front_irradiance'] * (1 - 0.5)  # Rough estimate

        return {
            **module_results,
            'clearance_height': clearance_height,
            'crop_height': crop_height,
            'estimated_ground_irradiance': estimated_ground_irradiance,
            'shade_fraction': 0.5,  # Placeholder
            'agripv_metrics': {
                'clearance_height': clearance_height,
                'usable_height_for_crops': clearance_height - crop_height,
                'row_spacing': row_spacing,
            },
        }


def get_module_presets() -> Dict[str, Dict]:
    """
    Get predefined module configurations

    Returns:
        Dictionary of module presets
    """
    return MODULE_TYPES.copy()


def calculate_gcr(module_height: float, tilt: float, pitch: float) -> float:
    """
    Calculate ground coverage ratio

    Args:
        module_height: Module height in meters
        tilt: Tilt angle in degrees
        pitch: Row spacing in meters

    Returns:
        GCR value (0-1)
    """
    effective_width = module_height * np.cos(np.radians(tilt))
    return effective_width / pitch
