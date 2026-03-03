"""
DataModel.py - Handles geographic data fetching and spatial operations
Supports GeoJSON, OGC APIs, and PostGIS/Supabase via REST API (httpx)
"""
import requests
import json
import os
import hashlib
import httpx
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from geopy.distance import geodesic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class SupabaseREST:
    """Lightweight Supabase REST client using httpx (avoids broken supabase-py proxy)"""

    def __init__(self):
        self.url = os.getenv('SUPABASE_URL', '')
        self.key = os.getenv('SUPABASE_ANON_KEY', '')
        self.ready = bool(self.url and self.key)
        if self.ready:
            ref = self.url.split('//')[1].split('.')[0] if '//' in self.url else '???'
            print(f"✓ Supabase REST client ready (project={ref})")
        else:
            print("⚠ Supabase credentials not found in .env file")

    @property
    def _headers(self) -> dict:
        return {
            'apikey': self.key,
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation',
        }

    def _rest(self, table: str) -> str:
        return f"{self.url}/rest/v1/{table}"

    # ── SELECT ──────────────────────────────────────────────
    def select(self, table: str, columns: str = "*", filters: Dict = None,
               order: str = None, limit: int = None) -> List[Dict]:
        if not self.ready:
            return []
        params = {'select': columns}
        if order:
            params['order'] = order
        if limit:
            params['limit'] = str(limit)
        # Build filter query string
        filter_parts = []
        if filters:
            for k, v in filters.items():
                filter_parts.append(f"{k}=eq.{v}")
        url = self._rest(table)
        if filter_parts:
            url += "?" + "&".join(filter_parts)
        try:
            r = httpx.get(url, params=params, headers=self._headers, timeout=15.0)
            if r.status_code == 200:
                return r.json()
            print(f"⚠ Supabase SELECT {table}: {r.status_code} {r.text[:200]}")
            return []
        except Exception as e:
            print(f"⚠ Supabase SELECT {table} error: {e}")
            return []

    # ── INSERT ──────────────────────────────────────────────
    def insert(self, table: str, data: Dict) -> Dict:
        if not self.ready:
            return {}
        try:
            r = httpx.post(self._rest(table), json=data, headers=self._headers, timeout=10.0)
            if r.status_code in (200, 201):
                rows = r.json()
                return rows[0] if rows else {}
            print(f"⚠ Supabase INSERT {table}: {r.status_code}")
            return {}
        except Exception as e:
            print(f"⚠ Supabase INSERT {table} error: {e}")
            return {}

    # ── UPDATE ──────────────────────────────────────────────
    def update(self, table: str, record_id: int, data: Dict) -> Dict:
        if not self.ready:
            return {}
        try:
            r = httpx.patch(
                f"{self._rest(table)}?id=eq.{record_id}",
                json=data, headers=self._headers, timeout=10.0
            )
            if r.status_code in (200, 204):
                rows = r.json() if r.text else []
                return rows[0] if rows else {}
            print(f"⚠ Supabase UPDATE {table}: {r.status_code}")
            return {}
        except Exception as e:
            print(f"⚠ Supabase UPDATE {table} error: {e}")
            return {}

    # ── DELETE ──────────────────────────────────────────────
    def delete(self, table: str, record_id: int) -> bool:
        if not self.ready:
            return False
        try:
            r = httpx.delete(
                f"{self._rest(table)}?id=eq.{record_id}",
                headers=self._headers, timeout=10.0
            )
            return r.status_code in (200, 204)
        except Exception as e:
            print(f"⚠ Supabase DELETE {table} error: {e}")
            return False

    # ── RPC ─────────────────────────────────────────────────
    def rpc(self, fn_name: str, params: Dict) -> List[Dict]:
        if not self.ready:
            return []
        try:
            r = httpx.post(
                f"{self.url}/rest/v1/rpc/{fn_name}",
                json=params, headers=self._headers, timeout=15.0
            )
            if r.status_code == 200:
                return r.json()
            print(f"⚠ Supabase RPC {fn_name}: {r.status_code}")
            return []
        except Exception as e:
            print(f"⚠ Supabase RPC {fn_name} error: {e}")
            return []


