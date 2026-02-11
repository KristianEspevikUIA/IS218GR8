# Interactive Web Map - Python Flask + MVC Architecture

## Project Overview

**InteractiveMap** is a responsive Python-based web mapping application that combines static geographic data, external OGC APIs, and optional spatial database services (PostGIS/Supabase) into a single interactive cartographic experience. Built with **Flask**, **Folium**, and **GeoPandas**, this application demonstrates best practices for managing geographic data flows, coordinate system transformations, and interactive map visualizations using **MVC (Model-View-Controller)** architecture.

### TLDR
A Python Flask web map that loads geographic data from multiple sources (GeoJSON, OGC APIs, PostGIS databases), visualizes them interactively with Folium, supports spatial filtering by distance using Haversine formula, and cleanly separates concerns with MVC architecture.

---

## Features

- ✅ **Multi-source Data Loading**: GeoJSON data + OGC APIs + Supabase PostGIS support
- ✅ **Interactive Map Rendering**: Folium-based interactive map with Leaflet backend
- ✅ **Spatial Search**: Filter features within specified distance radius
- ✅ **OGC API Integration**: Support for WFS and other OGC-compliant services
- ✅ **Data-Driven Styling**: Customize layer appearance based on properties
- ✅ **MVC Architecture**: Clean separation of Models, Views, and Controllers
- ✅ **Responsive Design**: Works on desktop and mobile browsers
- ✅ **REST API**: JSON endpoints for search and data operations

---

## Technical Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.11+ | Programming language |
| **Flask** | 3.0.0 | Web framework |
| **Folium** | 0.14.0 | Interactive mapping library (Leaflet wrapper) |
| **GeoPandas** | 0.14.0 | Geographic data analysis |
| **Requests** | 2.31.0 | HTTP API calls |
| **Geopy** | 2.4.0 | Geocoding and distance calculations |

---

## Data Catalog

| Dataset | Source | Format | Processing |
|---------|--------|--------|-----------|
| Norwegian Cities & Landmarks | Embedded GeoJSON | Point/LineString features | Manually curated from OSM data |
| GeoNorge API | External WFS/WMS | GeoJSON (via fetch) | Real-time HTTP requests to OGC services |
| PostGIS Database | Supabase | JSON (via API) | SQL spatial queries with PostGIS functions |
| OpenStreetMap Basemap | Mapnik tiles | XYZ Raster Tiles | Served via CDN |

---

## Architecture Overview

```
┌──────────────────────────────────┐
│      Web Browser (HTML/JS)       │
│    http://localhost:5000         │
└────────────────┬─────────────────┘
                 │
         ┌───────▼────────┐
         │  Flask Routes  │
         │  (app/__init__.py)
         └───────┬────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼──────┐ ┌──▼─────────┐ ┌▼──────────┐
│AppCtrlr  │ │ MapView    │ │ MapModel  │
│(Logic)   │ │(Folium)    │ │(State)    │
└───┬──────┘ └──┬─────────┘ └┬──────────┘
    │           │            │
    └───────────┼────────────┘
                │
    ┌───────────▼────────────────┐
    │        DataModel           │
    │  (Data fetching & spatial  │
    │      query operations)     │
    └───────────┬────────────────┘
                │
    ┌───────────┼───────────┬──────────┐
    │           │           │          │
 ┌──▼──┐  ┌─────▼───┐  ┌────▼────┐  ┌▼─────┐
 │JSON │  │OGC API  │  │Supabase │  │Distance
 │Data │  │(WFS)    │  │(PostGIS)│  │Calc
 └─────┘  └─────────┘  └─────────┘  └──────┘
```

**MVC Components:**

**Models** (`app/models/`)
- `DataModel.py`: Data fetching from multiple sources, spatial operations (Haversine distance)
- `MapModel.py`: Map state, layer management, viewport control

**Views** (`app/views/`)
- `MapView.py`: Renders interactive Folium/Leaflet maps, layer visualization

**Controllers** (`app/controllers/`)
- `AppController.py`: Orchestrates initialization, event handling, data loading logic

**Flask App** (`app/__init__.py`)
- REST API endpoints for searching, OGC API fetching, map export

---

## Installation & Setup

