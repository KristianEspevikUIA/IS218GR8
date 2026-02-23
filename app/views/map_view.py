"""
MapView.py - Handles map rendering with Folium
Converts geographic data into interactive web map visualizations
"""
import folium
from folium import plugins
from typing import Dict, List, Tuple, Optional


class MapView:
    def __init__(self, center: List[float], zoom_level: int):
        """
        Initialize Folium map
        :param center: [latitude, longitude]
        :param zoom_level: Initial zoom level
        """
        self.map = folium.Map(
            location=center,
            zoom_start=zoom_level,
            tiles='OpenStreetMap'
        )
        self.layers_group = {}

    def add_geojson_layer(self, layer_id: str, features: List[Dict], 
                         color: str = '#3388ff', popup_fields: List[str] = None):
        """
        Add GeoJSON layer to map with data-driven styling
        :param layer_id: Unique layer identifier
        :param features: List of GeoJSON features
        :param color: Default layer color (used if no specific style applies)
        :param popup_fields: Fields to show in popup
        """
        feature_group = folium.FeatureGroup(name=layer_id)
        
        for feature in features:
            geometry = feature.get('geometry', {})
            properties = feature.get('properties', {})
            
            # Data-driven styling based on property 'type'
            feature_color = color
            if 'type' in properties:
                type_val = properties['type']
                if type_val == 'Government Building':
                    feature_color = '#795548'  # Brown
                elif type_val == 'Port':
                    feature_color = '#2196f3'  # Blue
                elif type_val == 'Religious Building':
                    feature_color = '#9c27b0'  # Purple
                elif type_val == 'Infrastructure':
                    feature_color = '#607d8b'  # Grey
            
            if geometry['type'] == 'Point':
                coords = geometry['coordinates']
                
                # Create popup HTML
                popup_html = self._create_popup(properties, popup_fields)
                
                folium.CircleMarker(
                    location=[coords[1], coords[0]],  # (lat, lng)
                    radius=8,
                    popup=folium.Popup(popup_html, max_width=300),
                    color=feature_color,
                    fill=True,
                    fillColor=feature_color,
                    fillOpacity=0.7,
                    weight=2,
                    opacity=0.9
                ).add_to(feature_group)
                
            elif geometry['type'] == 'LineString':
                coords = [[c[1], c[0]] for c in geometry['coordinates']]
                folium.PolyLine(
                    coords,
                    color=feature_color,
                    weight=4,
                    opacity=0.8,
                    popup=folium.Popup(self._create_popup(properties, popup_fields), 
                                      max_width=300)
                ).add_to(feature_group)
        
        feature_group.add_to(self.map)
        self.layers_group[layer_id] = feature_group

    def draw_search_radius(self, center: Tuple[float, float], radius_km: float):
        """
        Draw search radius circle
        :param center: (latitude, longitude)
        :param radius_km: Radius in kilometers
        """
        folium.Circle(
            location=center,
            radius=radius_km * 1000,  # Convert to meters
            color='#ff6b6b',
            fill=False,
            weight=2,
            opacity=0.8,
            dash_array='5, 5'
        ).add_to(self.map)

    def add_layer_control(self):
        """Add layer control to map"""
        folium.LayerControl().add_to(self.map)

    def _create_popup(self, properties: Dict, fields: List[str] = None) -> str:
        """
        Create HTML popup content from feature properties
        :param properties: Feature attributes
        :param fields: Specific fields to show (None = all)
        :return: HTML string
        """
        if not properties:
            return "<div><p>No data available</p></div>"
        
        if fields:
            properties = {k: v for k, v in properties.items() if k in fields}
        
        html = "<div style='font-size: 12px; width: 200px;'><table style='width:100%;'>"
        for key, value in properties.items():
            html += f"<tr><td style='font-weight:bold;'>{key}:</td><td>{value}</td></tr>"
        html += "</table></div>"
        return html

    def get_html(self) -> str:
        """Get map as HTML string"""
        return self.map._repr_html_()

    def save(self, filepath: str):
        """Save map to HTML file"""
        self.map.save(filepath)
