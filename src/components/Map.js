import { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';

import 'mapbox-gl/dist/mapbox-gl.css';

function Map() {
  const mapRef = useRef();
  const mapContainerRef = useRef();

  const [modelType, setModelType] = useState('prob');
  const [totalLayers, setTotalLayers] = useState(1);
  const [resource, setResource] = useState(0);

  const handleSubmit = (event) => {
    event.preventDefault(); // Prevent default form submission
    console.log({ modelType, totalLayers, resource });
  };

  const syncSlider = (setter, value) => {
    setter(value);
  };

  useEffect(() => {
    mapboxgl.accessToken = 'pk.eyJ1IjoiZG9yamVlbGEiLCJhIjoiY20ybWJqZnlzMGtobTJrcHc3b2Rid3VmdiJ9.9xXysCma-jzUl_MvQh16Xw';
    mapRef.current = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: 'mapbox://styles/dorjeela/cm2f5v601008p01nxfdd725ms',
      center: [-78.786058, 43.001150], // Set a center coordinate
      zoom: 16,
    });

    return () => {
      mapRef.current.remove();
    };
  }, []);

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
                max="10"
                step="1"
                value={totalLayers}
                onChange={(e) => syncSlider(setTotalLayers, e.target.value)}
                className="slider w-full"
              />
              <input
                type="number"
                id="total_layers_input"
                min="1"
                max="10"
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
    </>
  );
}

export default Map;
