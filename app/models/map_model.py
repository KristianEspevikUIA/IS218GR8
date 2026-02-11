"""
MapModel.py - Manages map state, layers, and viewport
"""
from typing import Dict, List, Tuple, Optional


class MapModel:
    def __init__(self):
        self.map_center = [60.4518, 8.4689]  # Norway center
        self.zoom_level = 5
        self.layers = {}
        self.spatial_bounds = None
        self.search_point = None

    def add_layer(self, name: str, config: Dict):
        """
        Add a layer to the map model
        :param name: Layer identifier
        :param config: Layer configuration
        """
        self.layers[name] = {
            'name': name,
            'visible': True,
            'color': '#3388ff',
            'features': [],
            **config
        }

    def toggle_layer(self, name: str) -> bool:
        """Toggle layer visibility"""
        if name in self.layers:
            self.layers[name]['visible'] = not self.layers[name]['visible']
            return self.layers[name]['visible']
        return False

    def set_layer_features(self, name: str, features: List[Dict]):
        """Set features for a layer"""
        if name in self.layers:
            self.layers[name]['features'] = features

    def get_visible_layers(self) -> List[Dict]:
        """Get all visible layers"""
        return [layer for layer in self.layers.values() if layer['visible']]

    def set_viewport(self, center: List[float], zoom: int):
        """Update map viewport"""
        self.map_center = center
        self.zoom_level = zoom

    def set_search_point(self, lat: float, lng: float):
        """Set the center point for spatial search"""
        self.search_point = (lat, lng)

    def get_search_point(self) -> Optional[Tuple[float, float]]:
        """Get the search point"""
        return self.search_point
