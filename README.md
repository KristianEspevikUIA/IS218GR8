# Interactive Web Map - MVC Architecture

## Project Overview

**InteractiveMap** is a responsive web mapping application that combines static GeoJSON data, external OGC APIs, and optional spatial database services (PostGIS/Supabase) into a single interactive cartographic experience. Built with **Leaflet.js** and structured using the **Model-View-Controller (MVC)** design pattern, this application demonstrates best practices for managing geographic data flows, coordinate system transformations, and interactive map visualizations.

### TLDR
A modern web map that loads geographic data from multiple sources (GeoJSON files, OGC APIs, PostGIS databases), visualizes them with interactive popups, supports spatial filtering by distance, and uses MVC architecture for clean code separation.

---

## Features

- ✅ **Multi-source Data Loading**: GeoJSON files + OGC APIs + Supabase PostGIS
- ✅ **Interactive Popups**: Click features to view detailed attribute information
- ✅ **Layer Control**: Toggle layers on/off dynamically
- ✅ **Spatial Filtering**: Search features within a specified distance radius
- ✅ **Data-Driven Styling**: Customize layer appearance based on data properties
- ✅ **MVC Architecture**: Clean separation of concerns (Models, Views, Controllers)
- ✅ **Responsive Design**: Works on desktop and mobile devices

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
| Norwegian Cities & Landmarks | Local file | GeoJSON (Point/LineString) | Manually curated from OSM data |
| GeoNorge API | External WFS/WMS | GeoJSON | Real-time fetching via HTTP |
| PostGIS Database | Supabase | JSON (via API) | SQL spatial queries with PostGIS functions |
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

### Optional: Configure Supabase
To enable PostGIS queries, create a `.env` file:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

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

### Loading GeoJSON
```javascript
const geojsonData = await dataModel.fetchGeoJSON('./data/geojson/sample.geojson');
mapView.addGeoJSONLayer('layer-id', geojsonData);
```

### Querying OGC WFS API
```javascript
const features = await dataModel.fetchOGCAPI(
  'https://www.geonorge.no/wfs',
  { 
    service: 'WFS',
    request: 'GetFeature',
    typeName: 'municipality'
  }
);
```

### Spatial Query with PostGIS
```javascript
const results = await dataModel.querySupabase(supabaseClient, 'locations', {
  building_type: 'church'
});
```

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

## License

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
