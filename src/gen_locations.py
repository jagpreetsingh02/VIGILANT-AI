import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon
import os
import random

# Definining Approximate Polygons for Delhi Districts
DELHI_DISTRICTS = {
    'Rohini': [(77.09, 28.75), (77.15, 28.75), (77.15, 28.70), (77.09, 28.70)],
    'Dwarka': [(77.02, 28.62), (77.07, 28.62), (77.07, 28.55), (77.02, 28.55)],
    'South Delhi': [(77.18, 28.57), (77.25, 28.57), (77.25, 28.50), (77.18, 28.50)],
    'Central Delhi': [(77.18, 28.65), (77.24, 28.65), (77.24, 28.61), (77.18, 28.61)],
    'East Delhi': [(77.26, 28.66), (77.33, 28.66), (77.33, 28.59), (77.26, 28.59)],
    'West Delhi': [(77.06, 28.68), (77.14, 28.68), (77.14, 28.63), (77.06, 28.63)],
    'North Delhi': [(77.17, 28.74), (77.23, 28.74), (77.23, 28.68), (77.17, 28.68)]
}

# Delhi Bounding Box (User Specified)
DELHI_BOUNDS = {
    'min_lat': 28.40, 'max_lat': 28.88,
    'min_lon': 76.84, 'max_lon': 77.35
}

def generate_district_points(district_name, polygon_coords, num_points=100):
    try:
        poly = Polygon(polygon_coords)
        min_lon, min_lat, max_lon, max_lat = poly.bounds
        points = []
        attempts = 0
        while len(points) < num_points and attempts < 1000:
            attempts += 1
            # Sample from polygon bounds
            lon = random.uniform(min_lon, max_lon)
            lat = random.uniform(min_lat, max_lat)
            p = Point(lon, lat)
            if poly.contains(p):
                points.append((lat, lon))
        
        if len(points) < 'um_points:
            # Fallback to Delhi Bounds if polygon is too tight
            print(f"Warning: Could not strictly fit points in {district_name} polygon.")
            return generate_fallback_points(num_points)
            
        return points
    except Exception as e:
        print(f"Error in {district_name}: {e}")
        return generate_fallback_points(num_points)

def generate_fallback_points(num_points):
    points = []
    print("Using Fallback Delhi Bounding Box.")
    for _ in range(num_points):
        lat = random.uniform(DELHI_BOUNDS['min_lat'], DELHI_BOUNDS['max_lat'])
        lon = random.uniform(DELHI_BOUNDS['min_lon'], DELHI_BOUNDS['max_lon'])
        points.append((lat, lon))
    return points

def generate_valid_locations():
    print("Generating valid locations within Delhi Districts...")
    
    districts = list(DELHI_DISTRICTS.keys())
    shop_ids = [f'SHOP_{i:03d}' for i in range(1, 51)]
    location_data = []
    
    for shop_id in shop_ids:
        dist = random.choice(districts)
        coords = DELHI_DISTRICTS[dist]
        
        # generate 1 valid point
        valid_points = generate_district_points(dist, coords, num_points=1)
        lat, lon = valid_points[0]
        
        location_data.append({
            'ShopID': shop_id,
            'District': dist,
            'Latitude': round(lat, 6),
            'Longitude': round(lon, 6)
        })

    df = pd.DataFrame(location_data)
    
    # Validation check
    if len(df) == 0:
        print("CRITICAL: Polygon check failed completely. Using raw fallback.")
        # Total fallback logic could go here, but per-shop fallback handles it.
    
    os.makedirs('data/processed', exist_ok=True)
    out_path = 'data/processed/delhi_shop_locations.csv'
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} shop locations. Saved to {out_path}")

if __name__ == "__main__":
    generate_valid_locations()
