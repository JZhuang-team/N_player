import React from 'react';
import Map from './components/Map';

function App() {

  return (
    <div className="flex h-screen w-screen">
      {/* Map */}
      <div className="flex-1">
        <Map />
      </div>
    </div>
  );
}

export default App;
