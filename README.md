# UK Geo Neighbors

A Python package for finding neighboring UK administrative areas using geopandas. Works with any UK administrative boundary dataset including Local Authorities, LSOAs, MSOAs, wards, constituencies, travel to work areas, NHS boundaries, and more.

## Features

- ✅ **Universal compatibility**: Works with any UK administrative boundary dataset
- ✅ **Auto-detection**: Automatically detects ONS name and code columns (ends with NM/CD)
- ✅ **Flexible search**: Find areas by name or ONS code with fuzzy matching
- ✅ **Distance analysis**: Get precise distances and shared border lengths
- ✅ **Radius searches**: Find all areas within a specified distance
- ✅ **Fast performance**: Uses spatial indexing for efficient queries

## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/107SBakst/geo-functions.git
```

## Quick Start

```python
import geopandas as gpd
from uk_geo_neighbors import find_bordering_areas

# Load any UK boundary dataset
gdf = gpd.read_file("local_authorities.shp")

# Find direct neighbors
neighbors = find_bordering_areas("Camden", gdf)
print(neighbors[['LAD23NM', 'distance_m', 'borders_target']])
```

## Usage Examples

### Find Direct Neighbors

```python
# Find areas that directly border Camden
neighbors = find_bordering_areas("Camden", local_authorities_gdf)

# Results include distance metrics
print(neighbors.columns)
# ['LAD23CD', 'LAD23NM', 'geometry', 'distance_m', 'distance_km', 'borders_target', 'shared_border_m']
```

### Find Areas Within a Radius

```python
# Find all areas within 5km of Manchester city center
nearby_areas = find_bordering_areas(
    "Manchester", 
    gdf, 
    radius_metres=5000
)
```

### Search by ONS Code

```python
# Use official ONS codes for precise matching
lsoa_neighbors = find_bordering_areas("E01000001", lsoa_gdf)
```

### Advanced Options

```python
# Specify columns explicitly and return without geometry for faster processing
results = find_bordering_areas(
    query="Barnet",
    gdf=boundaries,
    name_col="area_name",
    code_col="area_code", 
    fuzzy=False,           # Exact match only
    return_geometry=False  # Return DataFrame instead of GeoDataFrame
)
```

## Supported Datasets

Works with any UK administrative boundary dataset including:

- **Local Authorities (LAs)**
- **Lower Super Output Areas (LSOAs)**
- **Middle Super Output Areas (MSOAs)** 
- **Wards**
- **Parliamentary Constituencies**
- **Travel to Work Areas**
- **NHS boundaries**
- **Any ONS boundary dataset with NM/CD column conventions**

## Output Columns

The function adds these columns to your results:

- `distance_m`: Minimum distance in metres from target boundary
- `distance_km`: Distance in kilometres (rounded to 2dp)
- `borders_target`: Boolean - True if area directly borders the target
- `shared_border_m`: Length of shared border in metres (0 if not touching)

## Requirements

- Python ≥ 3.8
- geopandas ≥ 0.10.0
- pandas ≥ 1.3.0
- shapely ≥ 1.8.0

## License

MIT License - see LICENSE file for details.

## Contributing

Issues and pull requests welcome at https://github.com/107SBakst/geo-functions

## Examples with Different Boundary Types

### Local Authorities
```python
la_neighbors = find_bordering_areas("Westminster", local_authorities_gdf)
```

### LSOAs  
```python
lsoa_neighbors = find_bordering_areas("Tower Hamlets 001A", lsoa_gdf)
```

### Wards
```python
ward_neighbors = find_bordering_areas("Bloomsbury", wards_gdf)
```

### Parliamentary Constituencies
```python
constituency_neighbors = find_bordering_areas("Holborn and St Pancras", constituencies_gdf)
```

All these work automatically thanks to ONS naming conventions!