### Prerequisites
- Python 3.11+ (download from https://www.python.org/)
- pip (comes with Python)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Quick Start (Windows)

1. **Clone the repository**
```bash
git clone https://github.com/KristianEspevikUIA/IS218GR8.git
cd IS218GR8
```

2. **Run the application**
Double-click `python_app/run.bat` 
OR in terminal:
```bash
cd python_app
pip install -r requirements.txt
python run.py
```

3. **Open in browser**
Navigate to `http://localhost:5000`

### Quick Start (Mac/Linux)

1. **Clone the repository**
```bash
git clone https://github.com/KristianEspevikUIA/IS218GR8.git
cd IS218GR8
```

2. **Run the application**
```bash
cd python_app
bash run.sh
```
OR manually:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 run.py
```

3. **Open in browser**
Navigate to `http://localhost:5000`

### VS Code Integration

1. Press **Ctrl+Shift+B** (or **Cmd+Shift+B** on Mac)
2. Select "Python: Run Flask Web Map" from the task menu
3. Server starts automatically on `http://localhost:5000`

---

## Usage Guide

### Basic Map Interaction
- **Pan**: Click and drag the map
- **Zoom**: Scroll wheel or use zoom controls
- **View Details**: Click on any feature to see popup

### Spatial Search
1. **Click on the map** to set the search center point
2. Enter a **radius (km)** in the right panel
3. Click **"Search by Distance"**
4. Results light up in red with search radius visualization

### OGC API Integration
Call the `/api/ogc-api` endpoint:
```bash
curl -X POST http://localhost:5000/api/ogc-api \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.geonorge.no/wfs",
    "params": {
      "service": "WFS",
      "request": "GetFeature",
      "typeName": "municipality"
    }
  }'
```

### Spatial Search via API
```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 59.9139,
    "lng": 10.7339,
    "radius_km": 50
  }'
```

---

## Project Structure

```
IS218GR8/
├── python_app/
│   ├── app/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── data_model.py      # Data fetching & spatial ops
│   │   │   └── map_model.py       # Map state management
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   └── map_view.py        # Folium map rendering
│   │   ├── controllers/
│   │   │   ├── __init__.py
│   │   │   └── app_controller.py  # Application logic
│   │   └── __init__.py            # Flask app & routes
│   ├── templates/
│   │   └── index.html             # Main template
│   ├── requirements.txt           # Python dependencies
│   ├── run.py                     # Python entry point
│   ├── run.bat                    # Windows launcher
│   └── run.sh                     # Mac/Linux launcher
├── .gitignore                     # Git ignore rules
├── README.md                      # This file
└── LICENSE                        # MIT License
```

---

## API Endpoints

### GET `/`
Renders the main map interface with data catalog

### POST `/api/search`
Spatial search by distance
- **Request**: `{"lat": float, "lng": float, "radius_km": float}`
- **Response**: `{"status": "success", "count": int, "features": [], "search_point": {}, "radius_km": float}`

### POST `/api/ogc-api`
Fetch data from OGC APIs
- **Request**: `{"url": "string", "params": {}}`
- **Response**: `{"status": "success", "message": "string"}`

### GET `/api/data-sources`
List registered data sources
- **Response**: `[{"id": "string", "name": "string", "type": "string", "visible": bool}]`

### GET `/api/export-map`
Export map as HTML file
- **Response**: `{"status": "success", "filepath": "string", "message": "string"}`

---

## Configuration

### Environment Variables (Optional)
Create `.env` file in `python_app/` directory:
```env
FLASK_ENV=development
FLASK_DEBUG=True
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

Load with:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Extending the Application

### Add a New Data Source
```python
# In AppController.setup_data_sources()
self.data_model.register_source('my-source', {
    'type': 'ogc_api',
    'name': 'My OGC Service'
})
```

### Add Custom Styling
```python
# In MapView.add_geojson_layer()
self.map_view.add_geojson_layer(
    layer_id='custom',
    features=features,
    color='#ff0000'  # Red
)
```

### Query PostGIS
```python
# In AppController
results = self.data_model.query_supabase(
    supabase_client,
    'places',
    filters={'city': 'Oslo'}
)
```

---

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

## Reflection & Improvements

### Current Strengths
- Clean MVC architecture enables testability and maintainability
- Haversine formula provides accurate geodesic distance calculations
- Folium generates interactive maps without complex setup
- Responsive design works across devices
- REST API allows external integrations

### Areas for Improvement

1. **Authentication & Security**: Currently has no authentication layer. For production, add Flask-Login and secure API endpoints with JWT tokens. Supabase API keys should never be exposed in client-side code.

2. **Performance Optimization**: Large feature collections (>10,000) may cause slow rendering. Implement server-side clustering, spatial indexing, or tile-based rendering using MapLibre GL instead of Folium.

3. **Advanced Spatial Analysis**: Current distance filtering is basic. Enhance with polygon intersection, buffer operations, and topology analysis using Shapely or PostGIS SQL queries directly.

4. **Error Handling & Logging**: Add comprehensive try-catch blocks, request validation, and logging to file for debugging production issues.

5. **Testing & CI/CD**: Implement unit tests for models, integration tests for controllers, and automated deployment pipeline using GitHub Actions.

---

## License

MIT License - See [LICENSE](LICENSE) file for details

---

## Contributors

- **Kristian Espeviksgård** - MVC architecture implementation with Python Flask & Folium

---

## Contact & Support

For issues, questions, or contributions, please open an issue on the [GitHub repository](https://github.com/KristianEspevikUIA/IS218GR8).

---

**Last Updated**: February 11, 2026  
**Language**: Python 3.11+ with Flask 3.0.0
