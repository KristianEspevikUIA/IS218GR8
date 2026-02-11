"""
Flask Web Application for Interactive Web Map
MVC Architecture with Folium, GeoPandas, and OGC API support
"""
import os
from flask import Flask, render_template, request, jsonify
from app.controllers.app_controller import AppController

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


# ==================== SUPABASE API ENDPOINTS ====================

@app.route('/api/supabase/places', methods=['GET'])
def get_supabase_places():
    """
    Fetch all places from Supabase
    Returns list of place records
    """
    try:
        places = controller.data_model.get_all_locations()
        return jsonify({
            'status': 'success',
            'count': len(places),
            'data': places
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/supabase/places/<int:place_id>', methods=['GET'])
def get_supabase_place(place_id):
    """
    Fetch a specific place from Supabase by ID
    """
    try:
        place = controller.data_model.get_location_by_id(place_id)
        if place:
            return jsonify({
                'status': 'success',
                'data': place
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Place {place_id} not found'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/supabase/places', methods=['POST'])
def create_supabase_place():
    """
    Create a new place in Supabase
    Expects JSON: {
        name: str, 
        description: str, 
        city: str,
        category: str,
        latitude: float, 
        longitude: float
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'description', 'city', 'category', 'latitude', 'longitude']
        if not all(key in data for key in required_fields):
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {", ".join(required_fields)}'
            }), 400
        
        # Insert into Supabase
        result = controller.data_model.insert_place(
            name=data['name'],
            description=data['description'],
            city=data['city'],
            category=data['category'],
            latitude=float(data['latitude']),
            longitude=float(data['longitude'])
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Place created successfully',
            'data': result
        }), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/supabase/places/<int:place_id>', methods=['PUT'])
def update_supabase_place(place_id):
    """
    Update a place in Supabase
    Expects JSON with fields to update
    """
    try:
        data = request.get_json()
        result = controller.data_model.update_supabase('places', place_id, data)
        
        if result:
            return jsonify({
                'status': 'success',
                'message': 'Place updated successfully',
                'data': result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Place {place_id} not found'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/supabase/places/<int:place_id>', methods=['DELETE'])
def delete_supabase_place(place_id):
    """
    Delete a place from Supabase
    """
    try:
        success = controller.data_model.delete_supabase('places', place_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Place {place_id} deleted successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Could not delete place {place_id}'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/supabase/places/nearby', methods=['POST'])
def get_nearby_places():
    """
    Find places near a point using PostGIS spatial query
    Uses places_within_radius() RPC function
    Expects JSON: {latitude: float, longitude: float, radius_km: float}
    """
    try:
        data = request.get_json()
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
        radius_km = float(data.get('radius_km', 10))
        
        # Use PostGIS function for efficient spatial query
        nearby_places = controller.data_model.places_within_radius(latitude, longitude, radius_km)
        
        return jsonify({
            'status': 'success',
            'count': len(nearby_places),
            'search_point': {'latitude': latitude, 'longitude': longitude},
            'radius_km': radius_km,
            'data': nearby_places
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/supabase/places/city/<city>', methods=['GET'])
def get_places_by_city(city):
    """
    Get all places in a specific city
    :param city: City name
    """
    try:
        places = controller.data_model.get_places_by_city(city)
        return jsonify({
            'status': 'success',
            'city': city,
            'count': len(places),
            'data': places
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/supabase/places/category/<category>', methods=['GET'])
def get_places_by_category(category):
    """
    Get all places in a specific category
    :param category: Category name (landmark, church, nature, sport, park, castle, etc.)
    """
    try:
        places = controller.data_model.get_places_by_category(category)
        return jsonify({
            'status': 'success',
            'category': category,
            'count': len(places),
            'data': places
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)
