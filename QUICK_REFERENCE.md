# Kristiansand Hjertestartere Map - Quick Reference

## ✅ What's Working Now

```
Map Status: OPERATIONAL ✓
Location: http://localhost:3000
Data: 263 AEDs in Kristiansand (65 open, 198 closed)
Visual: Green markers = OPEN, Red markers = CLOSED
Last Updated: Server startup
API: Hjertestarterregister v1
Auth: OAuth 2.0 (client_credentials)
```

---

## 🗺️ Quick Start

### Start the Server
```bash
py run.py
```

Expected output:
```
✓ Loaded 263 AEDs in Kristiansand region
  • Open now (IS_OPEN='Y'):   65 AEDs
  • Closed now (IS_OPEN='N'): 198 AEDs

Visual indicators on map:
  • Green markers = OPEN (IS_OPEN='Y')
  • Red markers = CLOSED (IS_OPEN='N')

✓ Map initialized successfully!
* Running on http://127.0.0.1:3000
```

### View the Map
```
Open browser:
http://localhost:3000
```

### Interact with Map
- **Zoom:** Mouse wheel or +/- buttons
- **Pan:** Click and drag
- **Click marker:** See AED details (name, address, hours, status)
- **Hover marker:** Tooltip shows name and status

---

## 📊 What You See

### On the Map
- **Base Map:** OpenStreetMap
- **Center:** Kristiansand city (58.1414°N, 8.0842°E)
- **Zoom:** Level 10 (city-level view)
- **Markers:** 263 total
  - 🟢 **65 GREEN** = Currently OPEN
  - 🔴 **198 RED** = Currently CLOSED

### Click Any Marker to See
- Site Name
- Address & City
- Postal Code
- Opening Hours Text
- Distance from center (km)
- IS_OPEN Status

---

## 🔄 Update/Refresh Data

### Method 1: Full Restart
```bash
# Press Ctrl+C in terminal to stop server
Ctrl+C

# Restart
py run.py

# Server fetches fresh data from API
```
**Time:** ~20-30 seconds  
**Why:** Folium regenerates HTML for all 263 markers

### Method 2: API Query (Get Just Data)
```bash
# Get available AEDs (filtered to open)
curl http://localhost:3000/api/aeds/available

# Get count only
curl http://localhost:3000/api/aeds/available/count
```

---

## 🎯 Key Facts

| Item | Value |
|------|-------|
| **Total AEDs** | 263 |
| **Open Now** | 65 (25%) |
| **Closed Now** | 198 (75%) |
| **Search Radius** | 15 km |
| **Center** | Kristiansand |
| **Data Source** | Hjertestarterregister API |
| **Refresh Needed For** | Changes to Python code |
| **Map Generates On** | Every Flask startup |

---

## 🐛 Troubleshooting

### Map Shows No Markers
```
Check server output for:
  ✓ Loaded 263 AEDs in Kristiansand region
  
If missing:
  1. Check .env has API credentials
  2. Check internet connection
  3. API might be temporarily down
```

### Port 3000 Already in Use
```bash
# Kill existing Flask process
taskkill /F /IM python.exe

# Then restart
py run.py
```

### API Returns 401 Unauthorized
```
Solution: Server restart
py run.py
# Gets fresh OAuth token
```

### Map Loads But No Data
```
Wait 20-30 seconds for:
  • API fetch (5-10s)
  • HTML generation (15-20s)
  
Then refresh browser (F5)
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `run.py` | Start Flask server |
| `app/controllers/app_controller.py` | Data loading logic |
| `app/views/map_view.py` | Map rendering with Folium |
| `app/models/hjertestarterregister_api.py` | API client & auth |
| `templates/index.html` | Web page template |
| `.env` | API credentials |

---

## 🔐 Security

### Credentials Required in `.env`
```env
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=...

HJERTESTARTERREGISTER_CLIENT_ID=...
HJERTESTARTERREGISTER_CLIENT_SECRET=...
```

### Local Only
- Development server (not WSGI)
- No HTTPS
- No authentication required to view map
- Suitable for local/demo use only

---

## 🚀 Status

```
┌─────────────────────────────────┐
│  ✅ SERVER RUNNING             │
│  ✅ API CONNECTED              │
│  ✅ 263 AEDs LOADED            │
│  ✅ MAP DISPLAYED              │
│  ✅ COLOR CODING WORKING       │
│  ✅ ZOOM/PAN FUNCTIONAL        │
│  ✅ POPUPS SHOWING DATA        │
└─────────────────────────────────┘

Status: READY FOR USE 🎉
```

---

## 📖 For More Details

See these files for complete documentation:
- `IMPLEMENTATION_SUMMARY.md` - What was done and why
- `WHY_MAP_WAS_STALE.md` - Technical explanation of the fix
- `AVAILABLE_AEDS_GUIDE.md` - API documentation

---

## 💡 Pro Tips

### Faster Development
```
Instead of restarting Flask every time:
1. Edit Python code
2. Press Ctrl+C to stop
3. Run `py run.py` again
4. Typical for Folium/Flask development
```

### API Testing
```bash
# Test API still works (get available AEDs)
curl "http://localhost:3000/api/aeds/available?latitude=59.9&longitude=10.7&distance=10000"

# This makes API call but doesn't update map
# Map updates only on Flask restart
```

### Map Performance
```
Marker rendering:
- 263 markers = ~20-30 seconds
- This is normal for Folium
- Client-side Leaflet would be faster (5 seconds)
```

---

## ✨ What's Unique About This Solution

✅ **Shows ALL AEDs** - not filtered to just open ones  
✅ **Color-coded by status** - green/red based on IS_OPEN  
✅ **Distance calculated** - Haversine formula per marker  
✅ **Fresh on startup** - always current data  
✅ **Full information** - popups show all details  
✅ **Interactive** - zoom, pan, click, hover  
✅ **Well-documented** - logs show what's loading  

---

## 🎓 How It Works

```
1. Browser requests http://localhost:3000
   ↓
2. Flask starts app_controller.initialize()
   ↓
3. load_aeds() fetches 263 AEDs from API
   ↓
4. MapView adds markers with IS_OPEN colors
   ↓
5. Folium generates HTML with embedded map data
   ↓
6. Flask sends HTML to browser
   ↓
7. Browser displays interactive map with:
   - 65 green (open) markers
   - 198 red (closed) markers
   - Popups on click
   - Zoom/pan controls
```

---

**Ready to explore Kristiansand's hjertestartere! 🗺️**

