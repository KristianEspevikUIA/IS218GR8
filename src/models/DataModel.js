/**
 * DataModel.js - Handles fetching and processing geographic data
 * Sources: GeoJSON files, OGC APIs, PostGIS (Supabase)
 */
class DataModel {
  constructor() {
    this.dataSources = new Map();
    this.cache = new Map();
  }

  /**
   * Register a data source
   * @param {string} name - Source identifier
   * @param {object} config - {type: 'geojson'|'api'|'supabase', url, ...}
   */
  registerSource(name, config) {
    this.dataSources.set(name, config);
  }

  /**
   * Fetch GeoJSON from file or URL
   * @param {string} url - URL to GeoJSON file
   * @returns {Promise<object>} GeoJSON FeatureCollection
   */
  async fetchGeoJSON(url) {
    if (this.cache.has(url)) {
      return this.cache.get(url);
    }

    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      this.cache.set(url, data);
      return data;
    } catch (error) {
      console.error(`Error fetching GeoJSON from ${url}:`, error);
      throw error;
    }
  }

  /**
   * Fetch data from OGC API (WFS, WMTS, etc.)
   * @param {string} url - OGC API endpoint
   * @param {object} params - Query parameters
   * @returns {Promise<object>} API response data
   */
  async fetchOGCAPI(url, params = {}) {
    const cacheKey = url + JSON.stringify(params);
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    try {
      const queryString = new URLSearchParams(params).toString();
      const fullUrl = queryString ? `${url}?${queryString}` : url;
      const response = await fetch(fullUrl);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      this.cache.set(cacheKey, data);
      return data;
    } catch (error) {
      console.error(`Error fetching OGC API from ${url}:`, error);
      throw error;
    }
  }

  /**
   * Query Supabase PostGIS database
   * @param {object} supabaseClient - Initialized Supabase client
   * @param {string} tableName - Table to query
   * @param {object} filters - Filter conditions
   * @returns {Promise<object>} Query results
   */
  async querySupabase(supabaseClient, tableName, filters = {}) {
    try {
      let query = supabaseClient.from(tableName).select('*');
      
      // Apply filters
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
   * Spatial filter: Find features within bounds
   * @param {object} geojson - GeoJSON FeatureCollection
   * @param {array} bounds - [[minLat, minLng], [maxLat, maxLng]]
   * @returns {object} Filtered GeoJSON
   */
  filterByBounds(geojson, bounds) {
    const [[minLat, minLng], [maxLat, maxLng]] = bounds;
    const filtered = {
      type: 'FeatureCollection',
      features: geojson.features.filter(feature => {
        const [lng, lat] = feature.geometry.coordinates;
        return lat >= minLat && lat <= maxLat && lng >= minLng && lng <= maxLng;
      })
    };
    return filtered;
  }

  /**
   * Spatial filter: Find features within distance of point
   * @param {object} geojson - GeoJSON FeatureCollection
   * @param {array} point - [latitude, longitude]
   * @param {number} radiusKm - Search radius in kilometers
   * @returns {object} Filtered GeoJSON
   */
  filterByDistance(geojson, point, radiusKm) {
    const [lat1, lng1] = point;
    const R = 6371; // Earth radius in km

    const filtered = {
      type: 'FeatureCollection',
      features: geojson.features.filter(feature => {
        const [lng2, lat2] = feature.geometry.coordinates;
        
        // Haversine formula
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

  /**
   * Clear cache
   */
  clearCache() {
    this.cache.clear();
  }
}

export default DataModel;
