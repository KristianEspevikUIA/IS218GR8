"""
Flask Web Application for Interactive Web Map
MVC Architecture with Leaflet.js dynamic frontend + Supabase REST backend
"""
import os
from datetime import datetime
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


# ==================== MAIN PAGE ====================

@app.route('/')
def index():
    """Render main map page (Leaflet.js loads data dynamically via /api/map/layers)"""
    data_catalog = [
        {'dataset': 'AED-hjertestartarar (263 stk)',
         'source': 'Hjertestarterregister API (OAuth 2.0)'},
        {'dataset': 'Brannstasjonar (OGC WFS)',
         'source': 'GeoNorge WFS'},
        {'dataset': 'Beredskapsressursar',
         'source': 'Lokal GeoJSON'},
        {'dataset': 'Supabase-stader (PostGIS)',
         'source': 'Supabase REST'},
        {'dataset': 'Bakgrunnskart',
         'source': 'OpenStreetMap CDN'},
    ]
    return render_template('index.html', data_catalog=data_catalog)


# ==================== DYNAMIC MAP DATA API ====================

@app.route('/api/map/layers')
def get_map_layers():
    """
    Return all map layers as GeoJSON.
    Called by Leaflet.js on every page load → always fresh data.
    """
    layers = controller.get_all_layers_geojson()
    return jsonify(layers)


# ==================== SPATIAL SEARCH ====================

