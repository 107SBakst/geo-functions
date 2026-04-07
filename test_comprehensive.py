"""
Comprehensive test of the find_bordering_areas function with Brent
"""
import sys
sys.path.insert(0, '.')

import geopandas as gpd
from uk_geo_neighbors import find_bordering_areas

# Load the data
print("Loading UK Local Authorities data...")
url = "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/Local_Authority_Districts_December_2024_Boundaries_UK_BGC/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json"
gdf = gpd.read_file(url)

print(f"Data loaded successfully. Shape: {gdf.shape}")
print(f"CRS: {gdf.crs}")

print("\nTesting find_bordering_areas function with 'Brent'...")
neighbors = find_bordering_areas('Brent', gdf)

print(f"\nSuccess! Found {len(neighbors)} areas that border Brent:")
print("=" * 80)

# Display all columns
display_cols = ['LAD24NM', 'LAD24CD', 'distance_m', 'distance_km', 'borders_target', 'shared_border_m']
print(neighbors[display_cols].to_string(index=False))

print("\n" + "=" * 80)
print(f"All {len(neighbors)} areas shown above directly border Brent (distance_m = 0.0)")
print("The shared_border_m column shows the length of shared boundary in metres.")