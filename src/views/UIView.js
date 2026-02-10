/**
 * UIView.js - Handles UI elements and interactive components
 * Layer toggling, search bars, filters, etc.
 */
class UIView {
  constructor() {
    this.listeners = new Map();
  }

  /**
   * Create and attach layer control UL to DOM
   * @param {object} layers - {layerId: {name: string}}
   * @param {HTMLElement} container - Container element
   */
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

  /**
   * Create search/filter panel
   * @param {HTMLElement} container - Container element
   */
  renderSearchPanel(container) {
    const panel = document.createElement('div');
    panel.id = 'search-panel';
    panel.className = 'search-panel';

    // Search input
    const searchLabel = document.createElement('label');
    searchLabel.textContent = 'Search:';
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.id = 'search-input';
    searchInput.placeholder = 'Search by attribute...';

    // Search by distance
    const radiusLabel = document.createElement('label');
    radiusLabel.textContent = 'Search radius (km):';
    const radiusInput = document.createElement('input');
    radiusInput.type = 'number';
    radiusInput.id = 'search-radius';
    radiusInput.min = '1';
    radiusInput.max = '100';
    radiusInput.value = '5';

    // Search button
    const searchBtn = document.createElement('button');
    searchBtn.textContent = 'Search';
    searchBtn.addEventListener('click', () => {
      const radius = parseFloat(radiusInput.value);
      this.emit('spatial-search', { radius });
    });

    // Clear search button
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

  /**
   * Render data catalog table
   * @param {array} dataCatalog - Array of dataset info
   * @param {HTMLElement} container - Container element
   */
  renderDataCatalog(dataCatalog, container) {
    const section = document.createElement('section');
    section.id = 'data-catalog';

    const title = document.createElement('h2');
    title.textContent = 'Data Catalog';
    section.appendChild(title);

    const table = document.createElement('table');
    table.className = 'catalog-table';

    // Header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    ['Dataset', 'Source', 'Format', 'Processing'].forEach(text => {
      const th = document.createElement('th');
      th.textContent = text;
      headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Body
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

  /**
   * Show/hide loading indicator
   * @param {boolean} show
   */
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

  /**
   * Show toast notification
   * @param {string} message
   * @param {string} type - 'info', 'success', 'error'
   */
  toast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
      toast.remove();
    }, 3000);
  }

  /**
   * Register event listener
   * @param {string} event - Event name
   * @param {function} callback - Handler function
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  /**
   * Emit event to all listeners
   * @param {string} event - Event name
   * @param {object} data - Event data
   */
  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => callback(data));
    }
  }
}

export default UIView;
