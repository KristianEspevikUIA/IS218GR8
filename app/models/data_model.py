"""
DataModel.py - Handles geographic data fetching and spatial operations
Supports GeoJSON, OGC APIs (WFS), and PostGIS/Supabase via REST API (httpx)
"""
import requests
import json
import os
import hashlib
import httpx
import xml.etree.ElementTree as ET
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
            print(f"OK Supabase REST client ready (project={ref})")
        else:
            print("WARN Supabase credentials not found in .env file")

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
            print(f"WARN Supabase SELECT {table}: {r.status_code} {r.text[:200]}")
            return []
        except Exception as e:
            print(f"WARN Supabase SELECT {table} error: {e}")
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
            print(f"WARN Supabase INSERT {table}: {r.status_code}")
            return {}
        except Exception as e:
            print(f"WARN Supabase INSERT {table} error: {e}")
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
            print(f"WARN Supabase UPDATE {table}: {r.status_code}")
            return {}
        except Exception as e:
            print(f"WARN Supabase UPDATE {table} error: {e}")
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
            print(f"WARN Supabase DELETE {table} error: {e}")
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
            print(f"WARN Supabase RPC {fn_name}: {r.status_code}")
            return []
        except Exception as e:
            print(f"WARN Supabase RPC {fn_name} error: {e}")
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
            print(f"OK Data inserted into {table_name}")
        return result

    def update_supabase(self, table_name: str, record_id: int, data: Dict) -> Dict:
        result = self.sb.update(table_name, record_id, data)
        if result:
            print(f"OK Data updated in {table_name}")
        return result

    def delete_supabase(self, table_name: str, record_id: int) -> bool:
        ok = self.sb.delete(table_name, record_id)
        if ok:
            print(f"OK Data deleted from {table_name}")
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
            print(f"ERR Error fetching Hjertestarterregister data: {e}")
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
            print(f"ERR Error fetching available AEDs: {e}")
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
            open_status = self._first_present(
                row, 'is_open_status', 'is_open', 'is_available', 'IS_OPEN'
            )
            active_status = self._first_present(
                row, 'active', 'is_active', 'asset_status', 'ACTIVE'
            )
            is_open = self._truthy_status(open_status)
            is_active = self._truthy_status(active_status, default=True)
            feature = {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lng, lat]},
                "properties": {
                    "asset_id": row.get('asset_id'),
                    "site_name": row.get('site_name', ''),
                    "site_address": row.get('site_address', ''),
                    "site_post_area": row.get('site_post_area', ''),
                    "is_available": is_open,
                    "is_open": is_open,
                    "is_active": is_active,
                    "is_open_status": 'Y' if is_open else 'N',
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

    @staticmethod
    def _first_present(row: Dict, *keys):
        for key in keys:
            value = row.get(key)
            if value is not None and value != '':
                return value
        return None

    @staticmethod
    def _truthy_status(value, default: bool = False) -> bool:
        """Normalize common API/database status values to bool."""
        if value is None or value == '':
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        text = str(value).strip().lower()
        if text in {'y', 'yes', 'true', '1', 'open', 'active', 'aktiv'}:
            return True
        if text in {'n', 'no', 'false', '0', 'closed', 'inactive', 'stengt'}:
            return False
        return default

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

    # ═══════════════════════════════════════════════════════════
    #  OGC WFS — Brannstasjoner (GeoNorge)
    # ═══════════════════════════════════════════════════════════
    def fetch_brannstasjoner_wfs(self, bbox: str = '7.5,58.0,8.5,58.5,EPSG:4326',
                                  max_features: int = 100) -> Dict:
        """
        Fetch fire stations from GeoNorge WFS (OGC standard).
        Returns GeoJSON FeatureCollection parsed from GML 3.2.
        """
        wfs_url = 'https://wfs.geonorge.no/skwms1/wfs.brannstasjoner'
        params = {
            'service': 'WFS',
            'version': '2.0.0',
            'request': 'GetFeature',
            'typeNames': 'Brannstasjon',
            'BBOX': bbox,
            'count': str(max_features),
        }
        try:
            print(f"[WFS] Fetching brannstasjoner from {wfs_url} (BBOX={bbox})")
            r = requests.get(wfs_url, params=params, timeout=15)
            r.raise_for_status()
            features = self._parse_brannstasjoner_gml(r.text)
            print(f"[WFS] OK Parsed {len(features)} brannstasjoner from GML")
            return {"type": "FeatureCollection", "features": features}
        except Exception as e:
            print(f"[WFS] ERR Error fetching brannstasjoner: {e}")
            return {"type": "FeatureCollection", "features": []}

    def _parse_brannstasjoner_gml(self, gml_text: str) -> List[Dict]:
        """Parse GML 3.2 response from GeoNorge WFS into GeoJSON features"""
        ns = {
            'wfs': 'http://www.opengis.net/wfs/2.0',
            'gml': 'http://www.opengis.net/gml/3.2',
            'app': 'http://skjema.geonorge.no/SOSI/produktspesifikasjon/Brannstasjoner/20230101',
        }
        features = []
        try:
            root = ET.fromstring(gml_text)
            members = root.findall('.//wfs:member', ns)
            if not members:
                # Try alternative namespace pattern
                members = root.findall('.//{http://www.opengis.net/wfs/2.0}member')

            for member in members:
                feature = self._parse_single_brannstasjon(member, ns)
                if feature:
                    features.append(feature)
        except ET.ParseError as e:
            print(f"[WFS] XML parse error: {e}")
        return features

    def _parse_single_brannstasjon(self, member, ns: dict) -> Optional[Dict]:
        """Parse a single brannstasjon GML member into a GeoJSON Feature"""
        try:
            # Find the brannstasjon element (try with namespace, then without)
            elem = member.find('.//app:Brannstasjon', ns)
            if elem is None:
                # Try finding any element with relevant tags
                for child in member.iter():
                    tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                    if tag == 'Brannstasjon':
                        elem = child
                        break
            if elem is None:
                return None

            # Extract properties
            props = {}
            for tag_name, prop_key in [
                ('brannstasjon', 'brannstasjon'),
                ('brannvesen', 'brannvesen'),
                ('stasjonstype', 'stasjonstype'),
                ('kasernert', 'kasernert'),
                ('kommunenummer', 'kommunenummer'),
            ]:
                el = elem.find(f'app:{tag_name}', ns)
                if el is None:
                    # Try without namespace
                    for child in elem.iter():
                        ctag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                        if ctag == tag_name:
                            el = child
                            break
                props[prop_key] = el.text.strip() if el is not None and el.text else ''

            props['source'] = 'GeoNorge WFS (OGC)'

            # Extract coordinates from gml:pos
            pos_el = None
            for p in member.iter():
                tag = p.tag.split('}')[-1] if '}' in p.tag else p.tag
                if tag == 'pos' and p.text:
                    pos_el = p
                    break

            if pos_el is None or not pos_el.text:
                return None

            # GML pos format from GeoNorge EPSG:4326: "lat lng" (northing easting)
            parts = pos_el.text.strip().split()
            if len(parts) < 2:
                return None

            lat = float(parts[0])
            lng = float(parts[1])

            # Sanity check — if lat > 90 it's actually lng-first
            if abs(lat) > 90 and abs(lng) <= 90:
                lat, lng = lng, lat

            return {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lng, lat]},
                "properties": props
            }
        except Exception as e:
            print(f"[WFS] Error parsing member: {e}")
            return None

    # ═══════════════════════════════════════════════════════════
    #  PostGIS spatial — Nearby hjertestartere (RPC)
    # ═══════════════════════════════════════════════════════════
    def nearby_hjertestartere(self, latitude: float, longitude: float,
                               radius_km: float = 5.0) -> List[Dict]:
        """
        Find AEDs near a point using PostGIS ST_DWithin (server-side spatial query).
        Requires the nearby_hjertestartere function in Supabase.
        """
        return self.sb.rpc('nearby_hjertestartere', {
            'center_lat': latitude,
            'center_lng': longitude,
            'radius_km': radius_km
        })
