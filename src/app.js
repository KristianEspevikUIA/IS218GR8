/**
 * app.js - Complete bundled application (no ES6 modules)
 */

// ============ MODELS ============

class MapModel {
  constructor() {
    this.mapCenter = [60.4518, 8.4689];
    this.zoomLevel = 5;
    this.layers = new Map();
    this.activeFilters = {};
    this.spatialBounds = null;
  }

  addLayer(name, config) {
    this.layers.set(name, {
      name,
      data: null,
      visible: true,
      ...config
    });
  }

  toggleLayer(name) {
    if (this.layers.has(name)) {
      const layer = this.layers.get(name);
      layer.visible = !layer.visible;
      return layer.visible;
    }
    return false;
  }

  setSpatialFilter(bounds) {
    this.spatialBounds = bounds;
  }

  getVisibleLayers() {
    return Array.from(this.layers.values()).filter(l => l.visible);
  }

  setViewport(center, zoom) {
    this.mapCenter = center;
    this.zoomLevel = zoom;
  }

  setLayerData(layerName, data) {
    if (this.layers.has(layerName)) {
      this.layers.get(layerName).data = data;
    }
  }
}

class DataModel {
  constructor() {
    this.dataSources = new Map();
  }

  registerSource(name, config) {
    this.dataSources.set(name, config);
  }

  async fetchOGCAPI(url, params = {}) {
    try {
      const queryString = new URLSearchParams(params).toString();
      const fullUrl = queryString ? `${url}?${queryString}` : url;
      const response = await fetch(fullUrl);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`Error fetching OGC API from ${url}:`, error);
      throw error;
    }
  }

  async querySupabase(supabaseClient, tableName, filters = {}) {
    try {
      let query = supabaseClient.from(tableName).select('*');
      
      Object.entries(filters).forEach(([key, value]) => {
        query = query.eq(key, value);
      });

      const { data, error } = await query;
      if (error) throw error;
      return data;
    } catch (error) {
      console.error(`Error querying Supabase table ${tableName}:`, error);
      throw error;
    }
  }

  /**
   * Query Supabase with PostGIS spatial SQL functions
   * @param {object} supabaseClient - Initialized Supabase client
   * @param {string} tableName - Table to query
   * @returns {Promise<array>} Query results with geometry data
   */
  async querySupabaseWithSpatial(supabaseClient, tableName) {
    try {
      // Query with PostGIS geometry column (assume geometry column exists)
      const { data, error } = await supabaseClient
        .from(tableName)
        .select('id, name, category, description, geometry');
      
      if (error) throw error;
      return data || [];
    } catch (error) {
      console.error(`Error querying PostGIS table ${tableName}:`, error);
      throw error;
    }
  }

  /**
   * Spatial query: Find features within distance using PostGIS ST_DWithin
   * @param {object} supabaseClient - Initialized Supabase client
   * @param {string} tableName - Table to query
   * @param {number} lng - Longitude of search point
   * @param {number} lat - Latitude of search point
   * @param {number} distanceMeters - Search radius in meters
   * @returns {Promise<array>} Features within radius
   */
  async querySupabaseWithinDistance(supabaseClient, tableName, lng, lat, distanceMeters) {
    try {
      // Use PostGIS ST_DWithin for distance-based spatial query
      // This requires a PostGIS geometry column with spatial index
      const { data, error } = await supabaseClient.rpc('find_nearby_locations', {
        p_longitude: lng,
        p_latitude: lat,
        p_distance: distanceMeters
      });
      
      if (error) throw error;
      return data || [];
    } catch (error) {
      console.warn(`PostGIS distance query not available (RPC function not created):`, error);
      // Fallback: return all data if RPC not available
      return await this.querySupabaseWithSpatial(supabaseClient, tableName);
    }
  }

  filterByDistance(geojson, point, radiusKm) {
    const [lat1, lng1] = point;
    const R = 6371;

    const filtered = {
      type: 'FeatureCollection',
      features: geojson.features.filter(feature => {
        const [lng2, lat2] = feature.geometry.coordinates;
        
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLng = (lng2 - lng1) * Math.PI / 180;
        const a = Math.sin(dLat / 2) ** 2 +
                  Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                  Math.sin(dLng / 2) ** 2;
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        const distance = R * c;

        return distance <= radiusKm;
      })
    };
    return filtered;
  }
}

// ============ VIEWS ============

