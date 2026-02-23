import json
import os
import sys
from dotenv import load_dotenv

# Add app directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.data_model import DataModel

def migrate_geojson_to_supabase():
    load_dotenv()
    
    # Initialize DataModel (handles Supabase connection)
    model = DataModel()
    
    if not model.supabase_client:
        print("Error: Supabase client could not be initialized. Check your .env file.")
        return

    # Load GeoJSON data
    geojson_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'data', 'norwegian_landmarks.geojson')
    
    try:
        with open(geojson_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        features = data.get('features', [])
        print(f"Found {len(features)} features to migrate...")
        
        success_count = 0
        
        for feature in features:
            props = feature['properties']
            geom = feature['geometry']
            
            if geom['type'] != 'Point':
                print(f"Skipping non-point feature: {props.get('name')}")
                continue
                
            coords = geom['coordinates'] # [lng, lat]
            
            place_data = {
                'name': props.get('name'),
                'description': f"Type: {props.get('type')}. built: {props.get('year_built')}",
                'city': props.get('city'),
                'category': props.get('type'),
                'latitude': coords[1],
                'longitude': coords[0]
            }
            
            print(f"Uploading {place_data['name']}...")
            result = model.insert_supabase('places', place_data)
            
            if result:
                success_count += 1
        
        print(f"\nMigration complete! Successfully uploaded {success_count} places.")
        
    except FileNotFoundError:
        print(f"Error: Could not find {geojson_path}")
    except Exception as e:
        print(f"Migration error: {e}")

if __name__ == "__main__":
    migrate_geojson_to_supabase()