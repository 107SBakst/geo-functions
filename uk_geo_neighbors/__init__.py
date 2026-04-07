"""
UK Geo Neighbors - A Python package for finding neighboring UK administrative areas.

This package provides functions to find neighboring administrative areas in the UK
using geopandas. It works with any UK administrative boundary dataset including:
- Local Authorities (LAs)
- Lower Super Output Areas (LSOAs) 
- Middle Super Output Areas (MSOAs)
- Wards
- Parliamentary Constituencies
- Travel to Work Areas
- NHS boundaries
- And more...

Main function:
- find_bordering_areas: Find areas that border or are near a target area
"""

from .neighbors import find_bordering_areas

__version__ = "0.1.0"
__author__ = "Samuel Bakst"
__email__ = "107sbakst@gmail.com"

__all__ = ["find_bordering_areas"]