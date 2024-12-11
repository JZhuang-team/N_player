import { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import { buildings, roads } from './geoData'; // Import the data

import 'mapbox-gl/dist/mapbox-gl.css';

function Map() {
  const mapRef = useRef();
  const mapContainerRef = useRef();
  const [modelType, setModelType] = useState('prob');
  const [totalLayers, setTotalLayers] = useState(1); // Default to 1 layer
  const [resource, setResource] = useState(0);
  const [layersVisible, setLayersVisible] = useState(false); // Manage layer visibility
  const [sidebarData, setSidebarData] = useState(null); // Data for the right sidebar
  const [backendData, setBackendData] = useState(null); // Data from the backend

  useEffect(() => {
    mapboxgl.accessToken = 'pk.eyJ1IjoiZG9yamVlbGEiLCJhIjoiY20ybWJqZnlzMGtobTJrcHc3b2Rid3VmdiJ9.9xXysCma-jzUl_MvQh16Xw';
    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: 'mapbox://styles/dorjeela/cm2f5v601008p01nxfdd725ms',
      center: [-78.786058, 43.001150],
      zoom: 16,
    });

    map.on('load', () => {
      if (layersVisible) {
        // Add buildings source and layers
        if (!map.getSource('buildings')) {
          map.addSource('buildings', {
            type: 'geojson',
            data: buildings,
          });

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

        // Add roads source and layers
        if (!map.getSource('roads')) {
          map.addSource('roads', {
            type: 'geojson',
            data: roads,
          });

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

        // Change the cursor to pointer when over a layer
        map.on('mouseenter', 'building-layer', () => {
          map.getCanvas().style.cursor = 'pointer';
        });

        map.on('mouseenter', 'road-layer', () => {
          map.getCanvas().style.cursor = 'pointer';
        });

        // Reset cursor when leaving the layer
        map.on('mouseleave', 'building-layer', () => {
          map.getCanvas().style.cursor = '';
        });

        map.on('mouseleave', 'road-layer', () => {
          map.getCanvas().style.cursor = '';
        });
      }
    });

    return () => {
      map.remove();
    };
  }, [layersVisible, backendData]);

  const syncSlider = (setter, value) => {
    setter(Number(value)); // Update the state with the parsed numeric value
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLayersVisible(true);

    const formData = {
      total_layers: totalLayers,
      resource: resource,
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
      setBackendData(data); // Store backend data in state
      setSidebarData({
        title: 'Results',
        description: `
          Objective Value: ${data.objective_value}<br />
          Investments: ${data.solutions.join(', ')}
        `,
      });
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  return (
    <>
      <div id="map-container" ref={mapContainerRef} className="h-screen" />
      {/* Card overlay */}
      <div className="absolute top-0 left-5 mt-5 mb-5 bg-white p-6 rounded-lg shadow-lg w-96 h-[calc(100%-2rem)] z-10 overflow-auto">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Model Type Selection */}
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

          {/* Total Layers Slider */}
          <div className="form-group">
            <label htmlFor="total_layers" className="block font-semibold mb-2">
              Total Layers:
            </label>
            <div className="flex items-center space-x-4">
              <input
                type="range"
                id="total_layers"
                name="total_layers"
                min="1"
                max="2" // Max value updated to 2
                step="1"
                value={totalLayers}
                onChange={(e) => syncSlider(setTotalLayers, e.target.value)}
                className="slider w-full"
              />
              <input
                type="number"
                id="total_layers_input"
                min="1"
                max="2" // Max value updated to 2
                value={totalLayers}
                onChange={(e) => syncSlider(setTotalLayers, e.target.value)}
                className="w-16 border border-gray-300 rounded px-2 py-1"
              />
            </div>
          </div>

          {/* Resource Slider */}
          <div className="form-group">
            <label htmlFor="resource" className="block font-semibold mb-2">
              Resource:
            </label>
            <div className="flex items-center space-x-4">
              <input
                type="range"
                id="resource"
                name="resource"
                min="0"
                max="500"
                step="5"
                value={resource}
                onChange={(e) => syncSlider(setResource, e.target.value)}
                className="slider w-full"
              />
              <input
                type="number"
                id="resource_input"
                min="0"
                max="500"
                step="5"
                value={resource}
                onChange={(e) => syncSlider(setResource, e.target.value)}
                className="w-16 border border-gray-300 rounded px-2 py-1"
              />
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="btn bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition"
          >
            Update
          </button>
        </form>
      </div>

      {sidebarData && (
        <div
            className="absolute top-0 right-5 mt-5 mb-5 bg-white p-6 rounded-lg shadow-lg w-96 h-[calc(100%-2rem)] z-10 overflow-auto"
            style={{ width: '24rem', height: 'calc(100% - 2rem)' }} // Match dimensions to the left sidebar
        >
            <h2 className="text-lg font-semibold mb-4">{sidebarData.title}</h2>
            <p dangerouslySetInnerHTML={{ __html: sidebarData.description }} />
        </div>
        )}

    </>
  );
}

export default Map;
