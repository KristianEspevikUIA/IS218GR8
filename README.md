# Interactive Web Map - MVC Architecture

## Project Overview

**InteractiveMap** is a responsive web mapping application that combines static GeoJSON data, external OGC APIs (Kartverket), and optional spatial database services (PostGIS/Supabase with Spatial SQL) into a single interactive cartographic experience. Built with **Leaflet.js** and structured using the **Model-View-Controller (MVC)** design pattern, this application demonstrates best practices for managing geographic data flows, coordinate system transformations, spatial SQL queries, and interactive map visualizations.

### TLDR
A modern web map that loads geographic data from three sources: (1) **GeoJSON files** (static), (2) **OGC APIs** (Kartverket Adresser - Norway's official geocoding service), and (3) **PostGIS databases** (Supabase with Spatial SQL functions for distance-based queries). Features interactive popups, layer toggling, and spatial filtering using PostGIS `ST_DWithin()` and `ST_Distance()` functions. Built with Leaflet and MVC architecture.

---

## Features

- ✅ **Multi-source Data Loading**: 
  - GeoJSON files (static, embedded)
  - OGC APIs (Kartverket Adresser - Norwegian geocoding service)
  - PostGIS databases (Supabase with Spatial SQL) *(optional)*
- ✅ **Interactive Popups**: Click features to view detailed attribute information
- ✅ **Layer Control**: Toggle data layers on/off dynamically with visual indicators
- ✅ **Spatial Filtering**: Search features within specified distance radius (Haversine formula)
- ✅ **Spatial SQL Functions**: 
  - `ST_DWithin()` - Distance-based queries on PostGIS geometry
  - `ST_GeomFromText()` - Create geometries from WKT
  - Spatial indexing with GIST for query optimization
- ✅ **Data-Driven Styling**: Customize layer appearance based on data properties
- ✅ **MVC Architecture**: Clean separation of concerns (Models, Views, Controllers)
- ✅ **Responsive Design**: Works on desktop and mobile devices
- ✅ **Official OGC API Integration**: Kartverket (Norwegian mapping authority services)
- ✅ **PostGIS Support**: Full spatial database integration with Spatial SQL

---

## Technical Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| **Leaflet.js** | 1.9.4 | Interactive mapping library |
| **Supabase** | 2.38.4 | PostGIS database client (optional) |
| **HTML5** | 2023 | Markup structure |
| **CSS3** | 2023 | Styling and layout |
| **JavaScript (ES6)** | 2015+ | Logic and interactivity |
| **GeoJSON** | RFC 7946 | Geographic data format |

---

## Data Catalog

| Dataset | Source | Format | Processing |
|---------|--------|--------|-----------|
| Norwegian Cities & Landmarks | Local file | GeoJSON (Point/LineString) | Manually curated from OSM data; embedded in HTML |
| **Kartverket Adresser API** | Kartverket (Official) | JSON → GeoJSON (Point) | Real-time fetching from Kartverket API; converts address data to map features |
| **PostGIS Database** | Supabase (Optional) | JSON (via PostGIS API) | Optional spatial queries; requires Supabase configuration |
| Map Tiles | OpenStreetMap | XYZ Tiles | Served via CDN from Mapnik |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│            User Interface / Browser              │
│                  (index.html)                    │
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
    ┌───▼─────┐  ┌──▼──────┐  ┌──▼──────┐
    │ MapView │  │ UIView  │  │AppCtrlr │
    │ (DOM)   │  │(Events) │  │(Logic)  │
    └───┬─────┘  └──┬──────┘  └──┬──────┘
        │           │            │
        └───────────┼────────────┘
                    │
    ┌───────────────▼────────────────┐
    │      MapModel / DataModel      │
    │    (State & Data Management)   │
    └───────────────┬────────────────┘
                    │
        ┌───────────┼──────────┬──────────┐
        │           │          │          │
    ┌───▼─┐ ┌──────▼──┐ ┌────▼────┐ ┌──▼─────┐
    │JSON │ │OGC API  │ │Supabase │ │Caching │
    │File │ │(WFS)    │ │(PostGIS)│ │ Layer  │
    └─────┘ └─────────┘ └─────────┘ └────────┘
```

### MVC Components:

**Models** (`src/models/`)
- `MapModel.js`: Manages map state, layers, viewport, and spatial filters
- `DataModel.js`: Handles data fetching from multiple sources with caching

**Views** (`src/views/`)
- `MapView.js`: Renders Leaflet map, GeoJSON layers, markers, popups
- `UIView.js`: Manages UI controls, layer toggles, search panel, notifications

**Controllers** (`src/controllers/`)
- `AppController.js`: Orchestrates application flow, event handling, data loading

---

## Installation & Setup

### Prerequisites
- Node.js (optional, for package management)
- Python 3.x (for local development server)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/KristianEspevikUIA/IS218GR8.git
cd IS218GR8
```

2. **Install dependencies** (optional, if using npm)
```bash
npm install
```

3. **Start local development server**
```bash
# Using Python
python -m http.server 8000

# Or using npm
npm start
```

4. **Access the application**
Open http://localhost:8000 in your browser

---

## Demo & Testing 🎬

### How to Create a Demo Video/GIF

**Option 1: Using ScreenToGif (Windows)**
1. Download [ScreenToGif](https://www.screentogif.com/)
2. Open the app and start recording
3. Interact with the map:
   - Pan/zoom around Norway
   - Click on features to see popups
   - Toggle layers on/off with checkboxes
   - Click map → enter radius → click Search to see distance-based filtering
4. Stop recording and export as **GIF** or **MP4**
5. Save to `/docs/demo.gif` in your repo

**Option 2: Using OBS (Mac/Windows/Linux)**
1. Download [OBS Studio](https://obsproject.com/)
2. Set up scene with browser window
3. Record the same interactions (30 seconds - 1 minute demo)
4. Export as MP4

**Demo Checklist - What to Show:**
- ✅ Load the map with all three data layers visible
- ✅ Show **GeoJSON layer** (blue local data)
- ✅ Show **Kartverket API layer** (orange churches)
- ✅ Toggle layer visibility using checkboxes
- ✅ Click on a feature to show popup with attributes
- ✅ Click on map → enter search radius (e.g., 50 km) → Search to show spatial filtering
- ✅ (Optional) Show Supabase PostGIS layer if configured (green points)

---

## Database Access Guide 🗄️

### Quick Setup (5 minutes)

**Step 1: Create Supabase Account**
1. Go to [supabase.com](https://supabase.com)
2. Sign up with GitHub or email
3. Create new project: name it `IS218GR8`, choose closest region
4. Wait 2-3 minutes for initialization

**Step 2: Enable PostGIS**
In **SQL Editor**, run:
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

**Step 3: Create Locations Table**
```sql
CREATE TABLE IF NOT EXISTS locations (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT,
  description TEXT,
  geometry GEOMETRY(Point, 4326) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_locations_geometry ON locations USING GIST(geometry);

-- Insert sample Norwegian churches with spatial geometry
INSERT INTO locations (name, category, description, geometry) VALUES
  ('Oslo Cathedral', 'church', 'Historic cathedral', ST_GeomFromText('POINT(10.7339 59.9139)', 4326)),
  ('Bergen Cathedral', 'church', 'Cathedral in coastal city', ST_GeomFromText('POINT(5.3221 60.3913)', 4326)),
  ('Stavanger Cathedral', 'church', 'Ancient cathedral', ST_GeomFromText('POINT(5.7331 58.9699)', 4326)),
  ('Trondheim Cathedral', 'church', 'Nidaros Cathedral', ST_GeomFromText('POINT(10.3951 63.4269)', 4326)),
  ('Tromsø Arctic Cathedral', 'church', 'Northern cathedral', ST_GeomFromText('POINT(18.9553 69.6492)', 4326));

ALTER TABLE locations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow public read" ON locations FOR SELECT USING (true);
```

**Step 4: Create PostGIS Spatial SQL Function**
```sql
CREATE OR REPLACE FUNCTION find_nearby_locations(
  p_longitude FLOAT,
  p_latitude FLOAT,
  p_distance INT
)
RETURNS TABLE (
  id BIGINT,
  name TEXT,
  category TEXT,
  description TEXT,
  geometry GEOMETRY
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    l.id, l.name, l.category, l.description, l.geometry
  FROM locations l
  WHERE ST_DWithin(
    l.geometry,
    ST_GeomFromText('POINT(' || p_longitude || ' ' || p_latitude || ')', 4326),
    p_distance
  )
  ORDER BY ST_Distance(l.geometry, ST_GeomFromText('POINT(' || p_longitude || ' ' || p_latitude || ')', 4326));
END;
$$ LANGUAGE plpgsql;
```

**Step 5: Get Your API Keys**
1. Go to **Settings → API**
2. Copy:
   - **Project URL**: `https://[uuid].supabase.co`
   - **anon key**: `eyJ0eXAi...` (long string)

**Step 6: Configure App**
Edit `index.html` (lines 27-32):
```javascript
window.SUPABASE_CONFIG = {
  projectUrl: 'https://YOUR-UUID.supabase.co',    // ← Replace this
  anonKey: 'YOUR-ACTUAL-ANON-KEY'                 // ← Replace this
};
```

**Step 7: Verify It Works**
- Reload http://localhost:8000
- Look for **green layer "Supabase PostGIS"** in map
- If green points appear = ✅ Success!

### Testing Spatial SQL Queries Directly

In Supabase **SQL Editor**, test these queries:

```sql
-- See all locations
SELECT id, name, ST_AsText(geometry) as point FROM locations;

-- Find locations within 50km of Oslo (Spatial SQL: ST_DWithin)
SELECT id, name, ST_Distance(geometry, ST_GeomFromText('POINT(10.7339 59.9139)', 4326)) / 1000 as distance_km
FROM locations
WHERE ST_DWithin(geometry, ST_GeomFromText('POINT(10.7339 59.9139)', 4326), 50000)
ORDER BY distance_km;

-- Call the PostGIS function
SELECT * FROM find_nearby_locations(10.7339, 59.9139, 50000);
```

### Troubleshooting

| Problem | Solution |
|---------|----------|
| Green layer doesn't appear | Check browser console for errors; verify API keys in index.html |
| "Extension not found" error | Make sure you ran `CREATE EXTENSION postgis` first |
| Can't find RPC function | Refresh browser; may take 1-2 min to propagate |
| "Row-Level Security" error | Verify RLS policy: `CREATE POLICY` statement must run |
| Clicking doesn't load data | Check Supabase credentials are correct (no spaces/typos) |

---

### 1. External OGC API (Kartverket Adresser API - Built-in) ✅
The application includes **Kartverket Adresser API** - the official Norwegian geocoding service from Kartverket (Norwegian mapping authority).
- ✅ No configuration needed - works out-of-the-box
- Searches for "kirke" (churches/religious buildings) across all of Norway
- Returns address data from official Norwegian register with coordinate geometry
- CORS-enabled REST API endpoint: `https://ws.geonorge.no/adresser/v1/sok`
- Data includes: address name, postal code, postal area, municipality, county
- Layer displayed as **orange markers** on the map

### 2. Optional: Configure Supabase PostGIS with Spatial SQL
To enable spatial queries from your own PostGIS database via Supabase *(combines external API + spatial database)*:

**Step 1: Create Supabase Project with PostGIS**
1. Go to https://supabase.com and sign up / login
2. Create a new project (or use existing)
3. Go to **SQL Editor** and enable PostGIS extension:
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```

**Step 2: Create Spatial Table with Geometry Column**
```sql
-- Create table with PostGIS GEOMETRY column (supports Spatial SQL)
CREATE TABLE locations (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT,
  description TEXT,
  geometry GEOMETRY(Point, 4326),  -- PostGIS geometry column (WGS84)
  created_at TIMESTAMP DEFAULT NOW()
);

-- Create spatial index for faster queries
CREATE INDEX idx_locations_geometry ON locations USING GIST(geometry);

-- Insert sample data with ST_GeomFromText (Spatial SQL function)
INSERT INTO locations (name, category, description, geometry) VALUES
  ('Oslo Cathedral', 'religion', 'Historic cathedral in Oslo', ST_GeomFromText('POINT(10.7339 59.9139)', 4326)),
  ('Bergen Museum', 'museum', 'Maritime museum in Bergen', ST_GeomFromText('POINT(5.3221 60.3913)', 4326)),
  ('Stavanger Cathedral', 'religion', 'Ancient cathedral', ST_GeomFromText('POINT(5.7331 58.9699)', 4326));

-- Enable Row-Level Security (allow public read)
ALTER TABLE locations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow public read" ON locations FOR SELECT USING (true);
```

**Step 3: Create PostGIS Spatial SQL Function (Distance-based Query)**
```sql
-- Create PL/pgSQL function using ST_DWithin (Spatial SQL)
-- This function finds all locations within a distance radius
CREATE OR REPLACE FUNCTION find_nearby_locations(
  p_longitude FLOAT,
  p_latitude FLOAT,
  p_distance INT
)
RETURNS TABLE (
  id BIGINT,
  name TEXT,
  category TEXT,
  description TEXT,
  geometry GEOMETRY
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    l.id,
    l.name,
    l.category,
    l.description,
    l.geometry
  FROM locations l
  WHERE ST_DWithin(
    l.geometry,
    ST_GeomFromText('POINT(' || p_longitude || ' ' || p_latitude || ')', 4326),
    p_distance
  );
END;
$$ LANGUAGE plpgsql;

-- Example: Query function from application
-- SELECT * FROM find_nearby_locations(10.7339, 59.9139, 50000);
-- This finds all locations within 50km of Oslo
```

**Step 4: Configure in Application**
Edit `index.html` and configure Supabase credentials:
```javascript
window.SUPABASE_CONFIG = {
  projectUrl: 'https://your-project.supabase.co',

  anonKey: 'your-actual-anon-key'
};
```

Get your credentials from: **Settings → API → Project URL & anon key**

---

## Usage

### Basic Map Interaction
- **Pan**: Click and drag the map
- **Zoom**: Scroll wheel or +/- buttons
- **View Details**: Click on any feature (point/line) to see a popup

### Layer Control
- Use the **Layer Control** panel on the right to toggle data layers on/off
- Each layer can be individually controlled

### Spatial Search
1. **Click on the map** to set the search center point
2. Enter a **radius (km)** in the search panel
3. Click **Search** to find all features within that distance
4. Results are highlighted in red with a dashed circle visualization

### Data Inspection
- Scroll down to view the **Data Catalog** table
- See metadata about each dataset source and format

---

## API Integration Examples

### Loading GeoJSON from File
```javascript
const geojsonData = await dataModel.fetchGeoJSON('./data/geojson/sample.geojson');
mapView.addGeoJSONLayer('layer-id', geojsonData);
```

### Querying OGC API (Kartverket Adresser API - Already Integrated!) ✅
```javascript
// This is already configured and runs automatically
const kartverketResponse = await dataModel.fetchOGCAPI(
  'https://ws.geonorge.no/adresser/v1/sok',
  { 
    sok: 'kirke',              // Search for churches
    treffPerSide: 50,          // Max 50 results per page
    asciiKompatibel: true      // ASCII-compatible output
  }
);

// Convert Kartverket response to GeoJSON
const geojsonData = {
  type: 'FeatureCollection',
  features: kartverketResponse.adresser.map(addr => ({
    type: 'Feature',
    geometry: {
      type: 'Point',
      coordinates: [addr.representasjonspunkt.lon, addr.representasjonspunkt.lat]
    },
    properties: {
      navn: addr.adressetekst,
      postnummer: addr.postnummer,
      poststed: addr.poststed,
      kommune: addr.kommune,
      fylke: addr.fylke
    }
  }))
};

mapView.addGeoJSONLayer('ogc-api-external', geojsonData, { color: '#ff8c00' });
```

**API Source:** [Kartverket Adresser API](https://ws.geonorge.no/adresser/v1/) - Official Norwegian address geocoding service

### Spatial Query with PostGIS (Supabase - Optional) ⚙️
```javascript
// 1. Basic query: Load all locations from PostGIS table
const allLocations = await dataModel.querySupabaseWithSpatial(
  window.SUPABASE_CLIENT,
  'locations'  // Table with geometry column
);

// 2. Distance-based spatial query using ST_DWithin (requires RPC function)
const nearbyLocations = await dataModel.querySupabaseWithinDistance(
  window.SUPABASE_CLIENT,
  'locations',
  10.7339,    // longitude
  59.9139,    // latitude
  50000       // radius in meters (50km)
);
// Uses PostGIS Spatial SQL: ST_DWithin(geometry, point, distance)
```

**PostGIS Spatial SQL Functions Used:**
- `ST_GeomFromText()` - Create geometry from WKT text
- `ST_DWithin()` - Find geometries within distance (with spatial index support)
- `ST_Distance()` - Calculate distance between geometries
- `ST_Intersects()` - Test if geometries intersect
- Spatial indexing with `GIST` for performance optimization

---

## Project Structure

```
IS218GR8/
├── index.html                 # Main entry point
├── package.json              # Dependencies
├── .gitignore                # Git ignore rules
├── README.md                 # This file
├── src/
│   ├── models/
│   │   ├── MapModel.js       # Map state management
│   │   └── DataModel.js      # Data source & spatial operations
│   ├── views/
│   │   ├── MapView.js        # Leaflet map rendering
│   │   └── UIView.js         # UI controls & events
│   └── controllers/
│       └── AppController.js  # Application orchestration
├── data/
│   └── geojson/
│       └── sample.geojson    # Test geographic data
├── assets/
│   ├── css/
│   │   └── main.css          # Application styles
│   └── images/               # Images & icons
└── LICENSE                   # MIT License
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
- Clean MVC architecture makes code maintainable and testable
- Efficient data caching prevents redundant API calls
- Responsive design works across different screen sizes
- Haversine formula correctly calculates geodesic distances

### Areas for Improvement

1. **Authentication & Security**: Implement user authentication for API endpoints; currently, Supabase keys are exposed in client-side code. Should use secure backend proxy or row-level security policies.

2. **Performance Optimization**: For large datasets (>10,000 features), implement clustering, virtual scrolling, and spatial indexing. Current implementation may struggle with massive feature collections.

3. **Enhanced Styling System**: Move from simple color-based styling to more sophisticated data-driven styling using feature properties (e.g., color by population, size by density). Consider integrating MapLibre GL for better performance with complex styles.

4. **Advanced Spatial Queries**: Extend beyond distance-based filtering to support polygon intersection, buffer operations, and topology analysis using a proper GIS library like Turf.js.

5. **Accessibility & Internationalization**: Add keyboard navigation, screen reader support, and multi-language interface to improve user accessibility. Currently lacks WCAG 2.1 compliance.

---

## Submission Checklist ✅

This project fulfills all assignment requirements:

| Requirement | Status | Location |
|------------|--------|----------|
| **Mapping Library** (Leaflet/MapLibre) | ✅ | Leaflet 1.9.4 (CDN) |
| **GeoJSON File** | ✅ | `data/geojson/sample.geojson` + embedded in HTML |
| **External OGC API** | ✅ | Kartverket Adresser API (`ws.geonorge.no/adresser/v1/sok`) |
| **Spatial Database (PostGIS)** | ✅ | Supabase with SQL functions: `ST_DWithin()`, `ST_Distance()` |
| **Interactive Features** (Popups) | ✅ | Click any feature to see attributes |
| **Layer Control** (Toggle On/Off) | ✅ | Checkboxes in left panel |
| **Spatial Filtering** (Distance-based) | ✅ | Click map → click "Search" with radius |
| **Data-Driven Styling** | ✅ | Different colors per layer |
| **README.md Documentation** | ✅ | This file |
  - Project name & TLDR | ✅ | Lines 1-8 |
  - Demo instructions | ✅ | Demo & Testing section |
  - Technical Stack | ✅ | Table (lines 37-44) |
  - Data Catalog | ✅ | Table (lines 46-53) |
  - Architecture Diagram | ✅ | ASCII diagram (lines 65-81) |
  - Reflection/Improvements | ✅ | Reflection & Improvements section |
  - Database Access Guide | ✅ | Database Access Guide section |

---

## How to Submit to Canvas

### Step 1: Commit Your Code to GitHub

```bash
# Navigate to your project
cd c:\Users\krist\IS218GR8

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit with message
git commit -m "feat: Complete web map with Leaflet, Kartverket API, and PostGIS

- Implements GeoJSON loading (local file)
- Integrates Kartverket Adresser API for Norwegian address geocoding
- Configures Supabase PostGIS with spatial SQL functions
- Adds interactive layer control, popups, and distance-based filtering
- Provides complete documentation and database setup guide"

# Push to GitHub
git push -u origin main
```

### Step 2: Get the Commit Link

1. Go to your GitHub repo: **https://github.com/KristianEspevikUIA/IS218GR8**
2. Click on the commit hash (latest commit)
3. Copy the full URL from address bar
4. Example format: `https://github.com/KristianEspevikUIA/IS218GR8/commit/abc123def456...`

### Step 3: Submit to Canvas

1. Log into **Canvas**
2. Go to **Course → IS-218 → Assignments**
3. Find the assignment submission box
4. Paste the GitHub commit link in the submission field
5. **Submit before deadline!**

---

## Local Testing Before Submission

```bash
# Start local server
python -m http.server 8000

# Or with Node.js
npm start

# Visit: http://localhost:8000
```

**Verify in browser:**
- ✅ Map loads with three layers
- ✅ Blue layer: Local GeoJSON landmarks
- ✅ Orange layer: Kartverket churches (50 results)
- ✅ Green layer: Supabase PostGIS (if configured)
- ✅ Layer checkboxes toggle visibility
- ✅ Clicking features shows popups
- ✅ Click map → search with radius shows filtering
- ✅ No console errors

---

MIT License - See [LICENSE](LICENSE) file for details

---

## Contributors

- **Kristian Espeviksgård** - Initial MVC implementation & documentation

---

## Contact & Support

For issues, questions, or contributions, please open an issue on the [GitHub repository](https://github.com/KristianEspevikUIA/IS218GR8).

---

**Last Updated**: February 10, 2026
Repo for gruppe 8 i IS-218
