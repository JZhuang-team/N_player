import { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import { buildings, roads, heatmapBuildings, heatmapRoads } from './geoData';
import 'mapbox-gl/dist/mapbox-gl.css';

function Map() {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const [modelType, setModelType] = useState('prob');
  const [totalLayers, setTotalLayers] = useState(1);
  const [resource, setResource] = useState(0);
  const [tempTotalLayers, setTempTotalLayers] = useState(1);
  const [tempResource, setTempResource] = useState(0);
  const [sidebarData, setSidebarData] = useState(null); // Right sidebar data
  const [backendData, setBackendData] = useState(null);
  const [isBuildingHeatmapVisible, setIsBuildingHeatmapVisible] = useState(false);
  const [isRoadHeatmapVisible, setIsRoadHeatmapVisible] = useState(false);
  const [showHeatmapButtons, setShowHeatmapButtons] = useState(false); // State for heatmap buttons

  // Initialize the map
  useEffect(() => {
    mapboxgl.accessToken = 'pk.eyJ1IjoiZG9yamVlbGEiLCJhIjoiY20ybWJqZnlzMGtobTJrcHc3b2Rid3VmdiJ9.9xXysCma-jzUl_MvQh16Xw';
    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: 'mapbox://styles/dorjeela/cm2f5v601008p01nxfdd725ms',
      center: [-78.786058, 43.001150],
      zoom: 16,
    });
  
    map.on('load', () => {
      mapRef.current = map;
  
      if (!map.getSource('buildings')) {
        map.addSource('buildings', { type: 'geojson', data: buildings });
        map.addLayer({
          id: 'building-layer',
          type: 'line',
          source: 'buildings',
          paint: {
            'line-color': '#0000FF',
            'line-opacity': 1,
            'line-width': 9,
          },
        });
      }
  
      if (!map.getSource('roads')) {
        map.addSource('roads', { type: 'geojson', data: roads });
        map.addLayer({
          id: 'road-layer',
          type: 'line',
          source: 'roads',
          paint: {
            'line-color': '#FF0000',
            'line-opacity': 1,
            'line-width': 6,
          },
        });
      }
  
      // Add click events for buildings and roads
      map.on('click', 'building-layer', () => {
        if (backendData) {
          setSidebarData({
            title: 'Building Data',
            description: `
              No of Layers: ${totalLayers}<br />
              Vulnerability: ${backendData.vulnerability[0]}<br />
              Investment: ${backendData.solutions[0]}<br />
              Raw Risk: ${backendData.risk[0]}<br />
              Consequence: ${backendData.consequence[0]}<br />
              Threat: ${backendData.threat[0]}
            `,
          });
        }
      });
  
      map.on('click', 'road-layer', () => {
        if (backendData) {
          setSidebarData({
            title: 'Road Data',
            description: `
              No of Layers: ${totalLayers}<br />
              Vulnerability: ${backendData.vulnerability[1]}<br />
              Investment: ${backendData.solutions[1]}<br />
              Raw Risk: ${backendData.risk[1]}<br />
              Consequence: ${backendData.consequence[1]}<br />
              Threat: ${backendData.threat[1]}
            `,
          });
        }
      });
  
      // Change cursor to pointer when hovering over layers
      map.on('mouseenter', 'building-layer', () => {
        map.getCanvas().style.cursor = 'pointer';
      });
      map.on('mouseleave', 'building-layer', () => {
        map.getCanvas().style.cursor = '';
      });
      map.on('mouseenter', 'road-layer', () => {
        map.getCanvas().style.cursor = 'pointer';
      });
      map.on('mouseleave', 'road-layer', () => {
        map.getCanvas().style.cursor = '';
      });
    });
  
    // Add heatmap toggling logic
    const toggleHeatmapLayer = (id, sourceId, data, isVisible, paintConfig) => {
      const map = mapRef.current;
    
      if (!map || !map.isStyleLoaded()) {
        console.warn('Map style is not loaded yet. Skipping heatmap toggle.');
        return;
      }
    
      if (isVisible) {
        if (!map.getSource(sourceId)) {
          map.addSource(sourceId, {
            type: 'geojson',
            data,
          });
        }
        if (!map.getLayer(id)) {
          map.addLayer({
            id,
            type: 'heatmap',
            source: sourceId,
            paint: paintConfig,
          });
        }
      } else {
        if (map.getLayer(id)) map.removeLayer(id);
        if (map.getSource(sourceId)) map.removeSource(sourceId);
      }
    };
    
  
    toggleHeatmapLayer(
      'heatmap-buildings-layer',
      'heatmap-buildings',
      heatmapBuildings,
      isBuildingHeatmapVisible,
      {
        'heatmap-intensity': ['interpolate', ['linear'], ['zoom'], 0, 1, 16, 3],
        'heatmap-weight': ['interpolate', ['linear'], ['get', 'investment'], 0, 0, 500, 1],
        'heatmap-color': [
          'interpolate',
          ['linear'],
          ['heatmap-density'],
          0, 'rgba(33, 102, 172, 0)',
          0.2, 'rgb(103, 169, 207)',
          0.4, 'rgb(209, 229, 240)',
          0.6, 'rgb(253, 219, 199)',
          0.8, 'rgb(239, 138, 98)',
          1, 'rgb(178, 24, 43)',
        ],
        'heatmap-radius': ['interpolate', ['linear'], ['zoom'], 0, 2, 16, 20],
      }
    );
  
    toggleHeatmapLayer(
      'heatmap-roads-layer',
      'heatmap-roads',
      heatmapRoads,
      isRoadHeatmapVisible,
      {
        'heatmap-intensity': ['interpolate', ['linear'], ['zoom'], 0, 1, 16, 3],
        'heatmap-weight': ['interpolate', ['linear'], ['get', 'threat'], 0, 0, 1, 1],
        'heatmap-color': [
          'interpolate',
          ['linear'],
          ['heatmap-density'],
          0, 'rgba(33, 102, 172, 0)',
          0.2, 'rgb(103, 169, 207)',
          0.4, 'rgb(209, 229, 240)',
          0.6, 'rgb(253, 219, 199)',
          0.8, 'rgb(239, 138, 98)',
          1, 'rgb(178, 24, 43)',
        ],
        'heatmap-radius': ['interpolate', ['linear'], ['zoom'], 0, 2, 16, 20],
      }
    );
  
    return () => map.remove();
  }, [backendData, totalLayers, isBuildingHeatmapVisible, isRoadHeatmapVisible]);
  

  const handleSubmit = async (event) => {
    event.preventDefault();
    setShowHeatmapButtons(true); // Show heatmap buttons after submitting

    const formData = {
      total_layers: tempTotalLayers,
      resource: tempResource,
      model_type: modelType,
    };

    try {
      const response = await fetch('http://localhost:8080/results', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Response from Flask:', data);
      setBackendData(data);
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  return (
    <>
      <div id="map-container" ref={mapContainerRef} className="h-screen" />
      {/* Left Sidebar */}
      <div className="absolute top-0 left-5 bg-white p-6 rounded shadow-lg w-96 h-[calc(100%-2rem)] z-10 overflow-auto">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="form-group">
            <label className="block font-semibold mb-2">Model Type:</label>
            <div className="flex items-center space-x-4">
              <label className="inline-flex items-center">
                <input
                  type="radio"
                  name="model_type"
                  value="prob"
                  checked={modelType === 'prob'}
                  onChange={() => setModelType('prob')}
                  className="form-radio text-blue-600"
                />
                <span className="ml-2">Probabilistic Model</span>
              </label>
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="total_layers" className="block font-semibold mb-2">Total Layers:</label>
            <div className="flex items-center space-x-4">
              <input
                type="range"
                id="total_layers"
                name="total_layers"
                min="1"
                max="2"
                step="1"
                value={tempTotalLayers}
                onChange={(e) => setTempTotalLayers(Number(e.target.value))}
                className="slider w-full"
              />
              <span className="text-gray-700">{tempTotalLayers}</span>
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="resource" className="block font-semibold mb-2">Resource:</label>
            <div className="flex items-center space-x-4">
              <input
                type="range"
                id="resource"
                name="resource"
                min="0"
                max="500"
                step="5"
                value={tempResource}
                onChange={(e) => setTempResource(Number(e.target.value))}
                className="slider w-full"
              />
              <span className="text-gray-700">{tempResource}</span>
            </div>
          </div>
          <button
            type="submit"
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            Update
          </button>
        </form>
      </div>
      {/* Heatmap Buttons */}
      {showHeatmapButtons && (
        <div className="absolute top-5 right-5 flex flex-col space-y-2 z-10">
          <button
            onClick={() => setIsBuildingHeatmapVisible((prev) => !prev)}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            {isBuildingHeatmapVisible ? 'Hide Building Heatmap' : 'Show Building Heatmap'}
          </button>
          <button
            onClick={() => setIsRoadHeatmapVisible((prev) => !prev)}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            {isRoadHeatmapVisible ? 'Hide Road Heatmap' : 'Show Road Heatmap'}
          </button>
        </div>
      )}
      {/* Right Sidebar */}
      {sidebarData && (
  <div
    className="absolute top-0 right-5 mt-5 mb-5 bg-white p-6 rounded-lg shadow-lg w-96 h-[calc(100%-2rem)] z-10 overflow-auto"
    style={{ width: '24rem', height: 'calc(100% - 2rem)' }} // Match dimensions to the left sidebar
  >
    {/* Header with Close Button */}
    <div className="flex justify-between items-center mb-4">
      <h2 className="text-lg font-semibold">{sidebarData.title}</h2>
      <button
        onClick={() => setSidebarData(null)} // Close the sidebar
        className="text-gray-500 hover:text-gray-700 focus:outline-none"
        aria-label="Close"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
    <p dangerouslySetInnerHTML={{ __html: sidebarData.description }} />
  </div>
)}

    </>
  );
}

export default Map;
