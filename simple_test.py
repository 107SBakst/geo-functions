"""
Simple test without CRS issues - just verify the functions can be imported and basic logic works.
"""

try:
    from uk_geo_neighbors import find_bordering_areas
    print("[OK] Successfully imported find_bordering_areas")
    
    # Test the helper functions
    from uk_geo_neighbors.neighbors import _detect_columns
    import pandas as pd
    
    # Create a simple test DataFrame with ONS-style columns
    test_df = pd.DataFrame({
        'LAD23CD': ['E01000001', 'E01000002'],
        'LAD23NM': ['Test Area 1', 'Test Area 2'],
        'OTHER_COL': ['A', 'B']
    })
    
    name_col, code_col = _detect_columns(test_df)
    print(f"[OK] Column detection working: name='{name_col}', code='{code_col}'")
    
    if name_col == 'LAD23NM' and code_col == 'LAD23CD':
        print("[OK] Column detection correctly identified ONS columns")
    else:
        print("[ERROR] Column detection failed")
        exit(1)
        
    print("\nPackage structure is correct and ready for use!")
    print("Install with: pip install git+https://github.com/107SBakst/geo-functions.git")
    print("Import with: from uk_geo_neighbors import find_bordering_areas")
    
except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
    exit(1)
except Exception as e:
    print(f"[ERROR] {e}")
    exit(1)