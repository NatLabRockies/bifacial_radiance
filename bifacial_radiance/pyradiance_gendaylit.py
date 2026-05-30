# Monkey-patch pyradiance.gendaylit to include -ang functionality
import subprocess as sp
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
import os
import json
import tempfile
from typing import Sequence, NamedTuple
from enum import Enum
from pyradiance.anci import handle_called_process_error, BINPATH

class xyRGB(NamedTuple):
    """Represents an extrema point from pextrem with pixel coordinates and RGB values."""
    x: int
    y: int
    R: float
    G: float
    B: float


@handle_called_process_error
def gendaylit(
    dt: None | datetime = None,
    latitude: None | float = None,
    longitude: None | float = None,
    timezone: None | int = None,
    altitude: None | float = None,
    azimuth: None | float = None,
    year: None | int = None,
    dirnorm: None | float = None,
    diffhor: None | float = None,
    dirhor: None | float = None,
    dirnorm_illum: None | float = None,
    diffhor_illum: None | float = None,
    solar: bool = False,
    sky_only: bool = False,
    silent: bool = False,
    grefl: None | float = None,
    interval: None | int = None,
) -> bytes:
    """Generates a RADIANCE description of the daylight sources using
    Perez models for direct and diffuse components.

    Args:
        dt: datetime object, mutally exclusive with altitude and azimuth
        latitude: latitude (degrees), only apply if dt is not None
        longitude: longitude (degrees), only apply if dt is not None
        timezone: standard meridian timezone, e.g., 120 for PST, only apply if dt is not None
        altitude: sun altitude, degrees above horizon, mutally exclusive with dt
        azimuth: sun azimuth, degrees west of south, mutally exclusive with dt
        year: Need to set it explicitly, won't use year in datetime object
        dirnorm: direct normal irradiance
        diffhor: diffuse horizontal irradiance
        dirhor: direct horizontal irradiance, either this or dirnorm
        dirnorm_illum: direct normal illuminance
        diffhor_illum: diffuse horizontal illuminance
        solar: if True, include solar position
        sky_only: sky description only
        silent: supress warnings,
        grefl: ground reflectance
        interval: interval for epw data

    Returns:
        output of gendaylit
    """
    cmd = [str(BINPATH / "gendaylit")]
    if dt is not None:
        cmd.append(str(dt.month))
        cmd.append(str(dt.day))
        cmd.append(str(dt.hour + dt.minute / 60 + dt.second / 3600))
        if latitude is not None:
            cmd.extend(["-a", str(latitude)])
        if longitude is not None:
            cmd.extend(["-o", str(longitude)])
        if timezone is not None:
            cmd.extend(["-m", str(timezone)])
        if year is not None:
            cmd += ["-y", str(year)]
    elif None not in (altitude, azimuth):
        cmd.extend(["-ang", str(altitude), str(azimuth)])
    else:
        raise ValueError("pyradiance.gendaylit: Must provide either dt or altitude and azimuth")
    if None not in (dirnorm, diffhor):
        cmd.extend(["-W", str(dirnorm), str(diffhor)])
    elif None not in (dirhor, diffhor):
        cmd.extend(["-G", str(dirhor), str(diffhor)])
    elif None not in (dirnorm_illum, diffhor_illum):
        cmd.extend(["-L", str(dirnorm_illum), str(diffhor_illum)])
    if solar:
        cmd.extend(["-O", "1"])
    if sky_only:
        cmd.append("-s")
    if silent:
        cmd.append("-w")
    if grefl is not None:
        cmd.extend(["-g", str(grefl)])
    if interval is not None:
        cmd.extend(["-i", str(interval)])
    return sp.run(cmd, stderr=sp.PIPE, stdout=sp.PIPE, check=True).stdout

@handle_called_process_error
def pextrem(
    pic: str | Path | bytes,
    original: bool = False,
    original_xyze: bool = False,
) -> tuple[xyRGB, xyRGB]:
    """Find extrema points in a Radiance picture.
    
    Finds the minimum and maximum brightness pixels in a Radiance HDR picture
    (RGBE, XYZE, or HyperSpectral format).
    
    Args:
        pic: Path or bytes to input picture file.
        original: If True, use original exposure values (before exposure compensation).
        original_xyze: If True, convert XYZE to luminance before finding extrema. 
        If the input is XYZE, then the second channel is in candelas/meterˆ2, 
        unless original_xyze is specified, when watts/sr/meterˆ2 are always reported.
    
    Returns:
        Two named tuples (min_xyRGB, max_xyRGB) with fields:
        x, y (int): pixel coordinates
        R, G, B (float): color channel values
        Represents the darkest and brightest pixels in the image.
    
    Examples:
        >>> min_pt, max_pt = pextrem("scene.hdr")
        >>> print(f"Darkest pixel at ({min_pt.x}, {min_pt.y}): RGB=({min_pt.R}, {min_pt.G}, {min_pt.B})")
        >>> print(f"Brightest pixel at ({max_pt.x}, {max_pt.y}): RGB=({max_pt.R}, {max_pt.G}, {max_pt.B})")
    """
    cmd = [str(BINPATH / "pextrem")]
    stdin = None
    
    if original:
        cmd.append("-o")
    elif original_xyze:
        cmd.append("-O")
    
    if isinstance(pic, (Path, str)):
        cmd.append(str(pic))
    elif isinstance(pic, bytes):
        stdin = pic
    else:
        raise TypeError("pic must be a Path, str, or bytes")
    
    result = sp.run(cmd, check=True, input=stdin, stdout=sp.PIPE)
    output = result.stdout.decode('latin1').strip()
    
    # Parse the output: two lines with format "x y  R G B"
    lines = output.split('\n')
    if len(lines) != 2:
        raise ValueError(f"Unexpected pextrem output format: expected 2 lines, got {len(lines)}")
    
    # Parse minimum values (first line)
    min_parts = lines[0].split()
    min_point = xyRGB(
        x=int(min_parts[0]),
        y=int(min_parts[1]),
        R=float(min_parts[2]),
        G=float(min_parts[3]),
        B=float(min_parts[4])
    )
    
    # Parse maximum values (second line)
    max_parts = lines[1].split()
    max_point = xyRGB(
        x=int(max_parts[0]),
        y=int(max_parts[1]),
        R=float(max_parts[2]),
        G=float(max_parts[3]),
        B=float(max_parts[4])
    )
    
    return (min_point, max_point)