"""
DataModel.py - Handles geographic data fetching and spatial operations
Supports GeoJSON, OGC APIs, and PostGIS/Supabase
"""
import requests
import json
from typing import Dict, List, Tuple, Optional
from geopy.distance import geodesic


class DataModel:
    def __init__(self):
        self.data_sources = {}
        self.loaded_data = {}

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

    def query_supabase(self, client, table_name: str, filters: Dict = None) -> List[Dict]:
        """
        Query Supabase PostGIS database
        :param client: Initialized Supabase client
        :param table_name: Table to query
        :param filters: Filter conditions
        :return: Query results
        """
        try:
            query = client.table(table_name).select("*")
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            response = query.execute()
            return response.data if hasattr(response, 'data') else response
        except Exception as e:
            print(f"Error querying Supabase table {table_name}: {e}")
            raise

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

    def store_data(self, name: str, data: Dict):
        """Store loaded data for later use"""
        self.loaded_data[name] = data

    def get_data(self, name: str) -> Optional[Dict]:
        """Retrieve stored data"""
        return self.loaded_data.get(name)
