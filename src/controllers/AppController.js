/**
 * AppController.js - Main application controller
 * Orchestrates initialization and overall application flow
 */
class AppController {
  constructor(mapModel, mapView, uiView, dataModel) {
    this.mapModel = mapModel;
    this.mapView = mapView;
    this.uiView = uiView;
    this.dataModel = dataModel;
    this.currentSearchPoint = null;
  }

  /**
   * Initialize the application
   */
  async init() {
    try {
      this.uiView.setLoading(true);

      // Register data sources
      this.setupDataSources();

      // Create layer control
      this.setupLayerControl();

      // Load initial layers
      await this.loadLayers();

      // Setup event listeners
      this.setupEventListeners();

      this.uiView.setLoading(false);
      this.uiView.toast('Map loaded successfully!', 'success');
    } catch (error) {
      console.error('Initialization error:', error);
      this.uiView.setLoading(false);
      this.uiView.toast('Error loading map', 'error');
    }
  }

  /**
   * Register all data sources
   */
  setupDataSources() {
    // GeoJSON source
    this.dataModel.registerSource('geojson-local', {
      type: 'geojson',
      url: './data/geojson/sample.geojson'
    });

    // OGC API example (GeoNorge)
    this.dataModel.registerSource('geonorge-api', {
      type: 'ogc-api',
      url: 'https://www.geonorge.no/wfs'
    });

    // Supabase (optional)
    // this.dataModel.registerSource('supabase', {
    //   type: 'supabase',
    //   projectUrl: process.env.SUPABASE_URL,
    //   anonKey: process.env.SUPABASE_ANON_KEY
    // });

    this.mapModel.addLayer('geojson-local', {
      name: 'Local GeoJSON Data',
      visible: true,
      color: '#3388ff'
    });

    this.mapModel.addLayer('geonorge-api', {
      name: 'GeoNorge API Data',
      visible: false,
      color: '#ff8c00'
    });
  }

  /**
   * Setup layer control UI
   */
  setupLayerControl() {
    this.uiView.renderLayerControl(this.mapModel.layers, document.getElementById('controls'));
  }

  /**
   * Load and display layers
   */
  async loadLayers() {
    try {
      // Load GeoJSON
      const geojsonConfig = this.dataModel.dataSources.get('geojson-local');
      const geojsonData = await this.dataModel.fetchGeoJSON(geojsonConfig.url);
      this.mapModel.setLayerData('geojson-local', geojsonData);
      this.mapView.addGeoJSONLayer('geojson-local', geojsonData, {
        color: '#3388ff'
      });

      // Optional: Load OGC API data
      // const ogcData = await this.dataModel.fetchOGCAPI(ogcUrl, {request: 'GetFeature'});
      // this.mapView.addGeoJSONLayer('geonorge-api', ogcData);

    } catch (error) {
      console.error('Error loading layers:', error);
      throw error;
    }
  }

  /**
   * Setup UI event listeners
   */
  setupEventListeners() {
    // Layer toggle
    this.uiView.on('toggle-layer', (data) => {
      this.mapModel.toggleLayer(data.layerId);
      this.mapView.toggleLayerVisibility(data.layerId, data.visible);
    });

    // Spatial search
    this.uiView.on('spatial-search', (data) => {
      this.performSpatialSearch(data.radius);
    });

    // Clear search
    this.uiView.on('clear-search', () => {
      this.mapView.clearSearchVisualization();
    });

    // Map click for search center
    this.mapView.map.on('click', (e) => {
      this.currentSearchPoint = [e.latlng.lat, e.latlng.lng];
      console.log('Search point set at:', this.currentSearchPoint);
    });
  }

  /**
   * Perform spatial search by distance
   * @param {number} radiusKm - Search radius in kilometers
   */
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

      // Filter features within radius
      const filtered = this.dataModel.filterByDistance(
        layerData,
        this.currentSearchPoint,
        radiusKm
      );

      // Update map visualization
      this.mapView.removeLayer('geojson-search-results');
      this.mapView.addGeoJSONLayer('geojson-search-results', filtered, {
        color: '#ff6b6b',
        weight: 3
      });

      // Draw search radius circle
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

export default AppController;
