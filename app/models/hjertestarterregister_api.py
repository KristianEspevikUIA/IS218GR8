"""
HjertestarterregisterAPI.py - REST client for Hjertestarterregister API
Fetches AED (Automated External Defibrillator) locations from Hjertestarterregister
"""
import requests
import os
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class HjertestarterregisterAPI:
    """
    Client for Hjertestarterregister API
    API Reference: https://hjertestarterregister.113.no/ords/api/v1/
    """
    
    BASE_URL = "https://hjertestarterregister.113.no/ords/api/v1"
    OAUTH_ENDPOINT = "https://hjertestarterregister.113.no/ords/api/oauth/token"
    
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
            
            print(f"✓ Authentication successful. Token expires in {result.get('expires_in', 3600)} seconds")
            return True
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Authentication failed: {e}")
            return False
    
    def _get_headers(self) -> Dict:
        """Get request headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"{self.token_type} {self.access_token}"
        return headers
    
    def search_assets(self, 
                     latitude: float = None, 
                     longitude: float = None,
                     distance: int = None,
                     max_rows: int = 5000) -> Optional[Dict]:
        """
        Search for assets (AEDs) matching criteria
        
        :param latitude: Latitude of search center
        :param longitude: Longitude of search center
        :param distance: Search distance in meters
        :param max_rows: Maximum number of rows to return
        :return: API response as dictionary with ASSETS list
        """
        params = {'max_rows': max_rows}
        
        if latitude is not None and longitude is not None and distance is not None:
            params['latitude'] = latitude
            params['longitude'] = longitude
            params['distance'] = distance
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/assets/search/",
                params=params,
                headers=self._get_headers(),
                timeout=15
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Error searching assets: {e}")
            return None
    
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
                'asset_type_name': asset.get('ASSET_TYPE_NAME'),
                'serial_number': asset.get('SERIAL_NUMBER'),
                'is_active': asset.get('ACTIVE') == 'Y',
                'is_open': asset.get('IS_OPEN') == 'Y',
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
