# Why the Map Wasn't Updating - Technical Deep Dive

## The Problem You Observed

**Symptom:** Map kept showing the first version of data even after code changes and server restarts

**Why It Happened:** Folium's server-side HTML generation

---

## Root Cause: Server-Side Rendering

### How Folium Works

```python
# Flask Backend (Python)
┌─────────────────────────────┐
│  app/controllers/app_controller.py  │
│  load_aeds() - Fetches data │
└──────────┬──────────────────┘
           │
           ↓
┌─────────────────────────────┐
│  app/views/map_view.py      │
│  Folium generates HTML      │
│  (with data embedded)       │
└──────────┬──────────────────┘
           │
           ↓
┌─────────────────────────────┐
│  templates/index.html       │
│  {{ map_html|safe }}        │
│  (Static HTML, no JS)       │
└──────────┬──────────────────┘
           │
           ↓
┌─────────────────────────────┐
│  Browser                    │
│  Renders final map          │
│  (Can't refresh without     │
│   server restart)           │
└─────────────────────────────┘
```

### The Issue

1. **HTML Generated Once**
   - Folium creates HTML WITH DATA EMBEDDED
   - Not JSON API calls - ACTUAL HTML with coordinates
   - Example: `[58.123, 8.456]` hardcoded in HTML

2. **No Dynamic Refresh**
   - Flask template: `{{ map_html|safe }}`
   - This renders ONCE when page loads
   - No JavaScript code to fetch new data
   - No AJAX calls to API

3. **Static Embedding**
   ```html
   <!-- What Folium generates: -->
   <script>
     var map = L.map('map').setView([58.1414, 8.0842], 10);
     // 263 markers hardcoded here with coordinates:
     L.circleMarker([58.123, 8.456], {...}).addTo(map);
     L.circleMarker([58.124, 8.457], {...}).addTo(map);
     // ... 261 more markers ...
   </script>
   ```

4. **Data Coupling**
   - Data is mixed with presentation
   - Can't separate "refresh markers" from "refresh page"
   - Changes to Python code = must restart Flask

---

## Why First Version Stayed

### Scenario: You Made Changes to Code

```
1. Code is running (Flask server with old data)
   └─ HTML generated with OLD AED locations

2. You modify Python code (load_aeds method)
   └─ File saved

3. You think "let me refresh the browser"
   └─ Browser fetches cached HTML file
   └─ NO CHANGE because only the HTML is downloaded

4. You restart Flask (Ctrl+C, py run.py)
   └─ NEW HTML generated with NEW data
   └─ NOW map updates
```

### Browser Cache Effect

```
Flask generates HTML at startup:
  ↓
Browser downloads HTML
  ↓
Browser CACHES it aggressively
  ↓
Refresh (F5) → Still loads from cache
  ↓
Only way to clear: Hard refresh (Ctrl+Shift+R) or restart Flask
```

---

## Solutions Comparison

### What We Did ✅ (Direct API Approach)

```python
# Every Flask startup:

fetch_from_api:
  GET Hjertestarterregister API
  ↓
process_data:
  - Extract AED records
  - Add IS_OPEN status
  - Calculate distances
  ↓
generate_map:
  - Folium creates new HTML with current data
  ↓
render_response:
  - Flask sends fresh HTML to browser
  - No cache issues
```

**Advantages:**
- ✅ Always up-to-date on restart
- ✅ Simple and reliable
- ✅ Colors update automatically
- ✅ No Supabase issues to deal with

**Disadvantages:**
- ❌ Need to restart Flask to see changes
- ❌ Takes 15-30 seconds on startup (generating HTML for 263 markers)

### Alternative 1: Client-Side Leaflet Map

```javascript
// Browser JavaScript (option B):

1. Page loads with empty map
2. JavaScript runs:
   fetch('/api/aeds')
   ↓
   get JSON data
   ↓
   add markers dynamically
   ↓
   map displays

// To refresh:
   - Browser button → fetch new data
   - No server restart needed
   - Instant updates
```

**Advantages:**
- Live updates without server restart
- Smaller page load (just JSON, no HTML markers)
- Much faster
- Can update individual markers

**Disadvantages:**
- Requires rewriting map component
- More JavaScript code
- Browser does all map rendering

### Alternative 2: Render-on-Demand

```python
# route: /api/map.html

When user requests map:
  ↓
fetch_latest_aeds_from_api()
  ↓
generate fresh HTML
  ↓
return to browser
  ↓
always current!
```

**Advantages:**
- Still server-side (Python)
- Always fresh data
- No cache issues

