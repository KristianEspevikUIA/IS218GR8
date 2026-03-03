# Available AEDs - Quick Start

**Goal:** List ONLY available (currently open) AEDs in Kristiansand using Hjertestarterregister API.

## Setup (30 seconds)

1. **Add to `.env`:**
   ```env
   HJERTESTARTERREGISTER_CLIENT_ID=<your_id>
   HJERTESTARTERREGISTER_CLIENT_SECRET=<your_secret>
   ```

2. **Run:**
   ```bash
   py run.py
   ```

3. **Query:**
   ```bash
   curl http://localhost:3000/api/aeds/available
   ```


## API Endpoints

### Get Available AEDs (Full Details)
```
GET /api/aeds/available
```
- **Default location:** Kristiansand city center (58.1414°N, 8.0842°E)
- **Default radius:** 15 km

**Query params:**
- `latitude` - Search center latitude
- `longitude` - Search center longitude  
- `distance` - Radius in meters (e.g., 5000 for 5 km)

**Example:**
```bash
# Kristiansand (default)
curl http://localhost:3000/api/aeds/available

# Custom: 10 km around Oslo
curl "http://localhost:3000/api/aeds/available?latitude=59.9139&longitude=10.7522&distance=10000"
```


### Get Count Only
```
GET /api/aeds/available/count
```

Faster when you just need the count.


## Python Usage

```python
from app.models.data_model import DataModel

dm = DataModel()

# Default: Kristiansand, 15 km radius
aeds = dm.get_available_aeds()

# Custom location
aeds = dm.get_available_aeds(
    latitude=59.9139,      # Oslo
    longitude=10.7522,
    distance=5000          # 5 km
)

# Results are sorted by distance (nearest first)
for aed in aeds:
    print(f"{aed['site_name']}")
    print(f"  {aed['distance_km']} km away")
    print(f"  {aed['site_address']}")
    print(f"  Hours: {aed['opening_hours_text']}")
```


## What Gets Filtered

Only AEDs with BOTH:
- ✓ `IS_OPEN = "Y"` (open right now based on opening hours)
- ✓ `ACTIVE = "Y"` (not decommissioned)

get sorted by **distance** (nearest first).


## Response Example

```json
{
  "status": "success",
  "count": 3,
  "search_center": {
    "latitude": 58.1414,
    "longitude": 8.0842,
    "name": "Kristiansand"
  },
  "search_radius_km": 15,
  "data": [
    {
      "site_name": "Kristiansand Hospital",
      "site_address": "Hospital Street 1",
      "site_post_code": "4604",
      "site_post_area": "Kristiansand",
      "distance_km": 0.8,
      "distance_meters": 800,
      "opening_hours_text": "24/7",
      "site_latitude": 58.1355,
      "site_longitude": 8.0920
    },
    // ... more AEDs sorted by distance
  ]
}
```


## Configuration

### Change Defaults

Edit `app/models/hjertestarterregister_api.py`:

```python
# Line ~32-33
KRISTIANSAND_CENTER = {"latitude": 58.1414, "longitude": 8.0842}
DEFAULT_SEARCH_RADIUS = 15000  # meters
```


## How It Works

1. **OAuth Authentication** → Gets access token
2. **API Search** → Queries Hjertestarterregister with location + radius + today's date
3. **Filter** → Keeps only IS_OPEN="Y" and ACTIVE="Y"
4. **Distance Calc** → Haversine formula from search center
5. **Sort** → Nearest first
6. **Return** → Clean list to client

**Token Expiry?** → Auto re-authenticates on 401 response


## Common Issues

| Issue | Solution |
|-------|----------|
| 401 Auth error | Check CLIENT_ID/SECRET in `.env` |
| 0 results | AEDs might be closed; expand radius or check hours |
| ModuleNotFoundError | Run `pip install -r requirements.txt` |
| slow responses | Reduce search radius or check network |


## Full Documentation

See **AVAILABLE_AEDS_GUIDE.md** for complete details:
- Advanced configuration
- Error handling details
- Use case examples
- Architecture overview
- Troubleshooting guide

---

**Feature ready to use!** 🚀
