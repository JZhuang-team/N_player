import React from 'react';
import Map from './components/Map';
import Sidebar from './components/Sidebar';

function App() {
  const handleSidebarUpdate = (data) => {
    console.log(data); // Process sidebar updates here
  };

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