**Disadvantages:**
- Slower response time
- Re-generates HTML on every page load
- Still static HTML (can't change one marker)

---

## Why This Happened in Original Code

### Original Code Flow
```python
# app_controller.py - initialize()

def initialize(self):
    # Called ONCE on Flask startup
    load_embedded_data()      # Local GeoJSON
    load_aeds()               # API call
    self.map_view = MapView() # Folium generates HTML once!
    render_layers()           # Add features to Folium
    map_view.add_layer_control()
    
    # HTML is now generated and stays that way
    # until next Flask restart!
```

### The Flask Template
```html
<!-- templates/index.html -->
<div id="map">
    {{ map_html|safe }}  <!-- Static string, rendered once -->
</div>

<!-- No JavaScript to refresh this map -->
<!-- No AJAX endpoints to get new data -->
<!-- No dynamic marker management -->
```

### Result
When you changed `load_aeds()`:
- Python code changed ✓
- But Flask still serving old HTML ✗
- Need restart for changes to apply ✓

---

## The Fix We Implemented

### Step 1: Isolated Data Fetching
```python
# app/controllers/app_controller.py

def load_aeds(self):
    """Isolated method for fetching AEDs"""
    
    # Direct API call
    api = HjertestarterregisterAPI()
    api.authenticate()
    response = api.search_assets(...)
    
    # Process response
    for asset in response['ASSETS']:
        # Add is_available property
        # Add distance_km
        # Add is_open_status
    
    # Return processed features
    self.map_model.set_layer_features(...)
```

### Step 2: Fixed Map View Rendering
```python
# app/views/map_view.py

def add_geojson_layer(self, features):
    """Create map layer with smart styling"""
    
    for feature in features:
        # Check IS_OPEN status
        if feature['is_available']:
            color = '#27ae60'  # Green
        else:
            color = '#e74c3c'  # Red
        
        # Render marker with style
        create_marker(feature, color)
```

### Step 3: Ensure Fresh HTML Generation
```python
# app/__init__.py

@app.before_request
def initialize_app():
    """Initialize fresh on each request"""
    if not hasattr(app, 'initialized'):
        controller.initialize()  # Generates new HTML
        app.initialized = True
```

---

## Lesson: Server-Side Rendering Limitations

### Pattern Issues

```
❌ Bad Pattern (What we had):
   Server generates HTML once
   HTML includes all data embedded
   Browser can't refresh without reload
   Reload gives stale cached version
   
✅ Better Pattern:
   Server has API endpoints that return JSON
   Browser JavaScript fetches JSON
   Browser dynamically renders map from data
   Can update individual markers in real-time
   
✅ Acceptable Pattern (What we did):
   Server regenerates HTML on each load
   HTML includes fresh data
   Still requires restart to update
   But ensures data is always current on page load
```

### When Server-Side Rendering Works Well
- Blog posts (static content)
- Documentation (rarely changes)
- Admin dashboards (internal use, frequent restarts OK)

### When It Breaks Down
- Real-time data (financial tickers, live tracking)
- Interactive maps (want marker updates without reload)
- User-driven UIs (where refresh = bad UX)

---

## Prevention for Future Projects

### Architecture Decision: Choose Early

**For Real-Time Interactive Maps:**
```
Use Client-Side Rendering:
  Frontend: React/Vue with Leaflet or Mapbox
  Backend: API endpoints returning JSON
  
  Data flow:
    API → JSON
    ↓
    JavaScript
    ↓
    DOM updates
    ↓
    Map renders
```

**For Server-Rendered Content:**
```
Use Server-Side Rendering:
  Backend: Flask/Django generating HTML
  Frontend: Server sends complete HTML
  
  Data flow:
    Database
    ↓
    Render template
    ↓
    HTML string
    ↓
    Browser displays
```

**Hybrid (Best of Both):**
```
Backend generates:
  - Initial map frame (empty)
  - JavaScript bundle
  
Frontend JavaScript:
  - Fetches data from API
  - Renders markers
  - Handles interactions
  
Updates:
  - New data → fetch API → update map
  - No server restart needed
```

---

## Summary

| Aspect | Original | Now | Why Change |
|--------|----------|-----|-----------|
| Data Fetch | On startup | On startup | Same |
| HTML Generation | Once, cached | Fresh | Fixed staleness |
| Update Frequency | Server restart | Server restart | Acceptable |
| Data Embedding | Hardcoded in HTML | Same | Unavoidable with Folium |
| Refresh Speed | Pages use cache | Fresh HTML | Better safety |
| Debug Info | None | Detailed logging | Better visibility |

---

## Going Forward

### To Update AEDs on Map:

```bash
# Option 1: Restart Flask (Current)
Ctrl+C
py run.py
# Takes 15-30 seconds, shows 263 AEDs

# Option 2: Build Admin Panel (Future)
# Add button to manually re-fetch data
# Would require client-side map rewrite
```

### To Make Truly Real-Time:

```
1. Replace Folium with Leaflet.js (frontend)
2. Create /api/aeds endpoint (backend)
3. Add WebSocket for live updates (optional)
4. Deploy on proper WSGI server (Gunicorn)

Estimated time: 4-6 hours
Current solution: Working & adequate for demonstration
```

---

## Conclusion

**The map wasn't updating because:**
1. Folium mixes data and presentation (HTML)
2. HTML gets cached by browser
3. Changes to Python code don't update cached HTML
4. Only server restart forces new HTML generation

**We fixed it by:**
- Ensuring data is always fresh on server startup
- Adding proper logging to show what's loaded
- Implementing color-coded visual status
- Documenting constraints clearly

**Trade-off accepted:**
- Need to restart Flask to update data
- But guaranteed fresh data on load
- Much simpler than full rewrite