class MapView {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.map = null;
    this.layers = new Map();
    this.markers = new Map();
    this.initMap();
  }

  initMap() {
    if (!this.container) {
      console.error('Map container not found');
      return;
    }

    this.map = L.map(this.container, {
      zoom: 5,
      center: [60.4518, 8.4689],
      attributionControl: true
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19
    }).addTo(this.map);
  }

  addGeoJSONLayer(layerId, geojson, options = {}) {
    const defaultStyle = {
      color: options.color || '#3388ff',
      weight: options.weight || 2,
      opacity: options.opacity || 0.8,
      fillOpacity: options.fillOpacity || 0.5
    };

    const layer = L.geoJSON(geojson, {
      style: defaultStyle,
      onEachFeature: (feature, layer) => {
        const popup = this.createPopup(feature.properties);
        layer.bindPopup(popup);
        
        // Only add style handlers for non-Point features (they don't have setStyle)
        if (feature.geometry.type !== 'Point') {
          layer.on('mouseover', function() {
            if (this.setStyle) {
              this.setStyle({
                weight: (options.weight || 2) + 2,
                opacity: 1
              });
            }
          });
          layer.on('mouseout', function() {
            if (this.setStyle) {
              this.setStyle(defaultStyle);
            }
          });
        }
      }
    });

    layer.addTo(this.map);
    this.layers.set(layerId, { layer, geojson });
    return layer;
  }

  createPopup(properties) {
    if (!properties || Object.keys(properties).length === 0) {
      return '<div class="popup-content"><p>No data available</p></div>';
    }

    let html = '<div class="popup-content"><table>';
    Object.entries(properties).forEach(([key, value]) => {
      html += `<tr><td><strong>${key}</strong></td><td>${value}</td></tr>`;
    });
    html += '</table></div>';
    return html;
  }

  addMarker(markerId, latlng, options = {}) {
    const marker = L.marker(latlng, {
      title: options.title || 'Marker'
    }).bindPopup(options.popup || options.title);

    if (options.icon) {
      marker.setIcon(options.icon);
    }

    marker.addTo(this.map);
    this.markers.set(markerId, marker);
    return marker;
  }

  toggleLayerVisibility(layerId, visible) {
    if (!this.layers.has(layerId)) return;

    const { layer } = this.layers.get(layerId);
    if (visible) {
      this.map.addLayer(layer);
    } else {
      this.map.removeLayer(layer);
    }
  }

  removeLayer(layerId) {
    if (this.layers.has(layerId)) {
      const { layer } = this.layers.get(layerId);
      this.map.removeLayer(layer);
      this.layers.delete(layerId);
    }
  }

  updateLayer(layerId, geojson) {
    if (this.layers.has(layerId)) {
      this.removeLayer(layerId);
      this.addGeoJSONLayer(layerId, geojson);
    }
  }

  fitToBounds(layerId) {
    if (this.layers.has(layerId)) {
      const { layer } = this.layers.get(layerId);
      this.map.fitBounds(layer.getBounds());
    }
  }

  getViewport() {
    const center = this.map.getCenter();
    return {
      center: [center.lat, center.lng],
      zoom: this.map.getZoom()
    };
  }

  setViewport(center, zoom) {
    this.map.setView(center, zoom);
  }

  drawSearchRadius(center, radiusKm) {
    if (this.searchCircle) {
      this.map.removeLayer(this.searchCircle);
    }

    this.searchCircle = L.circle(center, {
      radius: radiusKm * 1000,
      color: '#ff6b6b',
      fill: false,
      weight: 2,
      dashArray: '5, 5',
      opacity: 0.8
    }).addTo(this.map);
  }

  clearSearchVisualization() {
    if (this.searchCircle) {
      this.map.removeLayer(this.searchCircle);
      this.searchCircle = null;
    }
  }
}

class UIView {
  constructor() {
    this.listeners = new Map();
  }

  renderLayerControl(layers, container) {
    const controlDiv = document.createElement('div');
    controlDiv.id = 'layer-control';
    controlDiv.className = 'layer-control';

    const title = document.createElement('h3');
    title.textContent = 'Layers';
    controlDiv.appendChild(title);

    const list = document.createElement('div');
    list.className = 'layer-list';

    layers.forEach((config, layerId) => {
      const label = document.createElement('label');
      label.className = 'layer-item';

      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.checked = config.visible !== false;
      checkbox.dataset.layerId = layerId;
      checkbox.addEventListener('change', (e) => {
        this.emit('toggle-layer', { layerId, visible: e.target.checked });
      });

      const span = document.createElement('span');
      span.textContent = config.name;

      label.appendChild(checkbox);
      label.appendChild(span);
      list.appendChild(label);
    });

    controlDiv.appendChild(list);
    container.appendChild(controlDiv);
  }

