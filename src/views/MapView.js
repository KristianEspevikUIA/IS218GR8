/**
 * MapView.js - Handles all map rendering with Leaflet
 * Responsible for DOM manipulation and map visualization
 */
class MapView {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.map = null;
    this.layers = new Map();
    this.markers = new Map();
    this.initMap();
  }

  /**
   * Initialize Leaflet map
   */
  initMap() {
    if (!this.container) {
      console.error('Map container not found');
      return;
    }

    // Initialize map centered on Norway
    this.map = L.map(this.container, {
      zoom: 5,
      center: [60.4518, 8.4689],
      attributionControl: true
    });

    // Add base tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19
    }).addTo(this.map);
  }

  /**
   * Add GeoJSON layer to map
   * @param {string} layerId - Unique layer identifier
   * @param {object} geojson - GeoJSON FeatureCollection
   * @param {object} options - Styling and popup options
   */
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
        
        // Add hover effects
        layer.on('mouseover', function() {
          this.setStyle({
            weight: (options.weight || 2) + 2,
            opacity: 1
          });
        });
        layer.on('mouseout', function() {
          this.setStyle(defaultStyle);
        });
      }
    });

    layer.addTo(this.map);
    this.layers.set(layerId, { layer, geojson });
    return layer;
  }

  /**
   * Create popup HTML from feature properties
   * @param {object} properties - Feature attributes
   * @returns {string} HTML popup content
   */
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

  /**
   * Add marker to map
   * @param {string} markerId - Unique marker identifier
   * @param {array} latlng - [latitude, longitude]
   * @param {object} options - Marker options (title, icon, etc.)
   */
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

  /**
   * Toggle layer visibility
   * @param {string} layerId - Layer identifier
   * @param {boolean} visible - Show/hide layer
   */
  toggleLayerVisibility(layerId, visible) {
    if (!this.layers.has(layerId)) return;

    const { layer } = this.layers.get(layerId);
    if (visible) {
      this.map.addLayer(layer);
    } else {
      this.map.removeLayer(layer);
    }
  }

  /**
   * Remove layer from map
   * @param {string} layerId - Layer identifier
   */
  removeLayer(layerId) {
    if (this.layers.has(layerId)) {
      const { layer } = this.layers.get(layerId);
      this.map.removeLayer(layer);
      this.layers.delete(layerId);
    }
  }

  /**
   * Update layer with new GeoJSON data
   * @param {string} layerId - Layer identifier
   * @param {object} geojson - New GeoJSON data
   */
  updateLayer(layerId, geojson) {
    if (this.layers.has(layerId)) {
      this.removeLayer(layerId);
      this.addGeoJSONLayer(layerId, geojson);
    }
  }

  /**
   * Fit map bounds to layer
   * @param {string} layerId - Layer identifier
   */
  fitToBounds(layerId) {
    if (this.layers.has(layerId)) {
      const { layer } = this.layers.get(layerId);
      this.map.fitBounds(layer.getBounds());
    }
  }

  /**
   * Get current map viewport
   * @returns {object} {center: [lat, lng], zoom: number}
   */
  getViewport() {
    const center = this.map.getCenter();
    return {
      center: [center.lat, center.lng],
      zoom: this.map.getZoom()
    };
  }

  /**
   * Set map viewport
   * @param {array} center - [latitude, longitude]
   * @param {number} zoom - Zoom level
   */
  setViewport(center, zoom) {
    this.map.setView(center, zoom);
  }

  /**
   * Draw search radius circle
   * @param {array} center - [latitude, longitude]
   * @param {number} radiusKm - Radius in kilometers
   */
  drawSearchRadius(center, radiusKm) {
    if (this.searchCircle) {
      this.map.removeLayer(this.searchCircle);
    }

    this.searchCircle = L.circle(center, {
      radius: radiusKm * 1000, // Convert to meters
      color: '#ff6b6b',
      fill: false,
      weight: 2,
      dashArray: '5, 5',
      opacity: 0.8
    }).addTo(this.map);
  }

  /**
   * Clear search visualization
   */
  clearSearchVisualization() {
    if (this.searchCircle) {
      this.map.removeLayer(this.searchCircle);
      this.searchCircle = null;
    }
  }
}

export default MapView;