class DataModel:
    def __init__(self):
        self.data_sources = {}
        self.loaded_data = {}
        self.sb = SupabaseREST()
        # Backward-compat: code that checks `if self.supabase_client`
        self.supabase_client = self.sb if self.sb.ready else None

    def register_source(self, name: str, config: Dict):
        self.data_sources[name] = config

    # ═══════════════════════════════════════════════════════════
    #  OGC / external HTTP
    # ═══════════════════════════════════════════════════════════
    def fetch_ogc_api(self, url: str, params: Dict = None) -> Dict:
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching OGC API from {url}: {e}")
            raise

    # ═══════════════════════════════════════════════════════════
    #  Supabase helpers  (now via REST)
    # ═══════════════════════════════════════════════════════════
    def query_supabase(self, table_name: str, filters: Dict = None) -> List[Dict]:
        return self.sb.select(table_name, filters=filters)

    def insert_supabase(self, table_name: str, data: Dict) -> Dict:
        result = self.sb.insert(table_name, data)
        if result:
            print(f"✓ Data inserted into {table_name}")
        return result

    def update_supabase(self, table_name: str, record_id: int, data: Dict) -> Dict:
        result = self.sb.update(table_name, record_id, data)
        if result:
            print(f"✓ Data updated in {table_name}")
        return result

    def delete_supabase(self, table_name: str, record_id: int) -> bool:
        ok = self.sb.delete(table_name, record_id)
        if ok:
            print(f"✓ Data deleted from {table_name}")
        return ok

    # ═══════════════════════════════════════════════════════════
    #  Spatial filter
    # ═══════════════════════════════════════════════════════════
    def filter_by_distance(self, features: List[Dict], point: Tuple[float, float],
                           radius_km: float) -> List[Dict]:
        filtered = []
        for feature in features:
            if feature['geometry']['type'] == 'Point':
                coords = feature['geometry']['coordinates']
                feature_point = (coords[1], coords[0])
                distance_km = geodesic(point, feature_point).kilometers
                if distance_km <= radius_km:
                    filtered.append(feature)
        return filtered

    # ═══════════════════════════════════════════════════════════
    #  Hjertestarterregister (external API)
    # ═══════════════════════════════════════════════════════════
    def fetch_hjertestarterregister(self, latitude: float = None, longitude: float = None,
                                     distance: int = 99999) -> Dict:
        from app.models.hjertestarterregister_api import HjertestarterregisterAPI
        try:
            api = HjertestarterregisterAPI()
            if api.client_id and api.client_secret:
                api.authenticate()
            if latitude is None or longitude is None:
                latitude, longitude = 60.4518, 8.4689
            response = api.search_assets(latitude=latitude, longitude=longitude,
                                         distance=distance, max_rows=5000)
            if response:
                return api.convert_to_geojson(response)
            return {"type": "FeatureCollection", "features": []}
        except Exception as e:
            print(f"✗ Error fetching Hjertestarterregister data: {e}")
            return {"type": "FeatureCollection", "features": []}

    def get_available_aeds(self, latitude: float = None, longitude: float = None,
                           distance: int = None) -> List[Dict]:
        from app.models.hjertestarterregister_api import HjertestarterregisterAPI
        try:
            api = HjertestarterregisterAPI()
            if api.client_id and api.client_secret:
                api.authenticate()
            return api.search_available_aeds(latitude=latitude, longitude=longitude,
                                             distance=distance)
        except Exception as e:
            print(f"✗ Error fetching available AEDs: {e}")
            return []

    # ═══════════════════════════════════════════════════════════
    #  Hjertestartere from Supabase (synced data)
    # ═══════════════════════════════════════════════════════════
    def get_hjertestartere_geojson(self) -> Dict:
        """Fetch AEDs from Supabase hjertestartere table and return as GeoJSON"""
        rows = self.sb.select('hjertestartere')
        features = []
        for row in rows:
            lat = row.get('site_latitude')
            lng = row.get('site_longitude')
            if lat is None or lng is None:
                continue
            feature = {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lng, lat]},
                "properties": {
                    "asset_id": row.get('asset_id'),
                    "site_name": row.get('site_name', ''),
                    "site_address": row.get('site_address', ''),
                    "site_post_area": row.get('site_post_area', ''),
                    "is_available": row.get('is_open', False),
                    "is_open_status": 'Y' if row.get('is_open') else 'N',
                    "opening_hours_text": row.get('opening_hours_text', ''),
                    "distance_km": row.get('distance_km', 0),
                    "source": "supabase/hjertestartere"
                }
            }
            features.append(feature)

        # Diagnostic
        ids_sorted = sorted([str(f['properties']['asset_id']) for f in features])
        checksum = hashlib.md5(','.join(ids_sorted).encode()).hexdigest()[:12]
        print(f"[DIAG-B-SUPABASE-AED] timestamp={datetime.now().isoformat()}  "
              f"count={len(features)}  first_5={ids_sorted[:5]}  checksum={checksum}")

        return {"type": "FeatureCollection", "features": features}

    # ═══════════════════════════════════════════════════════════
    #  Places helpers
    # ═══════════════════════════════════════════════════════════
    def get_all_locations(self, table_name: str = 'places') -> List[Dict]:
        return self.query_supabase(table_name)

    def get_location_by_id(self, location_id: int, table_name: str = 'places') -> Optional[Dict]:
        results = self.query_supabase(table_name, filters={'id': location_id})
        return results[0] if results else None

    def places_within_radius(self, latitude: float, longitude: float,
                             radius_km: float) -> List[Dict]:
        return self.sb.rpc('places_within_radius', {
            'center_lat': latitude, 'center_lng': longitude, 'radius_km': radius_km
        })

    def insert_place(self, name: str, description: str, city: str,
                     category: str, latitude: float, longitude: float) -> Dict:
        return self.insert_supabase('places', {
            'name': name, 'description': description, 'city': city,
            'category': category, 'latitude': latitude, 'longitude': longitude
        })

    def get_places_by_city(self, city: str) -> List[Dict]:
        return self.query_supabase('places', filters={'city': city})

    def get_places_by_category(self, category: str) -> List[Dict]:
        return self.query_supabase('places', filters={'category': category})

    def store_data(self, name: str, data: Dict):
        self.loaded_data[name] = data

    def get_data(self, name: str) -> Optional[Dict]:
        return self.loaded_data.get(name)
