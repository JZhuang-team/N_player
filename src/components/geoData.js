// Original Building and Road Data
export const buildings = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      properties: {
        title: "Student Union",
        description: "Student Union",
      },
      geometry: {
        coordinates: [
          [
            [-78.786683, 43.001566],
            [-78.786266, 43.001567],
            [-78.786266, 43.001514],
            [-78.78613, 43.001514],
            [-78.786029, 43.001498],
            [-78.785933, 43.00146],
            [-78.78586, 43.001405],
            [-78.785809, 43.001345],
            [-78.785779, 43.001268],
            [-78.785778, 43.001156],
            [-78.785701, 43.001155],
            [-78.785699, 43.000859],
            [-78.786804, 43.000857],
            [-78.786807, 43.001235],
            [-78.78657, 43.001236],
            [-78.786571, 43.001266],
            [-78.78668, 43.001265],
            [-78.786683, 43.001566],
          ],
        ],
        type: "Polygon",
      },
    },
  ],
};

export const roads = {
  type: "Feature",
  properties: {
    title: "Mary Talbert Way",
    description: "Mary Talbert Way",
  },
  geometry: {
    coordinates: [
      [-78.785381, 42.999812],
      [-78.785388, 43.001257],
      [-78.785459, 43.001387],
      [-78.785619, 43.001533],
      [-78.785896, 43.0017],
      [-78.786026, 43.00173],
      [-78.786136, 43.001745],
      [-78.78869, 43.001745],
      [-78.788828, 43.001715],
      [-78.788999, 43.00163],
      [-78.789219, 43.001524],
      [-78.789397, 43.001479],
      [-78.789647, 43.001472],
      [-78.792954, 43.001454],
      [-78.79317, 43.001396],
      [-78.793285, 43.001304],
      [-78.793766, 43.000842],
      [-78.793766, 43.000392],
      [-78.793701, 43.000289],
      [-78.793586, 43.000238],
      [-78.79345, 43.000223],
      [-78.792914, 43.000216],
      [-78.79276, 43.000175],
      [-78.79266, 43.000096],
      [-78.792595, 42.999964],
      [-78.792595, 42.999775],
      [-78.792545, 42.999654],
      [-78.792401, 42.999565],
      [-78.792142, 42.999534],
      [-78.791517, 42.999534],
      [-78.790756, 42.999539],
      [-78.789844, 42.999555],
      [-78.789679, 42.999602],
      [-78.789556, 42.999728],
      [-78.789535, 43.000196],
      [-78.789449, 43.000311],
      [-78.789248, 43.000364],
      [-78.788989, 43.000348],
      [-78.788854, 43.000306],
      [-78.788669, 43.00018],
      [-78.78852, 43.00016],
      [-78.787609, 43.000161],
      [-78.787388, 43.000136],
      [-78.787023, 42.999996],
      [-78.786575, 42.999829],
      [-78.786405, 42.999806],
      [-78.786149, 42.999815],
      [-78.785376, 42.999812],
    ],
    type: "LineString",
  },
};

// Utility function to convert LineString or Polygon features to points
function lineToPoints(lineFeature, spacing = 0.0001) {
  const points = [];
  const coordinates =
    lineFeature.geometry.type === "Polygon"
      ? lineFeature.geometry.coordinates[0] // Get the outer ring of the Polygon
      : lineFeature.geometry.coordinates; // For LineString

  for (let i = 0; i < coordinates.length - 1; i++) {
    const [x1, y1] = coordinates[i];
    const [x2, y2] = coordinates[i + 1];

    const distance = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
    const steps = Math.ceil(distance / spacing);

    for (let j = 0; j <= steps; j++) {
      const t = j / steps;
      const x = x1 + t * (x2 - x1);
      const y = y1 + t * (y2 - y1);
      points.push({
        type: "Feature",
        geometry: {
          type: "Point",
          coordinates: [x, y],
        },
        properties: { ...lineFeature.properties }, // Preserve original properties
      });
    }
  }

  return points;
}

function convertGeoDataToPoints(geoJSON, spacing = 0.0001) {
  return {
    type: "FeatureCollection",
    features: geoJSON.features.flatMap((feature) =>
      feature.geometry.type === "LineString" || feature.geometry.type === "Polygon"
        ? lineToPoints(feature, spacing)
        : []
    ),
  };
}

// Generate heatmap-ready data for roads and buildings
export const heatmapBuildings = convertGeoDataToPoints(buildings, 0.0001); // Adjust spacing as needed
export const heatmapRoads = convertGeoDataToPoints({ type: "FeatureCollection", features: [roads] }, 0.0001);