  renderSearchPanel(container) {
    const panel = document.createElement('div');
    panel.id = 'search-panel';
    panel.className = 'search-panel';

    const searchLabel = document.createElement('label');
    searchLabel.textContent = 'Search:';
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.id = 'search-input';
    searchInput.placeholder = 'Search by attribute...';

    const radiusLabel = document.createElement('label');
    radiusLabel.textContent = 'Search radius (km):';
    const radiusInput = document.createElement('input');
    radiusInput.type = 'number';
    radiusInput.id = 'search-radius';
    radiusInput.min = '1';
    radiusInput.max = '100';
    radiusInput.value = '5';

    const searchBtn = document.createElement('button');
    searchBtn.textContent = 'Search';
    searchBtn.addEventListener('click', () => {
      const radius = parseFloat(radiusInput.value);
      this.emit('spatial-search', { radius });
    });

    const clearBtn = document.createElement('button');
    clearBtn.textContent = 'Clear';
    clearBtn.className = 'secondary';
    clearBtn.addEventListener('click', () => {
      searchInput.value = '';
      radiusInput.value = '5';
      this.emit('clear-search', {});
    });

    panel.appendChild(searchLabel);
    panel.appendChild(searchInput);
    panel.appendChild(document.createElement('br'));
    panel.appendChild(radiusLabel);
    panel.appendChild(radiusInput);
    panel.appendChild(document.createElement('br'));
    panel.appendChild(searchBtn);
    panel.appendChild(clearBtn);

    container.appendChild(panel);
  }

  renderDataCatalog(dataCatalog, container) {
    const section = document.createElement('section');
    section.id = 'data-catalog';

    const title = document.createElement('h2');
    title.textContent = 'Data Catalog';
    section.appendChild(title);

    const table = document.createElement('table');
    table.className = 'catalog-table';

    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    ['Dataset', 'Source', 'Format', 'Processing'].forEach(text => {
      const th = document.createElement('th');
      th.textContent = text;
      headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement('tbody');
    dataCatalog.forEach(item => {
      const row = document.createElement('tr');
      const cells = [item.dataset, item.source, item.format, item.processing];
      cells.forEach(text => {
        const td = document.createElement('td');
        td.textContent = text;
        row.appendChild(td);
      });
      tbody.appendChild(row);
    });
    table.appendChild(tbody);

    section.appendChild(table);
    container.appendChild(section);
  }

  setLoading(show) {
    if (!document.getElementById('loading-indicator')) {
      const loader = document.createElement('div');
      loader.id = 'loading-indicator';
      loader.className = 'loading-indicator';
      loader.innerHTML = '<p>Loading data...</p>';
      document.body.appendChild(loader);
    }

    const indicator = document.getElementById('loading-indicator');
    indicator.style.display = show ? 'flex' : 'none';
  }

  toast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
      toast.remove();
    }, 3000);
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => callback(data));
    }
  }
}

// ============ CONTROLLER ============

class AppController {
  constructor(mapModel, mapView, uiView, dataModel) {
    this.mapModel = mapModel;
    this.mapView = mapView;
    this.uiView = uiView;
    this.dataModel = dataModel;
    this.currentSearchPoint = null;
  }

  async init() {
    try {
      this.uiView.setLoading(true);

      this.setupDataSources();
      this.setupLayerControl();
      await this.loadLayers();
      this.setupEventListeners();

      this.uiView.setLoading(false);
      this.uiView.toast('Map loaded successfully!', 'success');
    } catch (error) {
      console.error('Initialization error:', error);
      this.uiView.setLoading(false);
      this.uiView.toast('Error loading map', 'error');
    }
  }

  setupDataSources() {
    this.dataModel.registerSource('geojson-local', {
      type: 'geojson',
      url: './data/geojson/sample.geojson'
    });

    // OGC API source - using Kartverket Adresser API (official Norwegian geocoding service)
    this.dataModel.registerSource('ogc-api-external', {
      type: 'ogc-api',
      url: 'https://ws.geonorge.no/adresser/v1/sok',
      params: {
        sok: 'kirke',  // Search for "kirke" (church) in Norwegian
        treffPerSide: 50,
        asciiKompatibel: true
      }
    });

    // Supabase configuration (optional - user must configure)
    this.dataModel.registerSource('supabase', {
      type: 'supabase',
      projectUrl: window.SUPABASE_CONFIG?.projectUrl || 'https://your-project.supabase.co',
      anonKey: window.SUPABASE_CONFIG?.anonKey || 'your-anon-key'
    });

    this.mapModel.addLayer('geojson-local', {
      name: 'Local GeoJSON Data',
      visible: true,
      color: '#3388ff'
    });

    this.mapModel.addLayer('ogc-api-external', {
      name: 'OGC API Data (Nominatim)',
      visible: false,
      color: '#ff8c00'
    });

    this.mapModel.addLayer('supabase-locations', {
      name: 'Supabase PostGIS',
      visible: false,
      color: '#10b981'
    });
  }

  setupLayerControl() {
    this.uiView.renderLayerControl(this.mapModel.layers, document.getElementById('controls'));
  }

