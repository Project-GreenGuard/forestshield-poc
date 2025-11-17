import { useEffect, useState } from "react";
import { getFires } from "../services/fireService";

/**
 * Converts lat/lng coordinates to x/y pixels for display on map
 * Simple mapping for demo purposes (Alberta/BC region approximation)
 */
function latLngToXY(lat, lng) {
  // Map coordinates: roughly Alberta/BC region
  // lat range: ~49-54, lng range: ~-120 to -110
  const minLat = 49;
  const maxLat = 54;
  const minLng = -120;
  const maxLng = -110;

  // Map to pixel coordinates (with padding)
  const padding = 40;
  const mapWidth = 800 - padding * 2;
  const mapHeight = 600 - padding * 2;

  const x = padding + ((lng - minLng) / (maxLng - minLng)) * mapWidth;
  const y = padding + ((maxLat - lat) / (maxLat - minLat)) * mapHeight;

  return { x, y };
}

function getRiskColor(risk) {
  switch (risk) {
    case "High":
      return "#DC2626"; // Red
    case "Moderate":
      return "#FF7A00"; // Orange
    case "Low":
      return "#FCD34D"; // Yellow
    default:
      return "#B22222"; // Default red
  }
}

export default function MapArea() {
  const [fires, setFires] = useState([]);

  useEffect(() => {
    const fetchFires = async () => {
      const fireData = await getFires();
      setFires(fireData);
    };

    fetchFires();
    // Auto-refresh every 10 seconds
    const interval = setInterval(fetchFires, 10000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div
      style={{
        gridArea: "map",
        background: "#242424",
        position: "relative",
        margin: 20,
        borderRadius: 10,
        overflow: "hidden",
      }}
    >
      {fires.map((fire) => {
        const { x, y } = latLngToXY(fire.lat, fire.lng);
        const color = getRiskColor(fire.risk);
        const isHighRisk = fire.risk === "High";

        return (
          <div key={fire.id}>
            {/* Predicted zone circle for high-risk fires */}
            {isHighRisk && (
              <div
                style={{
                  position: "absolute",
                  top: y - 40,
                  left: x - 40,
                  width: 80,
                  height: 80,
                  borderRadius: "50%",
                  border: `2px dashed ${color}`,
                  opacity: 0.3,
                  pointerEvents: "none",
                }}
              />
            )}
            {/* Fire marker */}
            <div
              style={{
                position: "absolute",
                top: y - 8,
                left: x - 8,
                width: 16,
                height: 16,
                borderRadius: "50%",
                background: color,
                border: "2px solid white",
                boxShadow: `0 0 10px ${color}`,
                cursor: "pointer",
              }}
              title={`${fire.name} - Risk: ${fire.risk}`}
            />
          </div>
        );
      })}
      <p
        style={{
          position: "absolute",
          bottom: 10,
          left: 10,
          fontSize: 14,
          color: "#B0B0B0",
        }}
      >
        🔴 Active Fire 🟠 Predicted Zone 🟩 Safe Route
      </p>
    </div>
  );
}
