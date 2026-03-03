# Available AEDs Feature - Complete Guide

## Overview

This feature lists **ONLY available (currently open) AEDs (Automated External Defibrillators)** in Kristiansand/Agder using the **Hjertestarterregister API v1**.

The system:
- ✓ Authenticates with OAuth 2.0 (client credentials)
- ✓ Filters to show ONLY AEDs that are:
  - **IS_OPEN = "Y"** (currently accepting visits)
  - **ACTIVE = "Y"** (not removed/decommissioned)
  - Have valid location data
- ✓ Calculates distance using Haversine formula
- ✓ Sorts results by nearest first
- ✓ Handles token expiry automatically (re-authenticates on 401 response)
- ✓ Displays comprehensive information (name, address, opening hours, coordinates)


## Environment Setup

### Required Environment Variables

Add these to your `.env` file:

```env
SUPABASE_URL=<your_supabase_url>
SUPABASE_ANON_KEY=<your_supabase_key>

HJERTESTARTERREGISTER_CLIENT_ID=<your_client_id>
HJERTESTARTERREGISTER_CLIENT_SECRET=<your_client_secret>
```

To obtain Hjertestarterregister credentials:
1. Contact the API provider at https://hjertestarterregister.113.no/
2. Register as a developer
3. Create an OAuth application with `client_credentials` grant type
4. Copy your Client ID and Client Secret to the `.env` file

**Note:** The app will warn if credentials are missing but will still function with limited data.


## How to Run

### 1. Install Dependencies
```bash
py -m pip install -r requirements.txt
```

### 2. Start the Flask Server
```bash
py run.py
```

The server will start on **http://localhost:3000**


### 3. Query Available AEDs via API

#### Get Available AEDs (Full Details)
```bash
GET /api/aeds/available
```

**Response:**
```json
{
  "status": "success",
  "count": 8,
  "search_center": {
    "latitude": 58.1414,
    "longitude": 8.0842,
    "name": "Kristiansand"
  },
  "search_radius_km": 15,
  "data": [
    {
      "asset_id": "AED001",
      "site_name": "Kristiansand City Hall",
      "site_address": "Dronningens gt. 1",
      "site_post_code": "4610",
      "site_post_area": "Kristiansand",
      "opening_hours_text": "Monday-Friday 09:00-17:00",
      "distance_km": 0.25,
      "distance_meters": 250,
      "site_latitude": 58.1422,
      "site_longitude": 8.0856,
      "serial_number": "ABC123456",
      "site_description": "Inside main entrance",
      "site_access_info": "Public access during office hours",
      "asset_status": "Active"
    },
    // ... more AEDs sorted by distance
  ]
}
```

#### Get Count Only
```bash
GET /api/aeds/available/count
```

**Response:**
```json
{
  "status": "success",
  "count": 8,
  "search_center": {
    "latitude": 58.1414,
    "longitude": 8.0842
  },
  "search_radius_km": 15
}
```


## Customization

### Change Search Center and Radius

#### Using Query Parameters:
```bash
# Search 20 km around Oslo city center
GET /api/aeds/available?latitude=59.9139&longitude=10.7522&distance=20000

# Search 5 km around a custom location
GET /api/aeds/available?latitude=58.5&longitude=8.5&distance=5000
```

#### Programmatically (in Python):
```python
from app.models.data_model import DataModel

data_model = DataModel()

# Get available AEDs around Kristiansand (default)
aeds = data_model.get_available_aeds()

# Get available AEDs around Oslo (20 km radius)
aeds = data_model.get_available_aeds(
    latitude=59.9139,
    longitude=10.7522,
    distance=20000  # 20 km in meters
)

# Print results
for aed in aeds:
    print(f"{aed['site_name']} - {aed['distance_km']} km away")
    print(f"  Address: {aed['site_address']}")
    print(f"  Hours: {aed['opening_hours_text']}")
    print()
```

### Default Search Configuration

The defaults are configured in `app/models/hjertestarterregister_api.py`:

```python
# Kristiansand city center coordinates
KRISTIANSAND_CENTER = {"latitude": 58.1414, "longitude": 8.0842}
DEFAULT_SEARCH_RADIUS = 15000  # 15 km in meters
```

To change defaults, edit these constants in the HjertestarterregisterAPI class.


## API Details

### Hjertestarterregister API Information

- **Base URL:** `https://hjertestarterregister.113.no/ords/api/v1/`
- **OAuth Token Endpoint:** `https://hjertestarterregister.113.no/ords/api/oauth/token`
- **Asset Search Endpoint:** `GET /assets/search/`
- **Token Lifetime:** 3600 seconds (1 hour)
- **Authentication:** HTTP Basic Auth with Client ID:Client Secret

### Search Parameters

The underlying API accepts:
- `latitude` - Center latitude for search
- `longitude` - Center longitude for search
- `distance` - Search radius in meters
- `date` - Date in DD-Mon-YYYY format for opening hours evaluation (auto-set to today)
- `max_rows` - Max results to return (default: 5000)

### Filter Logic

The feature filters the API response to return only AEDs where:
```
IS_OPEN = "Y" AND ACTIVE = "Y" AND (has latitude AND has longitude)
```

The API itself evaluates `IS_OPEN` based on the provided date and the AED's operating hours.

### Response Fields

