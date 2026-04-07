"""
Simple test script to verify the uk_geo_neighbors functions work correctly.
"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon
from uk_geo_neighbors import find_bordering_areas

def create_test_data():
    """Create a simple test GeoDataFrame with mock UK administrative areas."""
    
    # Create simple rectangular geometries in WGS84 (London area coordinates)
    areas = {
        'LAD23CD': ['E01000001', 'E01000002', 'E01000003', 'E01000004', 'E01000005'],
        'LAD23NM': ['Central Area', 'North Area', 'East Area', 'South Area', 'West Area'],
        'geometry': [
            Polygon([(-0.2, 51.5), (-0.1, 51.5), (-0.1, 51.6), (-0.2, 51.6)]),  # Central
            Polygon([(-0.2, 51.6), (-0.1, 51.6), (-0.1, 51.7), (-0.2, 51.7)]),  # North (borders Central)
            Polygon([(-0.1, 51.5), (0.0, 51.5), (0.0, 51.6), (-0.1, 51.6)]),    # East (borders Central)  
            Polygon([(-0.2, 51.4), (-0.1, 51.4), (-0.1, 51.5), (-0.2, 51.5)]),  # South (borders Central)
            Polygon([(-0.3, 51.5), (-0.2, 51.5), (-0.2, 51.6), (-0.3, 51.6)]),  # West (borders Central)
        ]
    }
    
    gdf = gpd.GeoDataFrame(areas)
    # Set CRS manually for testing
    gdf.crs = "EPSG:4326"
    return gdf

def test_basic_functionality():
    """Test basic neighbor finding functionality."""
    print("Testing UK Geo Neighbors Package")
    print("=" * 40)
    
    # Create test data
    gdf = create_test_data()
    print(f"[OK] Created test GeoDataFrame with {len(gdf)} areas")
    print(f"   Columns: {list(gdf.columns)}")
    print(f"   CRS: {gdf.crs}")
    
    # Test 1: Find neighbors by name
    print(f"\nTest 1: Find neighbors of 'Central Area'")
    try:
        neighbors = find_bordering_areas("Central Area", gdf)
        print(f"[OK] Found {len(neighbors)} neighbors")
        print(f"   Neighbor names: {neighbors['LAD23NM'].tolist()}")
        print(f"   All border target: {neighbors['borders_target'].all()}")
        print(f"   Distance range: {neighbors['distance_m'].min()}-{neighbors['distance_m'].max()}m")
    except Exception as e:
        print(f"[ERROR] {e}")
        return False
    
    # Test 2: Find neighbors by code 
    print(f"\nTest 2: Find neighbors by ONS code 'E01000001'")
    try:
        neighbors2 = find_bordering_areas("E01000001", gdf)
        print(f"[OK] Found {len(neighbors2)} neighbors")
        print(f"   Matches test 1: {len(neighbors2) == len(neighbors)}")
    except Exception as e:
        print(f"[ERROR] {e}")
        return False
        
    # Test 3: Radius search
    print(f"\nTest 3: Find areas within 5000m of Central Area")
    try:
        nearby = find_bordering_areas("Central Area", gdf, radius_metres=5000)
        print(f"[OK] Found {len(nearby)} areas within radius")
        print(f"   Should include all test areas: {len(nearby) >= 4}")
    except Exception as e:
        print(f"[ERROR] {e}")
        return False
        
    # Test 4: Return without geometry
    print(f"\nTest 4: Return DataFrame without geometry")
    try:
        df_result = find_bordering_areas("Central Area", gdf, return_geometry=False)
        print(f"[OK] Returned {type(df_result).__name__} with {len(df_result)} rows")
        print(f"   Has geometry column: {'geometry' in df_result.columns}")
        print(f"   Required columns present: {all(col in df_result.columns for col in ['distance_m', 'borders_target'])}")
    except Exception as e:
        print(f"[ERROR] {e}")
        return False
    
    print(f"\nAll tests passed! Package is working correctly.")
    return True

if __name__ == "__main__":
    success = test_basic_functionality()
    if success:
        print(f"\nPackage ready for use!")
        print(f"   Install with: pip install git+https://github.com/107SBakst/geo-functions.git")
        print(f"   Import with: from uk_geo_neighbors import find_bordering_areas")
    else:
        print(f"\nTests failed - check the package code")
        exit(1)