import { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import { buildings, roads } from './geoData'; // Import the data
import Sidebar from './Sidebar'; // Import Sidebar component

import 'mapbox-gl/dist/mapbox-gl.css';

function Map() {
  const mapRef = useRef();
  const mapContainerRef = useRef();
  const [modelType, setModelType] = useState('prob');
  const [totalLayers, setTotalLayers] = useState(1);
  const [resource, setResource] = useState(0);
  const [layersVisible, setLayersVisible] = useState(false); // Manage layer visibility
  const [sidebarData, setSidebarData] = useState(null); // Data for the right sidebar

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

          map.addLayer({
            id: 'building-layer2',
            type: 'fill',
            source: 'buildings',
            paint: {
              'fill-opacity': 0,
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
      }
    });

    return () => {
      map.remove();
    };
  }, [layersVisible]);

  const handleSubmit = (event) => {
    event.preventDefault();
    setLayersVisible(true); // Show layers when the button is pressed
    console.log({ modelType, totalLayers, resource });
  };

  return (
    <>
      <div id="map-container" ref={mapContainerRef} className="h-screen" />
      {/* Left Sidebar */}
      <Sidebar
        modelType={modelType}
        setModelType={setModelType}
        totalLayers={totalLayers}
        setTotalLayers={setTotalLayers}
        resource={resource}
        setResource={setResource}
        onSubmit={handleSubmit}
      />
      {/* Right Sidebar */}
      {sidebarData && (
        <div className="absolute top-0 right-5 mt-5 mb-5 bg-white p-6 rounded-lg shadow-lg w-96 h-auto z-10 overflow-auto">
          <h2 className="text-lg font-semibold mb-4">{sidebarData.title}</h2>
          <p>{sidebarData.description}</p>
        </div>
      )}
    </>
  );
}

export default Map;
