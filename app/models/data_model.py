"""
DataModel.py - Handles geographic data fetching and spatial operations
Supports GeoJSON, OGC APIs, and PostGIS/Supabase
"""
import requests
import json
import os
from typing import Dict, List, Tuple, Optional
from geopy.distance import geodesic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class DataModel:
    def __init__(self):
        self.data_sources = {}
        self.loaded_data = {}
        self.supabase_client = self._init_supabase()
    
    def _init_supabase(self):
        """Initialize Supabase client from environment variables"""
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if supabase_url and supabase_key:
            try:
                from supabase import create_client
                client = create_client(supabase_url, supabase_key)
                print("✓ Supabase client initialized successfully")
                return client
            except ImportError as e:
                print(f"⚠ Supabase library import error: {e}")
                print("Make sure to install with: pip install supabase")
                return None
            except Exception as e:
                print(f"⚠ Error initializing Supabase client: {e}")
                return None
        else:
            print("⚠ Supabase credentials not found in .env file")
            return None

    def register_source(self, name: str, config: Dict):
        """
        Register a data source
        :param name: Source identifier
        :param config: {type: 'geojson'|'ogc_api'|'supabase', url, ...}
        """
        self.data_sources[name] = config

    def fetch_ogc_api(self, url: str, params: Dict = None) -> Dict:
        """
        Fetch data from OGC API (WFS, WMS, etc.)
        :param url: OGC API endpoint
        :param params: Query parameters
        :return: API response as dictionary
        """
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching OGC API from {url}: {e}")
            raise

    def query_supabase(self, table_name: str, filters: Dict = None) -> List[Dict]:
        """
        Query Supabase PostGIS database
        :param table_name: Table to query
        :param filters: Filter conditions
        :return: Query results
        """
        if not self.supabase_client:
            print("Supabase client not initialized")
            return []
        
        try:
            query = self.supabase_client.table(table_name).select("*")
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            response = query.execute()
            return response.data if hasattr(response, 'data') else response
        except Exception as e:
            print(f"Error querying Supabase table {table_name}: {e}")
            return []
    
    def insert_supabase(self, table_name: str, data: Dict) -> Dict:
        """
        Insert data into Supabase table
        :param table_name: Target table
        :param data: Data to insert
        :return: Inserted record
        """
        if not self.supabase_client:
            print("Supabase client not initialized")
            return {}
        
        try:
            response = self.supabase_client.table(table_name).insert(data).execute()
            print(f"✓ Data inserted into {table_name}")
            return response.data[0] if response.data else {}
        except Exception as e:
            print(f"Error inserting into Supabase table {table_name}: {e}")
            return {}
    
    def update_supabase(self, table_name: str, record_id: int, data: Dict) -> Dict:
        """
        Update data in Supabase table
        :param table_name: Target table
        :param record_id: Record ID to update
        :param data: Data to update
        :return: Updated record
        """
        if not self.supabase_client:
            print("Supabase client not initialized")
            return {}
        
        try:
            response = self.supabase_client.table(table_name).update(data).eq('id', record_id).execute()
            print(f"✓ Data updated in {table_name}")
            return response.data[0] if response.data else {}
        except Exception as e:
            print(f"Error updating Supabase table {table_name}: {e}")
            return {}
    
    def delete_supabase(self, table_name: str, record_id: int) -> bool:
        """
        Delete data from Supabase table
        :param table_name: Target table
        :param record_id: Record ID to delete
        :return: Success status
        """
        if not self.supabase_client:
            print("Supabase client not initialized")
            return False
        
        try:
            self.supabase_client.table(table_name).delete().eq('id', record_id).execute()
            print(f"✓ Data deleted from {table_name}")
            return True
        except Exception as e:
            print(f"Error deleting from Supabase table {table_name}: {e}")
            return False

    def filter_by_distance(self, features: List[Dict], point: Tuple[float, float], 
                          radius_km: float) -> List[Dict]:
        """
        Spatial filter: Find features within distance of point
        :param features: List of GeoJSON features
        :param point: (latitude, longitude)
        :param radius_km: Search radius in kilometers
        :return: Filtered features
        """
        filtered = []
        
        for feature in features:
            if feature['geometry']['type'] == 'Point':
                coords = feature['geometry']['coordinates']
                feature_point = (coords[1], coords[0])  # (lat, lng)
                
                # Calculate distance using Haversine formula
                distance_km = geodesic(point, feature_point).kilometers
                
                if distance_km <= radius_km:
                    filtered.append(feature)
        
        return filtered

    def fetch_hjertestarterregister(self, latitude: float = None, longitude: float = None, 
                                   distance: int = 99999) -> Dict:
        """
        Fetch AED locations from Hjertestarterregister API
        :param latitude: Center latitude (uses Norway center if None)
        :param longitude: Center longitude (uses Norway center if None)
        :param distance: Search distance in meters
        :return: GeoJSON data of AEDs
        """
        from app.models.hjertestarterregister_api import HjertestarterregisterAPI
        
        try:
            api = HjertestarterregisterAPI()
            
            # Try to authenticate if credentials are available
            if api.client_id and api.client_secret:
                print("Attempting to authenticate with Hjertestarterregister API...")
                api.authenticate()
            
            # If no coordinates provided, search entire Norway
            if latitude is None or longitude is None:
                latitude = 60.4518  # Norway center
                longitude = 8.4689
            
            print(f"Fetching AEDs from Hjertestarterregister API...")
            print(f"  Center: ({latitude}, {longitude})")
            print(f"  Distance: {distance}m")
            
            # Search for assets
            response = api.search_assets(
                latitude=latitude,
                longitude=longitude,
                distance=distance,
                max_rows=5000
            )
            
            if response:
                # Convert to GeoJSON
                geojson = api.convert_to_geojson(response)
                print(f"✓ Fetched {geojson['metadata']['total_count']} AEDs")
                return geojson
            else:
                print("✗ Failed to fetch from API")
                return {"type": "FeatureCollection", "features": []}
        
        except Exception as e:
            print(f"✗ Error fetching Hjertestarterregister data: {e}")
            return {"type": "FeatureCollection", "features": []}

    def get_all_locations(self, table_name: str = 'places') -> List[Dict]:
        """
        Fetch all locations from Supabase
        :param table_name: Table name (default: 'places')
        :return: List of location records
        """
        return self.query_supabase(table_name)
    
    def get_location_by_id(self, location_id: int, table_name: str = 'places') -> Optional[Dict]:
        """
        Fetch a specific location by ID
        :param location_id: Location ID
        :param table_name: Table name
        :return: Location record or None
        """
        results = self.query_supabase(table_name, filters={'id': location_id})
        return results[0] if results else None
    
    def places_within_radius(self, latitude: float, longitude: float, radius_km: float) -> List[Dict]:
        """
        Query PostGIS function to find places within radius
        Uses the places_within_radius() RPC function
        :param latitude: Center latitude
        :param longitude: Center longitude
        :param radius_km: Search radius in kilometers
        :return: List of places with distance
        """
        if not self.supabase_client:
            print("Supabase client not initialized")
            return []
        
        try:
            response = self.supabase_client.rpc(
                'places_within_radius',
                {
                    'center_lat': latitude,
                    'center_lng': longitude,
                    'radius_km': radius_km
                }
            ).execute()
            # Handle both direct list and object response formats
            return response.data if hasattr(response, 'data') else response
        except Exception as e:
            print(f"Error calling places_within_radius: {e}")
            return []
    
    def insert_place(self, name: str, description: str, city: str, 
                     category: str, latitude: float, longitude: float) -> Dict:
        """
        Insert a new place into the places table
        :param name: Place name
        :param description: Description
        :param city: City name
        :param category: Category (landmark, church, nature, etc.)
        :param latitude: Latitude coordinate
        :param longitude: Longitude coordinate
        :return: Inserted record
        """
        data = {
            'name': name,
            'description': description,
            'city': city,
            'category': category,
            'latitude': latitude,
            'longitude': longitude
        }
        return self.insert_supabase('places', data)
    
    def get_places_by_city(self, city: str) -> List[Dict]:
        """
        Get all places in a specific city
        :param city: City name
        :return: List of places in that city
        """
        return self.query_supabase('places', filters={'city': city})
    
    def get_places_by_category(self, category: str) -> List[Dict]:
        """
        Get all places in a specific category
        :param category: Category (landmark, church, nature, sport, park, castle, etc.)
        :return: List of places in that category
        """
        return self.query_supabase('places', filters={'category': category})

    def store_data(self, name: str, data: Dict):
        """Store loaded data for later use"""
        self.loaded_data[name] = data

    def get_data(self, name: str) -> Optional[Dict]:
        """Retrieve stored data"""
        return self.loaded_data.get(name)