  async loadLayers() {
    try {
      // Load embedded GeoJSON data
      const geojsonData = window.GEOJSON_DATA;
      this.mapModel.setLayerData('geojson-local', geojsonData);
      this.mapView.addGeoJSONLayer('geojson-local', geojsonData, {
        color: '#3388ff'
      });

      // Load OGC API data (Kartverket Adresser API)
      try {
        const ogcConfig = this.dataModel.dataSources.get('ogc-api-external');
        const ogcResponse = await this.dataModel.fetchOGCAPI(ogcConfig.url, ogcConfig.params);
        
        // Convert Kartverket response to GeoJSON
        if (ogcResponse && ogcResponse.adresser && ogcResponse.adresser.length > 0) {
          const ogcData = {
            type: 'FeatureCollection',
            features: ogcResponse.adresser.map(addr => ({
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
          
          this.mapModel.setLayerData('ogc-api-external', ogcData);
          this.mapView.addGeoJSONLayer('ogc-api-external', ogcData, {
            color: '#ff8c00'
          });
          this.uiView.toast(`Loaded ${ogcData.features.length} addresses from Kartverket Adresser API`, 'success');
        }
      } catch (error) {
        console.warn('OGC API data failed to load:', error);
        this.uiView.toast('Kartverket API data unavailable', 'warning');
      }

      // Load Supabase PostGIS data with spatial queries (if configured)
      if (window.SUPABASE_CLIENT) {
        try {
          // Query all locations from Supabase (PostGIS enabled table)
          const supabaseData = await this.dataModel.querySupabaseWithSpatial(
            window.SUPABASE_CLIENT,
            'locations'
          );
          
          if (supabaseData && supabaseData.length > 0) {
            // Convert Supabase results to GeoJSON
            const geojsonFromSupabase = {
              type: 'FeatureCollection',
              features: supabaseData.map(item => {
                // Extract coordinates from geometry
                let coords = [0, 0];
                if (item.geometry) {
                  if (typeof item.geometry === 'string') {
                    // Parse GeoJSON string if needed
                    const geom = JSON.parse(item.geometry);
                    coords = geom.coordinates;
                  } else if (item.geometry.coordinates) {
                    coords = item.geometry.coordinates;
                  }
                }
                
                return {
                  type: 'Feature',
                  geometry: {
                    type: 'Point',
                    coordinates: coords
                  },
                  properties: {
                    id: item.id,
                    name: item.name,
                    category: item.category,
                    description: item.description
                  }
                };
              })
            };
            
            this.mapModel.setLayerData('supabase-locations', geojsonFromSupabase);
            this.mapView.addGeoJSONLayer('supabase-locations', geojsonFromSupabase, {
              color: '#10b981'
            });
            this.uiView.toast(`Loaded ${geojsonFromSupabase.features.length} locations from PostGIS database`, 'success');
          }
        } catch (error) {
          console.warn('Supabase PostGIS data failed to load:', error);
          // This is optional, so don't show error toast
        }
      }
    } catch (error) {
      console.error('Error loading layers:', error);
      throw error;
    }
  }

  setupEventListeners() {
    this.uiView.on('toggle-layer', (data) => {
      this.mapModel.toggleLayer(data.layerId);
      this.mapView.toggleLayerVisibility(data.layerId, data.visible);
    });

    this.uiView.on('spatial-search', (data) => {
      this.performSpatialSearch(data.radius);
    });

    this.uiView.on('clear-search', () => {
      this.mapView.clearSearchVisualization();
    });

    this.mapView.map.on('click', (e) => {
      this.currentSearchPoint = [e.latlng.lat, e.latlng.lng];
      console.log('Search point set at:', this.currentSearchPoint);
    });
  }

  performSpatialSearch(radiusKm) {
    if (!this.currentSearchPoint) {
      this.uiView.toast('Click on the map to set search center', 'info');
      return;
    }

    try {
      const layerData = this.mapModel.layers.get('geojson-local')?.data;
      if (!layerData) {
        this.uiView.toast('No data available for search', 'error');
        return;
      }

      const filtered = this.dataModel.filterByDistance(
        layerData,
        this.currentSearchPoint,
        radiusKm
      );

      this.mapView.removeLayer('geojson-search-results');
      this.mapView.addGeoJSONLayer('geojson-search-results', filtered, {
        color: '#ff6b6b',
        weight: 3
      });

      this.mapView.drawSearchRadius(this.currentSearchPoint, radiusKm);

      this.uiView.toast(
        `Found ${filtered.features.length} features within ${radiusKm}km`,
        'success'
      );
    } catch (error) {
      console.error('Search error:', error);
      this.uiView.toast('Search failed', 'error');
    }
  }
}
