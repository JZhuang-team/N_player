import React from 'react';

const MainContent = () => {
  const handleApplyMetric = (metric) => {
    console.log(`Apply metric: ${metric}`);
  };

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <div className="sidebar w-80 bg-gray-100 p-4 border-r">
        {/* Form container */}
        <div className="form-container">
          <div className="page-header mb-4">
            <h2 className="text-lg font-semibold">Configuration</h2>
          </div>

          {/* Model selection form */}
          <form action="result.html" method="post" className="space-y-4">
            {/* Model Type selection */}
            <div className="form-group">
              <label className="block mb-2 font-medium">Model Type:</label>
              <div className="flex items-center space-x-4">
                <div className="flex items-center">
                  <input
                    type="radio"
                    id="prob"
                    name="model_type"
                    className="mr-2"
                    value="prob"
                    defaultChecked
                  />
                  <label htmlFor="prob">Probabilistic Model</label>
                </div>
                {/* Uncomment for Strategic Model */}
                {/* <div className="flex items-center">
                  <input
                    type="radio"
                    id="stra"
                    name="model_type"
                    className="mr-2"
                    value="stra"
                  />
                  <label htmlFor="stra">Strategic Model</label>
                </div> */}
              </div>
            </div>

            {/* Total Layers slider */}
            <div className="form-group">
              <label htmlFor="total_layers" className="block mb-2 font-medium">
                Total Layers:
              </label>
              <div className="slider-container flex items-center space-x-4">
                <input
                  type="range"
                  className="slider flex-1"
                  name="total_layers"
                  id="total_layers"
                  min="1"
                  max="10"
                  step="1"
                  onInput={(e) => console.log(e.target.value)}
                />
                <input
                  type="number"
                  id="total_layers_input"
                  className="border rounded w-16"
                  min="1"
                  max="10"
                  onInput={(e) => console.log(e.target.value)}
                />
              </div>
            </div>

            {/* Resource slider */}
            <div className="form-group">
              <label htmlFor="C_bar_init" className="block mb-2 font-medium">
                Resource:
              </label>
              <div className="slider-container flex items-center space-x-4">
                <input
                  type="range"
                  className="slider flex-1"
                  name="C_bar_init"
                  id="C_bar_init"
                  min="0"
                  max="500"
                  step="5"
                  onInput={(e) => console.log(e.target.value)}
                />
                <input
                  type="number"
                  id="C_bar_init_input"
                  className="border rounded w-16"
                  min="0"
                  max="500"
                  step="5"
                  onInput={(e) => console.log(e.target.value)}
                />
              </div>
            </div>

            {/* Submit button */}
            <button type="submit" className="btn btn-primary bg-blue-500 text-white px-4 py-2 rounded">
              Update
            </button>
          </form>
        </div>
      </div>

      {/* Map Area */}
      <div className="map-area flex-1 relative">
        {/* Placeholder for actual map content */}
        <div id="map" className="map-canvas h-full bg-gray-200"></div>
        
        {/* Buttons for Map Controls */}
        <div className="top-right-buttons absolute top-4 right-4 flex flex-col space-y-2">
          <button
            onClick={() => handleApplyMetric('mainpage')}
            className="btn btn-map bg-blue-500 text-white px-4 py-2 rounded"
          >
            Return to Main
          </button>
          <button
            onClick={() => handleApplyMetric('consequence')}
            className="btn btn-map bg-blue-500 text-white px-4 py-2 rounded"
          >
            Consequence
          </button>
          <button
            onClick={() => handleApplyMetric('vulnerability')}
            className="btn btn-map bg-blue-500 text-white px-4 py-2 rounded"
          >
            Vulnerability
          </button>
          <button
            onClick={() => handleApplyMetric('threat')}
            className="btn btn-map bg-blue-500 text-white px-4 py-2 rounded"
          >
            Threat
          </button>
          <button
            onClick={() => handleApplyMetric('risk')}
            className="btn btn-map bg-blue-500 text-white px-4 py-2 rounded"
          >
            Risk
          </button>
          <button
            onClick={() => handleApplyMetric('investment')}
            className="btn btn-map bg-blue-500 text-white px-4 py-2 rounded"
          >
            Investment
          </button>
        </div>
      </div>
    </div>
  );
};

export default MainContent;
