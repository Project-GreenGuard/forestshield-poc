import { useEffect, useState } from "react";
import { getTemperature, getSummary } from "../services/fireService";

export default function DataPanel() {
  const [temperature, setTemperature] = useState(null);
  const [summary, setSummary] = useState({
    averageTemperature: 0,
    highRiskCount: 0,
    timestamp: null,
  });

  useEffect(() => {
    const fetchData = async () => {
      // Fetch current temperature
      const temp = await getTemperature();
      setTemperature(temp);

      // Fetch summary stats
      const summaryData = await getSummary();
      setSummary(summaryData);
    };

    // Initial fetch
    fetchData();

    // Auto-refresh every 10 seconds
    const interval = setInterval(fetchData, 10000);

    return () => clearInterval(interval);
  }, []);

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return "--";
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };

  return (
    <div
      style={{
        gridArea: "panel",
        background: "#181818",
        padding: 20,
      }}
    >
      <h3 style={{ color: "#FF7A00", marginTop: 0 }}>Live Data</h3>

      {/* Current Temperature */}
      <div
        style={{
          background: "#2A2A2A",
          padding: "20px 15px",
          marginTop: 10,
          borderRadius: 10,
          boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
        }}
      >
        <div style={{ color: "#B0B0B0", fontSize: 14, marginBottom: 5 }}>
          Temperature 🌡️
        </div>
        <div
          style={{
            fontSize: 24,
            fontWeight: "bold",
            color: temperature ? "#FF7A00" : "#666",
          }}
        >
          {temperature !== null ? `${temperature}°C` : "--°C"}
        </div>
      </div>

      {/* Average Temperature */}
      <div
        style={{
          background: "#2A2A2A",
          padding: "20px 15px",
          marginTop: 10,
          borderRadius: 10,
          boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
        }}
      >
        <div style={{ color: "#B0B0B0", fontSize: 14, marginBottom: 5 }}>
          Avg Temperature 🌡️
        </div>
        <div style={{ fontSize: 24, fontWeight: "bold", color: "#FF7A00" }}>
          {summary.averageTemperature}°C
        </div>
      </div>

      {/* High Risk Count */}
      <div
        style={{
          background: summary.highRiskCount > 0 ? "#DC2626" : "#2A2A2A",
          padding: "20px 15px",
          marginTop: 10,
          borderRadius: 10,
          boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
          transition: "background 0.3s",
        }}
      >
        <div
          style={{
            color: summary.highRiskCount > 0 ? "#FFF" : "#B0B0B0",
            fontSize: 14,
            marginBottom: 5,
          }}
        >
          High Risk Fires ⚠️
        </div>
        <div
          style={{
            fontSize: 24,
            fontWeight: "bold",
            color: summary.highRiskCount > 0 ? "#FFF" : "#DC2626",
          }}
        >
          {summary.highRiskCount}
        </div>
      </div>

      {/* Last Updated */}
      <div
        style={{
          background: "#2A2A2A",
          padding: "15px",
          marginTop: 10,
          borderRadius: 10,
          boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
          fontSize: 12,
          color: "#666",
          textAlign: "center",
        }}
      >
        Last updated: {formatTimestamp(summary.timestamp)}
      </div>
    </div>
  );
}
