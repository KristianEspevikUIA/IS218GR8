"""
Flask Web Application for Interactive Web Map
MVC Architecture with Folium, GeoPandas, and OGC API support
"""
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from app.controllers.app_controller import AppController

# Load environment variables from .env file
load_dotenv()

# Calculate the correct template folder path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_folder = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_folder)
controller = AppController()


@app.before_request
def initialize_app():
    """Initialize app on first request"""
    if not hasattr(app, 'initialized'):
        controller.initialize()
        app.initialized = True


@app.route('/')
def index():
    """Render main map page"""
    map_html = controller.get_map_html()
    
    # Data catalog
    data_catalog = [
        {
            'dataset': 'Norwegian Cities & Landmarks',
            'source': 'Local file',
            'format': 'GeoJSON (Point/LineString)',
            'processing': 'Manually curated from OSM data'
        },
        {
            'dataset': 'GeoNorge API',
            'source': 'External WFS/WMS',
            'format': 'GeoJSON',
            'processing': 'Real-time fetching via HTTP'
        },
        {
            'dataset': 'OpenStreetMap Basemap',
            'source': 'Mapnik tiles',
            'format': 'XYZ Tiles',
            'processing': 'Served via CDN'
        }
    ]
    
    return render_template(
        'index.html',
        map_html=map_html,
        data_catalog=data_catalog
    )


@app.route('/api/search', methods=['POST'])
def spatial_search():
    """
    API endpoint for spatial search
    Expects JSON: {radius_km: float, lat: float, lng: float}
    """
    try:
        data = request.get_json()
        radius_km = float(data.get('radius_km', 5))
        lat = float(data.get('lat'))
        lng = float(data.get('lng'))
        
        # Set search point
        controller.map_model.set_search_point(lat, lng)
        
        # Perform search
        results = controller.perform_spatial_search(radius_km)
        
        return jsonify({
            'status': 'success',
            'count': len(results),
            'features': results,
            'search_point': {'lat': lat, 'lng': lng},
            'radius_km': radius_km
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/ogc-api', methods=['POST'])
def fetch_ogc_data():
    """
    API endpoint to fetch OGC API data
    Expects JSON: {url: str, params: dict}
    """
    try:
        data = request.get_json()
        url = data.get('url')
        params = data.get('params', {})
        
        if not url:
            return jsonify({'status': 'error', 'message': 'URL required'}), 400
        
        # Fetch data
        success = controller.fetch_ogc_api(url, params)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Loaded data from {url}'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to load OGC API data'
            }), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/export-map')
def export_map():
    """Export map as HTML file"""
    try:
        filepath = 'map_export.html'
        controller.save_map(filepath)
        return jsonify({
            'status': 'success',
            'filepath': filepath,
            'message': 'Map exported successfully'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/data-sources')
def get_data_sources():
    """Get registered data sources"""
    sources = [
        {
            'id': 'geojson-local',
            'name': 'Local GeoJSON Data',
            'type': 'geojson',
            'visible': controller.map_model.layers['geojson-local']['visible']
        },
        {
            'id': 'ogc-api',
            'name': 'GeoNorge API Data',
            'type': 'ogc_api',
            'visible': controller.map_model.layers['ogc-api']['visible']
        }
    ]
    return jsonify(sources)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
