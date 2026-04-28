"""
HjertestarterregisterAPI.py - REST client for Hjertestarterregister API
Fetches AED (Automated External Defibrillator) locations from Hjertestarterregister
"""
import requests
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv
import math

# Load environment variables from .env file
load_dotenv()


class HjertestarterregisterAPI:
    """
    Client for Hjertestarterregister API
    API Reference: https://hjertestarterregister.113.no/ords/api/v1/
    """
    
    BASE_URL = "https://hjertestarterregister.113.no/ords/api/v1"
    OAUTH_ENDPOINT = "https://hjertestarterregister.113.no/ords/api/oauth/token"
    
    # Kristiansand city center coordinates
    KRISTIANSAND_CENTER = {"latitude": 58.1414, "longitude": 8.0842}
    DEFAULT_SEARCH_RADIUS = 15000  # 15 km in meters
    
    def __init__(self, client_id: str = None, client_secret: str = None):
        """
        Initialize API client
        :param client_id: OAuth Client ID (optional, loads from env if not provided)
        :param client_secret: OAuth Client Secret (optional, loads from env if not provided)
        """
        # Load from environment if not provided as parameters
        self.client_id = client_id or os.getenv('HJERTESTARTERREGISTER_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('HJERTESTARTERREGISTER_CLIENT_SECRET')
        self.access_token = None
        self.token_type = "bearer"
        self.token_expires_at = None
        self.session = requests.Session()
    
    def set_credentials(self, client_id: str, client_secret: str):
        """Set OAuth credentials"""
        self.client_id = client_id
        self.client_secret = client_secret
    
    def authenticate(self) -> bool:
        """
        Authenticate and obtain OAuth access token
        :return: True if successful, False otherwise
        """
        if not self.client_id or not self.client_secret:
            print("⚠ No credentials provided - will use public search only")
            print("  To enable full API access, set HJERTESTARTERREGISTER_CLIENT_ID and")
            print("  HJERTESTARTERREGISTER_CLIENT_SECRET in your .env file")
            return False
        
        try:
            auth = (self.client_id, self.client_secret)
            data = {"grant_type": "client_credentials"}
            
            response = requests.post(
                self.OAUTH_ENDPOINT,
                auth=auth,
                data=data,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            self.access_token = result.get('access_token')
            self.token_type = result.get('token_type', 'bearer')
            expires_in = result.get('expires_in', 3600)
            self.token_expires_at = datetime.now().timestamp() + expires_in
            
            print(f"✓ Authentication successful. Token expires in {expires_in} seconds")
            return True
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Authentication failed: {e}")
            return False
    
    def _token_expired(self) -> bool:
        """Check if access token has expired"""
        if not self.token_expires_at or not self.access_token:
            return True
        return datetime.now().timestamp() >= self.token_expires_at
    
    def _ensure_authenticated(self) -> bool:
        """Ensure we have a valid token, re-authenticate if needed"""
        if self._token_expired():
            return self.authenticate()
        return True
    
    def _get_headers(self) -> Dict:
        """Get request headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"{self.token_type} {self.access_token}"
        return headers
    
    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula
        :return: Distance in meters
        """
        R = 6371000  # Earth radius in meters
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_phi / 2) ** 2 +
             math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def search_assets(self, 
                     latitude: float = None, 
                     longitude: float = None,
                     distance: int = None,
                     date: str = None,
                     max_rows: int = 5000) -> Optional[Dict]:
        """
        Search for assets (AEDs) matching criteria
        
        :param latitude: Latitude of search center
        :param longitude: Longitude of search center
        :param distance: Search distance in meters
        :param date: Date in DD-Mon-YYYY format for opening hours evaluation
        :param max_rows: Maximum number of rows to return
        :return: API response as dictionary with ASSETS list
        """
        # Ensure we have a valid token
        if not self._ensure_authenticated():
            return None
        
        params = {'max_rows': max_rows}
        
        if latitude is not None and longitude is not None:
            params['latitude'] = latitude
            params['longitude'] = longitude
        
        if distance is not None:
            params['distance'] = distance
        
        if date is None:
            # Use today's date in DD-Mon-YYYY format
            today = datetime.now()
            date = today.strftime('%d-%b-%Y')
        
        params['date'] = date
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/assets/search/",
                params=params,
                headers=self._get_headers(),
                timeout=15
            )
            
            # Handle 401 Unauthorized - token may have expired
            if response.status_code == 401:
                print("⚠ Token expired, re-authenticating...")
                if self.authenticate():
                    # Retry the request with new token
                    response = self.session.get(
                        f"{self.BASE_URL}/assets/search/",
                        params=params,
                        headers=self._get_headers(),
                        timeout=15
                    )
                else:
                    print("✗ Re-authentication failed")
                    return None
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Error searching assets: {e}")
            return None
    
    def search_available_aeds(self,
                             latitude: float = None,
                             longitude: float = None,
                             distance: int = None) -> List[Dict]:
        """
        Search for ONLY available (open) AEDs in specified location
        
        :param latitude: Latitude of search center (default: Kristiansand)
        :param longitude: Longitude of search center (default: Kristiansand)
        :param distance: Search distance in meters (default: 15 km)
        :return: List of available AEDs sorted by distance
        """
        # Use Kristiansand defaults if not provided
        if latitude is None:
            latitude = self.KRISTIANSAND_CENTER["latitude"]
        if longitude is None:
            longitude = self.KRISTIANSAND_CENTER["longitude"]
        if distance is None:
            distance = self.DEFAULT_SEARCH_RADIUS
        
        # Search for assets
        response = self.search_assets(
            latitude=latitude,
            longitude=longitude,
            distance=distance
        )
        
        if not response or 'ASSETS' not in response:
            return []
        
        # Filter to only OPEN and ACTIVE AEDs
        available_aeds = []
        
        for asset in response['ASSETS']:
            # Filter criteria:
            # 1. Must be OPEN (IS_OPEN == "Y")
            # 2. Must be ACTIVE (ACTIVE == "Y")
            # 3. Must have location data
            
            if (asset.get('IS_OPEN') == 'Y' and
                asset.get('ACTIVE') == 'Y' and
                asset.get('SITE_LATITUDE') and
                asset.get('SITE_LONGITUDE')):
                
                # Calculate distance from search center
                dist_meters = self._haversine_distance(
                    latitude,
                    longitude,
                    float(asset['SITE_LATITUDE']),
                    float(asset['SITE_LONGITUDE'])
                )
                
                # Prepare AED record with distance
                aed_record = {
                    'asset_id': asset.get('ASSET_ID'),
                    'site_name': asset.get('SITE_NAME'),
                    'site_address': asset.get('SITE_ADDRESS'),
                    'site_post_code': asset.get('SITE_POST_CODE'),
                    'site_post_area': asset.get('SITE_POST_AREA'),
                    'opening_hours_text': asset.get('OPENING_HOURS_TEXT'),
                    'site_latitude': float(asset.get('SITE_LATITUDE')),
                    'site_longitude': float(asset.get('SITE_LONGITUDE')),
                    'distance_meters': round(dist_meters, 0),
                    'distance_km': round(dist_meters / 1000, 2),
                    'site_description': asset.get('SITE_DESCRIPTION'),
                    'site_access_info': asset.get('SITE_ACCESS_INFO'),
                    'serial_number': asset.get('SERIAL_NUMBER'),
                    'asset_status': asset.get('ASSET_STATUS'),
                }
                
                available_aeds.append(aed_record)
        
        # Sort by distance (nearest first)
        available_aeds.sort(key=lambda x: x['distance_meters'])
        
        return available_aeds
    
    def convert_to_geojson(self, api_response: Dict) -> Dict:
        """
        Convert API response to GeoJSON format
        
        :param api_response: Response from API search methods
        :return: GeoJSON FeatureCollection
        """
        if not api_response or 'ASSETS' not in api_response:
            return {"type": "FeatureCollection", "features": []}
        
        features = []
        
        for asset in api_response['ASSETS']:
            # Skip if no location data
            if not asset.get('SITE_LATITUDE') or not asset.get('SITE_LONGITUDE'):
                continue
            
            properties = {
                'asset_id': asset.get('ASSET_ID'),
                'asset_guid': asset.get('ASSET_GUID'),
                'site_name': asset.get('SITE_NAME'),
                'site_address': asset.get('SITE_ADDRESS'),
                'site_post_code': asset.get('SITE_POST_CODE'),
                'site_post_area': asset.get('SITE_POST_AREA'),
                'site_floor_number': asset.get('SITE_FLOOR_NUMBER'),
                'site_description': asset.get('SITE_DESCRIPTION'),
                'site_access_info': asset.get('SITE_ACCESS_INFO'),
                'opening_hours_text': asset.get('OPENING_HOURS_TEXT'),
                'asset_type_name': asset.get('ASSET_TYPE_NAME'),
                'serial_number': asset.get('SERIAL_NUMBER'),
                'is_active': asset.get('ACTIVE') == 'Y',
                'is_open': asset.get('IS_OPEN') == 'Y',
                'is_available': asset.get('IS_OPEN') == 'Y',
                'is_open_status': asset.get('IS_OPEN', 'N'),
                'asset_status': asset.get('ASSET_STATUS'),
                'created_date': asset.get('CREATED_DATE'),
                'modified_date': asset.get('MODIFIED_DATE'),
            }
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        asset['SITE_LONGITUDE'],
                        asset['SITE_LATITUDE']
                    ]
                },
                "properties": properties
            }
            
            features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "total_count": len(features),
                "api_message": api_response.get('API_MESSAGE'),
                "current_user_id": api_response.get('API_CURRENT_USER_ID')
            }
        }
