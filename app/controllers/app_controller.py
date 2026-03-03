"""
AppController.py - Main application controller
Orchestrates initialization and overall application flow.
Now supports DYNAMIC data serving — no more frozen Folium HTML.
"""
import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from app.models.map_model import MapModel
from app.models.data_model import DataModel


def _diag_features(label: str, features: list):
    """Diagnostic: log count, first 5 IDs, and checksum"""
    ids = []
    for f in features:
        props = f.get('properties', {})
        fid = props.get('asset_id') or props.get('id') or props.get('name') or 'unknown'
        ids.append(str(fid))
    ids_sorted = sorted(ids)
    checksum = hashlib.md5(','.join(ids_sorted).encode()).hexdigest()[:12]
    ts = datetime.now().isoformat()
    print(f"[{label}] ts={ts}  count={len(features)}  first5={ids_sorted[:5]}  cksum={checksum}")


class AppController:
    def __init__(self):
        self.map_model = MapModel()
        self.data_model = DataModel()
        self.geojson_data = None
        self._local_features = []

    def initialize(self):
        """Initialize data sources (called once at startup)"""
        try:
            print(f"\n{'='*60}")
            print(f"[INIT] controller.initialize()  {datetime.now().isoformat()}")
            print(f"{'='*60}")

            self.setup_data_sources()
            self._load_local_geojson()

            print("✓ Controller initialized (data served dynamically per request)")
            return True
        except Exception as e:
            print(f"✗ Initialization error: {e}")
            import traceback
            traceback.print_exc()
            return False

    # ─── data source registration ────────────────────────────
    def setup_data_sources(self):
        self.data_model.register_source('geojson-local', {
            'type': 'geojson', 'name': 'Beredskapsressursar (lokal GeoJSON)'
        })
        self.data_model.register_source('ogc-wfs', {
            'type': 'ogc_wfs', 'name': 'Brannstasjoner (GeoNorge WFS)'
        })
        self.data_model.register_source('hjertestarterregister', {
            'type': 'api', 'name': 'AED Locations (Hjertestarterregister)'
        })
        self.data_model.register_source('supabase-places', {
            'type': 'supabase', 'name': 'Supabase Places'
        })

        for lid, cfg in [
            ('geojson-local', {'name': 'Beredskapsressursar', 'color': '#3388ff', 'visible': True}),
            ('ogc-wfs', {'name': 'Brannstasjoner (WFS)', 'color': '#ff8c00', 'visible': True}),
            ('hjertestarterregister', {'name': 'AED Locations', 'color': '#ff1744', 'visible': True}),
            ('supabase-places', {'name': 'Supabase Data', 'color': '#009688', 'visible': True}),
        ]:
            self.map_model.add_layer(lid, cfg)

    # ─── local geojson (static, loaded once) ─────────────────
    def _load_local_geojson(self):
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_dir, 'data', 'norwegian_landmarks.geojson')
            with open(file_path, 'r', encoding='utf-8') as f:
                self.geojson_data = json.load(f)
            self._local_features = self.geojson_data.get('features', [])
            self.data_model.store_data('geojson-local', self.geojson_data)
            print(f"✓ Loaded {len(self._local_features)} features from local GeoJSON")
        except Exception as e:
            print(f"✗ Error loading local GeoJSON: {e}")
            self._local_features = []

    # ═══════════════════════════════════════════════════════════
    #  Dynamic data getters (called per request — always fresh)
    # ═══════════════════════════════════════════════════════════
    def get_all_layers_geojson(self) -> Dict:
        """
        Return ALL map layers as a dict of GeoJSON FeatureCollections.
        Called on every page load → always fresh data.
        """
        ts = datetime.now().isoformat()
        print(f"\n[DYNAMIC] get_all_layers_geojson() at {ts}")

        layers = {}

        # 1. Local GeoJSON — beredskapsressursar (cached in memory)
        layers['beredskap'] = {
            "type": "FeatureCollection",
            "features": self._local_features
        }

        # 2. Brannstasjoner — OGC WFS from GeoNorge (live per request)
        try:
            brann_geojson = self.data_model.fetch_brannstasjoner_wfs()
            layers['brannstasjoner'] = brann_geojson
        except Exception as e:
            print(f"[DYNAMIC] ✗ brannstasjoner WFS failed: {e}")
            layers['brannstasjoner'] = {"type": "FeatureCollection", "features": []}

        # 3. AEDs — prefer Supabase hjertestartere, fallback to live API
        aed_geojson = self.data_model.get_hjertestartere_geojson()
        if len(aed_geojson.get('features', [])) == 0:
            print("[DYNAMIC] hjertestartere table empty/missing — falling back to live API")
            aed_geojson = self._fetch_aeds_from_api()
        layers['aeds'] = aed_geojson

        # 3. Supabase places
        places = self.data_model.get_all_locations('places')
        place_features = []
        for p in places:
            if p.get('latitude') and p.get('longitude'):
                place_features.append({
                    "type": "Feature",
                    "geometry": {"type": "Point",
                                 "coordinates": [p['longitude'], p['latitude']]},
                    "properties": {
                        "name": p.get('name', ''),
                        "description": p.get('description', ''),
                        "city": p.get('city', ''),
                        "category": p.get('category', ''),
                        "source": "supabase/places"
                    }
                })
        layers['places'] = {
            "type": "FeatureCollection",
            "features": place_features
        }

        # Diagnostic
        total = sum(len(l.get('features', [])) for l in layers.values())
        print(f"[DYNAMIC] total features across all layers = {total}")
        for name, fc in layers.items():
            _diag_features(f"DYNAMIC-layer-{name}", fc.get('features', []))

        return layers

    # ─── Keep backward-compat methods ────────────────────────
    def _fetch_aeds_from_api(self) -> Dict:
        """Fallback: fetch AEDs directly from Hjertestarterregister API"""
        try:
            from app.models.hjertestarterregister_api import HjertestarterregisterAPI
            api = HjertestarterregisterAPI()
            if api.client_id and api.client_secret:
                api.authenticate()
            response = api.search_assets(
                latitude=58.1414, longitude=8.0842, distance=15000, max_rows=5000
            )
            if response and 'ASSETS' in response:
                geojson = api.convert_to_geojson(response)
                # Enhance with is_available
                for feature in geojson['features']:
                    for asset in response['ASSETS']:
                        if asset.get('ASSET_ID') == feature['properties'].get('asset_id'):
                            feature['properties']['is_available'] = asset.get('IS_OPEN') == 'Y'
                            feature['properties']['is_open_status'] = asset.get('IS_OPEN', 'N')
                            break
                _diag_features("DYNAMIC-AED-API-FALLBACK", geojson['features'])
                return geojson
        except Exception as e:
            print(f"✗ API fallback failed: {e}")
        return {"type": "FeatureCollection", "features": []}

    def perform_spatial_search(self, radius_km: float) -> List[Dict]:
        search_point = self.map_model.get_search_point()
        if not search_point:
            return []
        features = self._local_features
        return self.data_model.filter_by_distance(features, search_point, radius_km)

    def fetch_ogc_api(self, url: str, params: Dict = None) -> bool:
        try:
            data = self.data_model.fetch_ogc_api(url, params)
            if isinstance(data, dict) and 'features' in data:
                self.map_model.set_layer_features('ogc-api', data.get('features', []))
                return True
            return False
        except Exception:
            return False

    def get_available_aeds(self, latitude=None, longitude=None, distance=None) -> dict:
        try:
            aeds = self.data_model.get_available_aeds(
                latitude=latitude, longitude=longitude, distance=distance
            )
            return {'count': len(aeds), 'aeds': aeds}
        except Exception as e:
            print(f"✗ Error fetching available AEDs: {e}")
            return {'count': 0, 'aeds': []}

    def save_map(self, filepath: str):
        print(f"⚠ save_map() no longer applicable with dynamic Leaflet.js frontend")
