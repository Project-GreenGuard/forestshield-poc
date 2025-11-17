export default function AlertBanner({ fires = [] }) {
  // Check if any fire has high risk
  const hasHighRisk = fires.some((fire) => fire.risk === "High");

  if (!hasHighRisk) {
    return null;
  }

  return (
    <div
      style={{
        gridArea: "alert",
        background: "linear-gradient(135deg, #DC2626, #B91C1C)",
        color: "white",
        padding: "15px 30px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: "18px",
        fontWeight: "bold",
        boxShadow: "0 4px 12px rgba(220, 38, 38, 0.4)",
        animation: "pulse 2s infinite",
      }}
    >
      ⚠️ HIGH RISK WILDFIRE DETECTED — IMMEDIATE ATTENTION REQUIRED
    </div>
  );
}