@app.route('/api/search', methods=['POST'])
def spatial_search():
    try:
        data = request.get_json()
        radius_km = float(data.get('radius_km', 5))
        lat = float(data.get('lat'))
        lng = float(data.get('lng'))
        controller.map_model.set_search_point(lat, lng)
        results = controller.perform_spatial_search(radius_km)
        return jsonify({
            'status': 'success', 'count': len(results),
            'features': results,
            'search_point': {'lat': lat, 'lng': lng},
            'radius_km': radius_km
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/ogc-api', methods=['POST'])
def fetch_ogc_data():
    try:
        data = request.get_json()
        url = data.get('url')
        params = data.get('params', {})
        if not url:
            return jsonify({'status': 'error', 'message': 'URL required'}), 400
        success = controller.fetch_ogc_api(url, params)
        if success:
            return jsonify({'status': 'success', 'message': f'Loaded data from {url}'})
        return jsonify({'status': 'error', 'message': 'Failed to load OGC API data'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/data-sources')
def get_data_sources():
    sources = []
    for lid, layer in controller.map_model.layers.items():
        sources.append({
            'id': lid,
            'name': layer.get('name', lid),
            'visible': layer.get('visible', True),
        })
    return jsonify(sources)


# ==================== POSTGIS SPATIAL ENDPOINTS ====================

@app.route('/api/postgis/nearby-aeds', methods=['POST'])
def get_nearby_aeds_postgis():
    """Find AEDs near a point using PostGIS ST_DWithin (server-side spatial query)"""
    try:
        data = request.get_json()
        lat = float(data.get('latitude'))
        lng = float(data.get('longitude'))
        r = float(data.get('radius_km', 5))
        results = controller.data_model.nearby_hjertestartere(lat, lng, r)
        return jsonify({
            'status': 'success',
            'count': len(results),
            'search_point': {'latitude': lat, 'longitude': lng},
            'radius_km': r,
            'engine': 'PostGIS ST_DWithin',
            'data': results
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


# ==================== SUPABASE PLACES API ====================

@app.route('/api/supabase/places', methods=['GET'])
def get_supabase_places():
    try:
        places = controller.data_model.get_all_locations()
        return jsonify({'status': 'success', 'count': len(places), 'data': places})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/supabase/places/<int:place_id>', methods=['GET'])
def get_supabase_place(place_id):
    try:
        place = controller.data_model.get_location_by_id(place_id)
        if place:
            return jsonify({'status': 'success', 'data': place})
        return jsonify({'status': 'error', 'message': f'Place {place_id} not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/supabase/places', methods=['POST'])
def create_supabase_place():
    try:
        data = request.get_json()
        required = ['name', 'description', 'city', 'category', 'latitude', 'longitude']
        if not all(k in data for k in required):
            return jsonify({'status': 'error',
                            'message': f'Missing fields: {", ".join(required)}'}), 400
        result = controller.data_model.insert_place(
            name=data['name'], description=data['description'],
            city=data['city'], category=data['category'],
            latitude=float(data['latitude']), longitude=float(data['longitude'])
        )
        return jsonify({'status': 'success', 'data': result}), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/supabase/places/<int:place_id>', methods=['PUT'])
def update_supabase_place(place_id):
    try:
        data = request.get_json()
        result = controller.data_model.update_supabase('places', place_id, data)
        if result:
            return jsonify({'status': 'success', 'data': result})
        return jsonify({'status': 'error', 'message': f'Place {place_id} not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/supabase/places/<int:place_id>', methods=['DELETE'])
def delete_supabase_place(place_id):
    try:
        ok = controller.data_model.delete_supabase('places', place_id)
        if ok:
            return jsonify({'status': 'success', 'message': f'Place {place_id} deleted'})
        return jsonify({'status': 'error', 'message': f'Could not delete {place_id}'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/supabase/places/nearby', methods=['POST'])
def get_nearby_places():
    try:
        data = request.get_json()
        lat = float(data.get('latitude'))
        lng = float(data.get('longitude'))
        r = float(data.get('radius_km', 10))
        nearby = controller.data_model.places_within_radius(lat, lng, r)
        return jsonify({
            'status': 'success', 'count': len(nearby),
            'search_point': {'latitude': lat, 'longitude': lng},
            'radius_km': r, 'data': nearby
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/supabase/places/city/<city>', methods=['GET'])
def get_places_by_city(city):
    try:
        places = controller.data_model.get_places_by_city(city)
        return jsonify({'status': 'success', 'city': city,
                        'count': len(places), 'data': places})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/supabase/places/category/<category>', methods=['GET'])
def get_places_by_category(category):
    try:
        places = controller.data_model.get_places_by_category(category)
        return jsonify({'status': 'success', 'category': category,
                        'count': len(places), 'data': places})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


# ==================== HJERTESTARTERREGISTER AED ENDPOINTS ====================

@app.route('/api/aeds/available', methods=['GET'])
def get_available_aeds():
    try:
        lat = request.args.get('latitude', type=float)
        lng = request.args.get('longitude', type=float)
        dist = request.args.get('distance', type=int)
        aeds = controller.data_model.get_available_aeds(
            latitude=lat, longitude=lng, distance=dist
        )
        return jsonify({
            'status': 'success', 'count': len(aeds),
            'search_center': {'latitude': lat or 58.1414, 'longitude': lng or 8.0842},
            'search_radius_km': (dist or 15000) / 1000,
            'data': aeds
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/aeds/available/count', methods=['GET'])
def get_available_aeds_count():
    try:
        lat = request.args.get('latitude', type=float)
        lng = request.args.get('longitude', type=float)
        dist = request.args.get('distance', type=int)
        aeds = controller.data_model.get_available_aeds(
            latitude=lat, longitude=lng, distance=dist
        )
        return jsonify({'status': 'success', 'count': len(aeds)})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


# ==================== SEMESTERPROSJEKT: DEKNINGSGAP ====================
# Oppgave 4 — Totalforsvaret 2025–2026
# Serverar pre-computed lag frå app/data/coverage/ + dashboard-oppsummering.

@app.route('/api/coverage/service-areas')
def coverage_service_areas():
    """Buffersoner rundt AED, brannstasjon, sjukehus (GeoJSON, UTM32N → WGS84)"""
    return jsonify(controller.get_coverage_layer('service_areas'))


@app.route('/api/coverage/gaps')
def coverage_gaps_endpoint():
    """Dekningsgap-polygonar: befolka område utan AED innan 400m."""
    return jsonify(controller.get_coverage_layer('coverage_gaps'))


@app.route('/api/coverage/risk-grid')
def coverage_risk_grid():
    """250m rutenett med population, coverage_frac, risk_score, risk_class."""
    return jsonify(controller.get_coverage_layer('risk_grid'))


@app.route('/api/coverage/recommendations')
def coverage_recommendations():
    """Topp-N anbefalte nye AED-plasseringar (grådig algoritme)."""
    return jsonify(controller.get_coverage_layer('recommendations'))


@app.route('/api/coverage/population')
def coverage_population():
    """Befolkningsrutenett (250m) — kalibrert modell over kommunen."""
    return jsonify(controller.get_coverage_layer('population'))


@app.route('/api/coverage/summary')
def coverage_summary():
    """Statistikk for sidepanel: total befolkning, dekningsandel, klasser."""
    return jsonify({
        'status': 'success',
        'data': controller.coverage_summary(),
        'generated_at': datetime.now().isoformat(),
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
