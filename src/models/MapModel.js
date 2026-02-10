/**
 * MapModel.js - Handles map state and geographic data
 * Manages map layers, bounds, and coordinate transformations
 */
class MapModel {
  constructor() {
    this.mapCenter = [60.4518, 8.4689]; // Default: Norway center
    this.zoomLevel = 5;
    this.layers = new Map();
    this.activeFilters = {};
    this.spatialBounds = null;
  }

  /**
   * Add a layer to the map model
   * @param {string} name - Layer identifier
   * @param {object} config - Layer configuration
   */
  addLayer(name, config) {
    this.layers.set(name, {
      name,
      data: null,
      visible: true,
      ...config
    });
  }

  /**
   * Toggle layer visibility
   * @param {string} name - Layer identifier
   */
  toggleLayer(name) {
    if (this.layers.has(name)) {
      const layer = this.layers.get(name);
      layer.visible = !layer.visible;
      return layer.visible;
    }
    return false;
  }

  /**
   * Set spatial filter (e.g., bounding box)
   * @param {array} bounds - [[lat1, lng1], [lat2, lng2]]
   */
  setSpatialFilter(bounds) {
    this.spatialBounds = bounds;
  }

  /**
   * Get all visible layers
   * @returns {array} Visible layer objects
   */
  getVisibleLayers() {
    return Array.from(this.layers.values()).filter(l => l.visible);
  }

  /**
   * Update map viewport
   * @param {array} center - [latitude, longitude]
   * @param {number} zoom - Zoom level
   */
  setViewport(center, zoom) {
    this.mapCenter = center;
    this.zoomLevel = zoom;
  }

  /**
   * Store data for a layer
   * @param {string} layerName - Layer identifier
   * @param {object} data - GeoJSON or other geographic data
   */
  setLayerData(layerName, data) {
    if (this.layers.has(layerName)) {
      this.layers.get(layerName).data = data;
    }
  }
}

export default MapModel;
