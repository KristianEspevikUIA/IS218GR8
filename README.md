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
- **Python 3.11+** (download from https://www.python.org/)
- **pip** (included with Python)
- **Visual Studio Code** (optional but recommended)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Quick Start - VS Code (Recommended ⭐)

**Fastest way to run the application on Windows or Mac:**

1. **Open the project in VS Code**
```bash
git clone https://github.com/KristianEspevikUIA/IS218GR8.git
cd IS218GR8
code .
```

2. **Install Python Extension**
   - Open Extensions (Ctrl+Shift+X)
   - Search for "Python"
   - Install the official Python extension by Microsoft

3. **Run with Ctrl+Shift+B**
   - Press **Ctrl+Shift+B** (Windows) or **Cmd+Shift+B** (Mac)
   - Select "**Run Flask Web Map**" task
   - VS Code automatically installs dependencies and starts the server

4. **Open in browser**
   - Navigate to `http://localhost:5000`
   - Map loads with interactive features ready to use

**OR Debug with F5:**
   - Press **F5** to launch Flask with Python debugger attached
   - Set breakpoints in code
   - Server runs on `http://localhost:5000`

### Quick Start - Command Line (Windows)

1. **Clone and enter directory**
```bash
git clone https://github.com/KristianEspevikUIA/IS218GR8.git
cd IS218GR8
```

2. **Install dependencies**
```bash
python -m pip install -r requirements.txt
```

3. **Run the server**
```bash
python run.py
```

4. **Open in browser**
Navigate to `http://localhost:5000`

### Quick Start - Command Line (Mac/Linux)

1. **Clone and enter directory**
```bash
git clone https://github.com/KristianEspevikUIA/IS218GR8.git
cd IS218GR8
```

2. **Create virtual environment** (optional but recommended)
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the server**
```bash
python3 run.py
```

5. **Open in browser**
Navigate to `http://localhost:5000`

---

## VS Code Quick Reference

### Keyboard Shortcuts

| Action | Windows | Mac |
|--------|---------|-----|
| **Run Flask Server** | Ctrl+Shift+B | Cmd+Shift+B |
| **Debug Flask (F5)** | F5 | F5 |
| **Open Terminal** | Ctrl+` | Ctrl+` |
| **Run Task** | Ctrl+Shift+B | Cmd+Shift+B |

### Step-by-Step: Running from VS Code

**1. Open the workspace folder**
```
File > Open Folder > IS218GR8
```

**2. Install Python extension** (if not already installed)
```
Ctrl+Shift+X > Search "Python" > Install
```

**3. Select Python interpreter** (optional but recommended)
```
Ctrl+Shift+P > "Python: Select Interpreter" > Choose 3.11 or higher
```

**4. Start the server with Ctrl+Shift+B**
```
Ctrl+Shift+B (Windows) or Cmd+Shift+B (Mac)
↓
Choose "Run Flask Web Map"
↓
Dependencies install automatically
↓
Server starts on http://localhost:5000
↓
Flask outputs: "Running on http://127.0.0.1:5000"
```

**5. Open browser and navigate to**
```
http://localhost:5000
```

### Debugging in VS Code

Press **F5** to start Flask with debugger attached:
```
F5
↓
Server starts in debug mode
↓
Set breakpoints by clicking left margin in code
↓
Debugger stops at breakpoints when code runs
↓
Step through code with F10 (step over) or F11 (step into)
```

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
├── app/
│   ├── __init__.py                # Flask app initialization & routes
│   ├── models/
│   │   ├── __init__.py
│   │   ├── data_model.py          # Data fetching & spatial operations
│   │   └── map_model.py           # Map state management
│   ├── views/
│   │   ├── __init__.py
│   │   └── map_view.py            # Folium map rendering
│   └── controllers/
│       ├── __init__.py
│       └── app_controller.py      # Application orchestration & logic
├── templates/
│   └── index.html                 # Jinja2 template for web UI
├── .vscode/
│   ├── tasks.json                 # VS Code build tasks (cross-platform)
│   └── launch.json                # VS Code Python debugger config
├── run.py                         # Flask entry point
├── requirements.txt               # Python dependencies
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
