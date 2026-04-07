"""
Debug script to test the find_bordering_areas function with Brent
"""
import sys
sys.path.insert(0, '.')

import geopandas as gpd
from uk_geo_neighbors import find_bordering_areas

# Load the data
print("Loading data...")
url = "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/Local_Authority_Districts_December_2024_Boundaries_UK_BGC/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json"
gdf = gpd.read_file(url)

print(f"Data loaded. Shape: {gdf.shape}")
print(f"CRS: {gdf.crs}")
print("\nColumn names:")
print(gdf.columns.tolist())

print("\nFirst few names:")
print(gdf['LAD24NM'].head(10).tolist())

# Check if Brent exists
brent_check = gdf[gdf['LAD24NM'].str.contains('Brent', case=False, na=False)]
print(f"\nBrent check - found {len(brent_check)} matches:")
if len(brent_check) > 0:
    print(brent_check[['LAD24NM', 'LAD24CD']])

print("\nCalling find_bordering_areas...")
try:
    neighbors = find_bordering_areas('Brent', gdf)
    print(f"Success! Found {len(neighbors)} neighbors")
    if len(neighbors) > 0:
        print("\nNeighbors:")
        print(neighbors[['LAD24NM', 'LAD24CD', 'distance_m', 'borders_target']])
    else:
        print("No neighbors found!")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()