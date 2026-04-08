"""
Core functions for finding neighboring UK administrative areas.
"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import base
import re
from typing import Optional, Tuple, Union


def _detect_columns(gdf: gpd.GeoDataFrame) -> Tuple[Optional[str], Optional[str]]:
    """
    Auto-detect name and code columns using ONS naming conventions.
    ONS name columns end in 'NM', code columns end in 'CD'.
    Returns (name_col, code_col) — either may be None if not found.
    """
    cols = gdf.columns.tolist()
    
    # ONS pattern: prefix + year (optional) + NM/CD
    # e.g. LAD23NM, LSOA21CD, MSOA21NM, WD23NM, PCON23CD
    nm_cols = [c for c in cols if re.search(r'NM\d*$', c, re.IGNORECASE)]
    cd_cols = [c for c in cols if re.search(r'CD\d*$', c, re.IGNORECASE)]
    
    # Prefer shorter column names (less likely to be secondary/Welsh variants)
    # ONS often includes both English and Welsh name columns e.g. LAD23NM, LAD23NMW
    nm_cols_sorted = sorted(nm_cols, key=len)
    cd_cols_sorted = sorted(cd_cols, key=len)
    
    name_col = nm_cols_sorted[0] if nm_cols_sorted else None
    code_col = cd_cols_sorted[0] if cd_cols_sorted else None
    
    return name_col, code_col


def _find_target(gdf: gpd.GeoDataFrame, 
                 query: str,
                 name_col: Optional[str],
                 code_col: Optional[str],
                 fuzzy: bool = True) -> gpd.GeoDataFrame:
    """
    Find the target row(s) in the GeoDataFrame by name or code.
    Tries exact match first, then case-insensitive, then partial if fuzzy=True.
    """
    search_cols = [c for c in [name_col, code_col] if c is not None]
    
    if not search_cols:
        raise ValueError(
            "Could not identify name or code columns. "
            "Please specify name_col and/or code_col explicitly."
        )
    
    # 1. Exact match across name and code columns
    for col in search_cols:
        result = gdf[gdf[col] == query]
        if not result.empty:
            return result
    
    # 2. Case-insensitive match
    for col in search_cols:
        result = gdf[gdf[col].str.lower() == query.lower()]
        if not result.empty:
            return result
    
    # 3. Partial / fuzzy match (contains)
    if fuzzy:
        for col in search_cols:
            result = gdf[gdf[col].str.contains(query, case=False, na=False)]
            if not result.empty:
                if len(result) > 1:
                    print(f"Multiple matches found for '{query}' in '{col}':")
                    print(result[col].tolist())
                    print("Returning first match. Use a more specific query if needed.")
                return result.iloc[[0]]
    
    # Nothing found — show helpful error
    sample_names = gdf[name_col].head(5).tolist() if name_col else []
    sample_codes = gdf[code_col].head(5).tolist() if code_col else []
    raise ValueError(
        f"'{query}' not found in dataset.\n"
        f"Sample names: {sample_names}\n"
        f"Sample codes: {sample_codes}"
    )


def find_bordering_areas(
    query: str,
    gdf: gpd.GeoDataFrame,
    radius_metres: Optional[int] = None,
    name_col: Optional[str] = None,
    code_col: Optional[str] = None,
    buffer_metres: int = 50,
    fuzzy: bool = True,
    return_geometry: bool = True,
) -> gpd.GeoDataFrame:
    """
    Find all administrative areas that border or are within a radius of a 
    target area. Works with any ONS boundary dataset: LAs, LSOAs, MSOAs, 
    wards, constituencies, NHS boundaries, travel to work areas, etc.

    Parameters
    ----------
    query : str
        Name or ONS code of the target area. Case-insensitive.
        e.g. "Barnet", "E09000003", "Barnet 001A", "E01000001"
    gdf : GeoDataFrame
        GeoDataFrame containing the boundary dataset.
        Can be in any CRS — will be reprojected to EPSG:27700 internally.
    radius_metres : int or None
        If None, returns only directly bordering areas.
        If set, returns all areas within this distance (in metres) of the 
        target boundary. Direct neighbours are included (distance = 0).
    name_col : str or None
        Column containing area names. Auto-detected from ONS conventions if None.
    code_col : str or None
        Column containing area codes. Auto-detected from ONS conventions if None.
    buffer_metres : int
        Small buffer applied when finding direct neighbours to handle 
        digitisation gaps in boundary data. Default 50m. Only used when 
        radius_metres is None.
    fuzzy : bool
        If True, falls back to partial string matching if exact match fails.
    return_geometry : bool
        If True (default), returns full GeoDataFrame with geometries.
        If False, returns a plain DataFrame (faster, smaller).

    Returns
    -------
    GeoDataFrame sorted by distance_m containing:
        - All original columns from the input GeoDataFrame
        - distance_m      : minimum distance in metres from target boundary
        - distance_km     : distance in km, rounded to 2dp
        - borders_target  : True if area directly borders the target
        - shared_border_m : length of shared border in metres (0 if not touching)

    Examples
    --------
    Find areas bordering Camden:
    >>> neighbors = find_bordering_areas("Camden", local_authorities_gdf)
    
    Find all areas within 5km of Manchester:
    >>> nearby = find_bordering_areas("Manchester", gdf, radius_metres=5000)
    
    Find neighboring LSOAs using ONS code:
    >>> lsoa_neighbors = find_bordering_areas("E01000001", lsoa_gdf)
    """

    # ------------------------------------------------------------------ #
    # 1. Reproject to British National Grid (metres) for distance accuracy #
    # ------------------------------------------------------------------ #
    original_crs = gdf.crs
    if gdf.crs is None:
        raise ValueError("GeoDataFrame has no CRS set. Set it before calling this function.")
    
    if gdf.crs.to_epsg() != 27700:
        gdf = gdf.to_crs(epsg=27700)

    # ------------------------------------------------------------------ #
    # 2. Auto-detect name/code columns if not provided                    #
    # ------------------------------------------------------------------ #
    detected_name_col, detected_code_col = _detect_columns(gdf)
    name_col = name_col or detected_name_col
    code_col = code_col or detected_code_col

    print(f"Using columns — name: '{name_col}', code: '{code_col}'")

    # ------------------------------------------------------------------ #
    # 3. Find the target area                                             #
    # ------------------------------------------------------------------ #
    target = _find_target(gdf, query, name_col, code_col, fuzzy)
    target_geom = target.geometry.iloc[0]
    target_idx  = target.index[0]
    
    # Display what was found
    target_label = target[name_col].iloc[0] if name_col else target[code_col].iloc[0]
    print(f"Target found: {target_label}")

    # ------------------------------------------------------------------ #
    # 4. Build search geometry                                            #
    # ------------------------------------------------------------------ #
    if radius_metres is not None:
        # Full radius search
        search_buffer = target_geom.buffer(radius_metres)
    else:
        # Direct neighbours only — small buffer for digitisation tolerance
        search_buffer = target_geom.buffer(buffer_metres)

    # ------------------------------------------------------------------ #
    # 5. Spatial index pre-filter then precise intersection check         #
    # ------------------------------------------------------------------ #
    candidate_idx = list(gdf.sindex.intersection(search_buffer.bounds))
    candidates = gdf.iloc[candidate_idx]

    results = candidates[
        candidates.geometry.intersects(search_buffer) &
        (candidates.index != target_idx)
    ].copy()

    if results.empty:
        print(f"No neighbouring areas found for '{query}'.")
        return results

    # ------------------------------------------------------------------ #
    # 6. Compute distance metrics                                         #
    # ------------------------------------------------------------------ #
    target_boundary = target_geom.boundary

    results["distance_m"] = results.geometry.apply(
        lambda geom: round(target_boundary.distance(geom.boundary), 1)
    )
    results["distance_km"]    = (results["distance_m"] / 1000).round(2)
    results["borders_target"] = results["distance_m"] < buffer_metres

    # Shared border length — only meaningful for direct neighbours
    def calculate_shared_border(row):
        if row["borders_target"]:
            return round(target_boundary.intersection(row.geometry.boundary).length, 1)
        else:
            return 0.0
    
    results["shared_border_m"] = results.apply(calculate_shared_border, axis=1)

    # ------------------------------------------------------------------ #
    # 7. Sort and tidy output                                             #
    # ------------------------------------------------------------------ #
    results = results.sort_values("distance_m").reset_index(drop=True)

    if not return_geometry:
        # Drop geometry for lighter output
        info_cols = [c for c in [name_col, code_col] if c]
        metric_cols = ["distance_m", "distance_km", "borders_target", "shared_border_m"]
        return pd.DataFrame(results[info_cols + metric_cols])

    return results


def find_areas_within(
    smaller_gdf: gpd.GeoDataFrame,
    larger_gdf: gpd.GeoDataFrame,
    larger_area_query: str,
    larger_name_col: Optional[str] = None,
    larger_code_col: Optional[str] = None,
    smaller_name_col: Optional[str] = None,
    smaller_code_col: Optional[str] = None,
    fuzzy: bool = True,
    return_geometry: bool = True,
) -> gpd.GeoDataFrame:
    """
    Find all smaller administrative areas (e.g. wards) that fall within or
    overlap a named larger administrative area (e.g. a local authority).

    Any smaller area that intersects the larger area at all is included —
    this covers both fully-contained areas and partial overlaps that cross
    the boundary.

    Parameters
    ----------
    smaller_gdf : GeoDataFrame
        GeoDataFrame of the smaller areas (e.g. wards, LSOAs).
    larger_gdf : GeoDataFrame
        GeoDataFrame of the larger areas (e.g. local authorities).
    larger_area_query : str
        Name or ONS code of the specific larger area to look up.
        e.g. "Barnet", "E09000003"
    larger_name_col : str or None
        Name column in larger_gdf. Auto-detected if None.
    larger_code_col : str or None
        Code column in larger_gdf. Auto-detected if None.
    smaller_name_col : str or None
        Name column in smaller_gdf. Auto-detected if None.
    smaller_code_col : str or None
        Code column in smaller_gdf. Auto-detected if None.
    fuzzy : bool
        If True, falls back to partial string matching for the larger area query.
    return_geometry : bool
        If True (default), returns a GeoDataFrame with geometries.
        If False, returns a plain DataFrame.

    Returns
    -------
    GeoDataFrame (or DataFrame if return_geometry=False) containing all
    smaller areas that intersect the named larger area, with extra columns:
        - overlap_area_m2 : area of intersection with the larger area in m²
        - pct_within      : percentage of the smaller area's total area that
                            lies within the larger area (0–100)
        - fully_within    : True if the smaller area is entirely inside the
                            larger area

    Examples
    --------
    Find all wards within Barnet:
    >>> wards_in_barnet = find_areas_within(wards_gdf, las_gdf, "Barnet")

    Find all LSOAs within a local authority by ONS code:
    >>> lsoas = find_areas_within(lsoa_gdf, la_gdf, "E09000003")
    """

    # ------------------------------------------------------------------ #
    # 1. Reproject both GDFs to British National Grid (metres)            #
    # ------------------------------------------------------------------ #
    for label, gdf in [("smaller_gdf", smaller_gdf), ("larger_gdf", larger_gdf)]:
        if gdf.crs is None:
            raise ValueError(
                f"{label} has no CRS set. Set it before calling this function."
            )

    if smaller_gdf.crs.to_epsg() != 27700:
        smaller_gdf = smaller_gdf.to_crs(epsg=27700)
    if larger_gdf.crs.to_epsg() != 27700:
        larger_gdf = larger_gdf.to_crs(epsg=27700)

    # ------------------------------------------------------------------ #
    # 2. Auto-detect columns in each GDF                                  #
    # ------------------------------------------------------------------ #
    det_larger_name, det_larger_code = _detect_columns(larger_gdf)
    larger_name_col = larger_name_col or det_larger_name
    larger_code_col = larger_code_col or det_larger_code

    det_smaller_name, det_smaller_code = _detect_columns(smaller_gdf)
    smaller_name_col = smaller_name_col or det_smaller_name
    smaller_code_col = smaller_code_col or det_smaller_code

    print(f"Larger area columns  — name: '{larger_name_col}', code: '{larger_code_col}'")
    print(f"Smaller area columns — name: '{smaller_name_col}', code: '{smaller_code_col}'")

    # ------------------------------------------------------------------ #
    # 3. Find the named larger area                                       #
    # ------------------------------------------------------------------ #
    target = _find_target(larger_gdf, larger_area_query, larger_name_col, larger_code_col, fuzzy)
    target_geom = target.geometry.iloc[0]
    target_label = (
        target[larger_name_col].iloc[0] if larger_name_col
        else target[larger_code_col].iloc[0]
    )
    print(f"Larger area found: {target_label}")

    # ------------------------------------------------------------------ #
    # 4. Spatial index pre-filter, then precise intersection check        #
    # ------------------------------------------------------------------ #
    candidate_idx = list(smaller_gdf.sindex.intersection(target_geom.bounds))
    candidates = smaller_gdf.iloc[candidate_idx]

    results = candidates[candidates.geometry.intersects(target_geom)].copy()

    if results.empty:
        print(f"No smaller areas found within '{target_label}'.")
        return results

    # ------------------------------------------------------------------ #
    # 5. Compute overlap metrics                                          #
    # ------------------------------------------------------------------ #
    results["overlap_area_m2"] = results.geometry.apply(
        lambda geom: round(geom.intersection(target_geom).area, 1)
    )
    results["pct_within"] = (
        (results["overlap_area_m2"] / results.geometry.area * 100)
        .round(2)
        .clip(upper=100.0)
    )
    results["fully_within"] = results.geometry.apply(
        lambda geom: target_geom.contains(geom)
    )

    # ------------------------------------------------------------------ #
    # 6. Sort by pct_within descending then tidy                          #
    # ------------------------------------------------------------------ #
    results = results.sort_values("pct_within", ascending=False).reset_index(drop=True)

    if not return_geometry:
        info_cols = [c for c in [smaller_name_col, smaller_code_col] if c]
        metric_cols = ["overlap_area_m2", "pct_within", "fully_within"]
        return pd.DataFrame(results[info_cols + metric_cols])

    return results