Each returned AED contains:
| Field | Type | Description |
|-------|------|-------------|
| `asset_id` | string | Unique AED identifier |
| `site_name` | string | Name of location |
| `site_address` | string | Street address |
| `site_post_code` | string | Postal code |
| `site_post_area` | string | City/area name |
| `opening_hours_text` | string | Human-readable opening hours |
| `site_latitude` | float | Latitude coordinate |
| `site_longitude` | float | Longitude coordinate |
| `distance_meters` | float | Distance from search center (meters) |
| `distance_km` | float | Distance from search center (km) |
| `serial_number` | string | AED serial number |
| `site_description` | string | Location description |
| `site_access_info` | string | Access instructions |
| `asset_status` | string | Current status |


## Error Handling

### No AEDs Found
```json
{
  "status": "success",
  "count": 0,
  "message": "No available AEDs found in 15.0 km radius",
  "data": []
}
```

### Authentication Failure
The system automatically handles token expiry:
1. If a request returns 401 Unauthorized, the client re-authenticates
2. A new token is obtained
3. The request is retried

If re-authentication fails (invalid credentials), you'll see:
```
⚠ Token expired, re-authenticating...
✗ Re-authentication failed
```

### API Errors
If the Hjertestarterregister API returns an error:
```json
{
  "status": "error",
  "message": "Error description"
}
```

Check:
1. Your Client ID and Client Secret are correct
2. Your credentials have not been revoked
3. The API is accessible from your network
4. Your credentials have the required scopes


## Performance Notes

- **Search Distance:** Default 15 km is balanced for city-level searches
- **Caching:** Results are NOT cached; each request hits the API
- **Response Time:** Typically 1-3 seconds depending on API responsiveness
- **Large Searches:** Searching large areas (>50 km) may take longer


## Example Use Cases

### 1. Emergency Response (Get nearest AED)
```python
available_aeds = data_model.get_available_aeds()
if available_aeds:
    nearest = available_aeds[0]  # Already sorted by distance
    print(f"Nearest AED: {nearest['site_name']}")
    print(f"Distance: {nearest['distance_km']} km")
    print(f"Address: {nearest['site_address']}")
```

### 2. Web Dashboard
```javascript
// Fetch available AEDs for current location
const button = document.getElementById('findAedsButton');
button.addEventListener('click', async () => {
  const response = await fetch('/api/aeds/available');
  const data = await response.json();
  
  if (data.count > 0) {
    displayAedsOnMap(data.data);
  } else {
    alert('No AEDs found nearby');
  }
});
```

### 3. Mobile App Integration
```python
# Get AEDs within 5 km
aeds = data_model.get_available_aeds(
    latitude=58.1414,
    longitude=8.0842,
    distance=5000
)

for aed in aeds:
    # Create marker on map
    create_map_marker(aed['site_latitude'], aed['site_longitude'], aed['site_name'])
```

### 4. Real-time Count Widget
```javascript
// Update count every 5 minutes
setInterval(async () => {
  const response = await fetch('/api/aeds/available/count');
  const data = await response.json();
  document.getElementById('aedCount').textContent = `${data.count} AEDs nearby`;
}, 5 * 60 * 1000);
```


## Troubleshooting

### Issue: "401 Client Error" without re-auth
- **Cause:** Invalid or revoked credentials
- **Solution:** Verify CLIENT_ID and CLIENT_SECRET in `.env`

### Issue: No AEDs returned even though they exist
- **Cause:** All AEDs in radius might be closed (IS_OPEN != "Y")
- **Solution:** Try expanding the search radius or checking opening hours

### Issue: "ModuleNotFoundError: No module named 'requests'"
- **Cause:** Dependencies not installed
- **Solution:** Run `py -m pip install -r requirements.txt`

### Issue: Slow response times
- **Cause:** Large search radius or poor network
- **Solution:** Reduce search radius or check network connectivity

### Issue: `python.terminal.useEnvFile` warning
- **Solution:** The `.vscode/settings.json` has been configured; restart VS Code


## Testing

### Manual API Testing (cURL)
```bash
# Get available AEDs in Kristiansand (default)
curl http://localhost:3000/api/aeds/available

# Get available AEDs around Oslo
curl "http://localhost:3000/api/aeds/available?latitude=59.9139&longitude=10.7522&distance=20000"

# Get ONLY the count
curl http://localhost:3000/api/aeds/available/count
```

### Python Testing
```python
# Create a simple test script
from app.models.data_model import DataModel

dm = DataModel()
aeds = dm.get_available_aeds()

print(f"Found {len(aeds)} available AEDs")
for aed in aeds[:5]:  # Show first 5
    print(f"  - {aed['site_name']} ({aed['distance_km']} km)")
```


## API Architecture

The feature uses a three-layer architecture:

1. **API Client Layer** (`hjertestarterregister_api.py`)
   - Handles OAuth authentication
   - Manages token lifecycle
   - Performs distance calculations
   - Applies filtering logic

2. **Data Model Layer** (`data_model.py`)
   - Provides high-level methods
   - Manages API client lifecycle

3. **Web Service Layer** (`__init__.py`)
   - Exposes REST endpoints
   - Handles HTTP requests/responses
   - Manages query parameters


## License & Attribution

This feature integrates with **Hjertestarterregister API** maintained by the Norwegian health authorities. Please ensure compliance with their terms of service and data usage policies.

- **API Documentation:** https://hjertestarterregister.113.no/
- **Data License:** Norwegian health data regulations apply


## Support

For issues with:
- **Feature Code:** Check this repository's issues
- **API Access:** Contact https://hjertestarterregister.113.no/
- **Credentials:** Contact your API provider

---

**Last Updated:** March 3, 2026
**Feature Version:** 1.0
