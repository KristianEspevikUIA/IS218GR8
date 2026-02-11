"""
AppController.py - Main application controller
Orchestrates initialization and overall application flow
"""
import json
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
        
        self.map_model.add_layer('geojson-local', {
            'name': 'Local GeoJSON Data',
            'color': '#3388ff',
            'visible': True
        })
        
        self.map_model.add_layer('ogc-api', {
            'name': 'GeoNorge API Data',
            'color': '#ff8c00',
            'visible': False
        })

    def load_embedded_data(self):
        """Load embedded Norwegian landmarks GeoJSON data"""
        self.geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Oslo City Hall",
                        "city": "Oslo",
                        "type": "Government Building",
                        "year_built": 1950,
                        "population": 634293
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [10.7339, 59.9139]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Bergen Harbor",
                        "city": "Bergen",
                        "type": "Port",
                        "year_built": 1200,
                        "population": 285900
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [5.3221, 60.3913]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Stavanger Cathedral",
                        "city": "Stavanger",
                        "type": "Religious Building",
                        "year_built": 1125,
                        "population": 144652
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [5.7331, 58.9699]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Nidaros Cathedral",
                        "city": "Trondheim",
                        "type": "Religious Building",
                        "year_built": 1070,
                        "population": 193559
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [10.3951, 63.4269]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Tromsø Arctic Cathedral",
                        "city": "Tromsø",
                        "type": "Religious Building",
                        "year_built": 1965,
                        "population": 77570
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [18.9553, 69.6492]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Northern Railway",
                        "city": "Multiple",
                        "type": "Infrastructure",
                        "year_built": 1902,
                        "length_km": 1147
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [10.7339, 59.9139],
                            [11.0905, 60.5925],
                            [10.3951, 63.4269],
                            [18.9553, 69.6492]
                        ]
                    }
                }
            ]
        }
        
        self.data_model.store_data('geojson-local', self.geojson_data)
        self.map_model.set_layer_features('geojson-local', self.geojson_data['features'])

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
