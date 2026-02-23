"""
AppController.py - Main application controller
Orchestrates initialization and overall application flow
"""
import json
import os
from typing import Dict, List, Tuple, Optional
from app.models.map_model import MapModel
from app.models.data_model import DataModel
from app.views.map_view import MapView


class AppController:
    def __init__(self):
        self.map_model = MapModel()
        self.data_model = DataModel()
        self.map_view = None
        self.geojson_data = None

    def initialize(self):
        """Initialize the application"""
        try:
            # Setup data sources
            self.setup_data_sources()
            
            # Load embedded data
            self.load_embedded_data()
            
            # Load AED data from API
            print("\nLoading AED data from Hjertestarterregister...")
            self.load_aeds()
            
            # Create map view
            self.map_view = MapView(
                center=self.map_model.map_center,
                zoom_level=self.map_model.zoom_level
            )
            
            # Add layers to map
            self.render_layers()
            
            # Add layer control
            self.map_view.add_layer_control()
            
            print("✓ Map initialized successfully!")
            return True
        except Exception as e:
            print(f"✗ Initialization error: {e}")
            return False

    def setup_data_sources(self):
        """Register all data sources"""
        self.data_model.register_source('geojson-local', {
            'type': 'geojson',
            'name': 'Local GeoJSON Data'
        })
        
        self.data_model.register_source('ogc-api', {
            'type': 'ogc_api',
            'name': 'GeoNorge API Data'
        })
        
        self.data_model.register_source('hjertestarterregister', {
            'type': 'api',
            'name': 'AED Locations (Hjertestarterregister)'
        })

        self.data_model.register_source('supabase-places', {
            'type': 'supabase',
            'name': 'Supabase Places'
        })
        
        self.map_model.add_layer('geojson-local', {
            'name': 'Local Files',
            'color': '#3388ff',
            'visible': True
        })
        
        self.map_model.add_layer('ogc-api', {
            'name': 'GeoNorge API Data',
            'color': '#ff8c00',
            'visible': False
        })
        
        self.map_model.add_layer('hjertestarterregister', {
            'name': 'AED Locations',
            'color': '#ff1744',  # Red for AEDs
            'visible': True
        })

        self.map_model.add_layer('supabase-places', {
            'name': 'Supabase Data',
            'color': '#009688',  # Teal for Supabase
            'visible': True
        })

    def load_embedded_data(self):
        """Load data from local file and Supabase"""
        # 1. Load local GeoJSON
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_dir, 'data', 'norwegian_landmarks.geojson')
            
            with open(file_path, 'r', encoding='utf-8') as f:
                self.geojson_data = json.load(f)
            
            self.data_model.store_data('geojson-local', self.geojson_data)
            self.map_model.set_layer_features('geojson-local', self.geojson_data['features'])
            print(f"✓ Loaded {len(self.geojson_data.get('features', []))} features from local file")
            
        except Exception as e:
            print(f"Error loading local GeoJSON: {e}")

        # 2. Load from Supabase
        if self.data_model.supabase_client:
            print("Fetching data from Supabase...")
            places = self.data_model.get_all_locations('places')
            
            if places:
                # Convert Supabase records to GeoJSON features
                supabase_features = []
                for place in places:
                    feature = {
                        "type": "Feature",
                        "properties": {
                            "name": place.get('name'),
                            "description": place.get('description'),
                            "city": place.get('city'),
                            "category": place.get('category'),
                            "source": "Supabase"
                        },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [place.get('longitude'), place.get('latitude')]
                        }
                    }
                    supabase_features.append(feature)
                
                self.map_model.set_layer_features('supabase-places', supabase_features)
                print(f"✓ Loaded {len(supabase_features)} places from Supabase")
            else:
                print("No data found in Supabase 'places' table")

    def render_layers(self):
        """Render all visible layers on the map"""
        for layer in self.map_model.get_visible_layers():
            features = layer.get('features', [])
            if features:
                self.map_view.add_geojson_layer(
                    layer_id=layer['name'],
                    features=features,
                    color=layer.get('color', '#3388ff')
                )

    def fetch_ogc_api(self, url: str, params: Dict = None) -> bool:
        """
        Fetch and display OGC API data
        :param url: OGC API endpoint
        :param params: Query parameters
        :return: Success status
        """
        try:
            print(f"Fetching OGC API from {url}...")
            data = self.data_model.fetch_ogc_api(url, params)
            
            # Handle GeoJSON response
            if isinstance(data, dict) and 'features' in data:
                self.map_model.set_layer_features('ogc-api', data.get('features', []))
                self.map_model.toggle_layer('ogc-api')
                print(f"✓ Loaded {len(data['features'])} features from OGC API")
                return True
            else:
                print("✗ Invalid GeoJSON response from OGC API")
                return False
        except Exception as e:
            print(f"✗ Error fetching OGC API: {e}")
            return False

    def perform_spatial_search(self, radius_km: float) -> List[Dict]:
        """
        Perform spatial search within radius
        :param radius_km: Search radius in kilometers
        :return: Filtered features
        """
        search_point = self.map_model.get_search_point()
        if not search_point:
            print("✗ No search point set. Click on map to set center.")
            return []
        
        try:
            features = self.geojson_data.get('features', [])
            filtered = self.data_model.filter_by_distance(features, search_point, radius_km)
            
            print(f"✓ Found {len(filtered)} features within {radius_km}km")
            
            # Add search results to map
            if filtered:
                self.map_view.draw_search_radius(search_point, radius_km)
                self.map_view.add_geojson_layer(
                    layer_id='search-results',
                    features=filtered,
                    color='#ff6b6b'
                )
            
            return filtered
        except Exception as e:
            print(f"✗ Search error: {e}")
            return []

    def load_aeds(self, latitude: float = None, longitude: float = None, 
                  distance: int = 99999) -> bool:
        """
        Load AED data from Hjertestarterregister API
        :param latitude: Center latitude (uses Norway center if None)
        :param longitude: Center longitude (uses Norway center if None)
        :param distance: Search distance in meters
        :return: Success status
        """
        try:
            geojson = self.data_model.fetch_hjertestarterregister(
                latitude=latitude,
                longitude=longitude,
                distance=distance
            )
            
            if geojson and geojson['features']:
                self.map_model.set_layer_features('hjertestarterregister', 
                                                  geojson['features'])
                print(f"✓ Loaded {len(geojson['features'])} AEDs")
                return True
            return False
        except Exception as e:
            print(f"✗ Error loading AEDs: {e}")
            return False

    def get_map_html(self) -> str:
        """Get map as HTML for rendering"""
        if self.map_view:
            return self.map_view.get_html()
        return "<p>Map not initialized</p>"

    def save_map(self, filepath: str):
        """Save map to HTML file"""
        if self.map_view:
            self.map_view.save(filepath)
            print(f"✓ Map saved to {filepath}")
