import { useState, useEffect } from 'react';
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import MapArea from "./components/MapArea";
import DataPanel from "./components/DataPanel";
import AlertBanner from "./components/AlertBanner";
import { getFires } from "./services/fireService";
import "./App.css";

function App() {
  const [fires, setFires] = useState([]);

  useEffect(() => {
    const fetchFires = async () => {
      const fireData = await getFires();
      setFires(fireData);
    };
    
    // Initial fetch
    fetchFires();
    
    // Auto-refresh every 10 seconds to update alerts
    const interval = setInterval(fetchFires, 10000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="dashboard">
      <Sidebar />
      <Topbar />
      <AlertBanner fires={fires} />
      <MapArea />
      <DataPanel />
    </div>
  );
}

export default App;
