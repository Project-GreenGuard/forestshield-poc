from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime, timedelta
import requests

app = Flask(__name__)
CORS(app)

# ------------------------------
# SENSOR MODEL
# ------------------------------
sensors = {
    "oakville-1": {
        "id": "oakville-1",
        "name": "Oakville Sensor 1",
        "city": "Oakville",
        "lat": 43.4675,
        "lng": -79.6877,
        "temperature": None,   # from physical sensor
        "humidity": None,
        "wind_speed": None,
        "uv_index": None,
        "pm2_5": None,
        "pm10": None,
        "aqi_us": None,
        "fire_risk": None,
        "last_update": None,
    },
    "oakville-2": {
        "id": "oakville-2",
        "name": "Oakville Sensor 2",
        "city": "Oakville",
        "lat": 43.4675,
        "lng": -79.6877,
        "temperature": None,   # from physical sensor
        "humidity": None,
        "wind_speed": None,
        "uv_index": None,
        "pm2_5": None,
        "pm10": None,
        "aqi_us": None,
        "fire_risk": None,
        "last_update": None,
    },

    # Virtual sensors (driven by live APIs)
    "toronto-1": {
        "id": "toronto-1",
        "name": "Toronto Central",
        "city": "Toronto",
        "lat": 43.6532,
        "lng": -79.3832,
        "temperature": None,
        "humidity": None,
        "wind_speed": None,
        "uv_index": None,
        "pm2_5": None,
        "pm10": None,
        "aqi_us": None,
        "fire_risk": None,
        "last_update": None,
    },
    "mississauga-1": {
        "id": "mississauga-1",
        "name": "Mississauga West",
        "city": "Mississauga",
        "lat": 43.5890,
        "lng": -79.6441,
        "temperature": None,
        "humidity": None,
        "wind_speed": None,
        "uv_index": None,
        "pm2_5": None,
        "pm10": None,
        "aqi_us": None,
        "fire_risk": None,
        "last_update": None,
    },
    "brampton-1": {
        "id": "brampton-1",
        "name": "Brampton North",
        "city": "Brampton",
        "lat": 43.7315,
        "lng": -79.7624,
        "temperature": None,
        "humidity": None,
        "wind_speed": None,
        "uv_index": None,
        "pm2_5": None,
        "pm10": None,
        "aqi_us": None,
        "fire_risk": None,
        "last_update": None,
    },
    "vaughan-1": {
        "id": "vaughan-1",
        "name": "Vaughan Hills",
        "city": "Vaughan",
        "lat": 43.8372,
        "lng": -79.5083,
        "temperature": None,
        "humidity": None,
        "wind_speed": None,
        "uv_index": None,
        "pm2_5": None,
        "pm10": None,
        "aqi_us": None,
        "fire_risk": None,
        "last_update": None,
    },
    "markham-1": {
        "id": "markham-1",
        "name": "Markham East",
        "city": "Markham",
        "lat": 43.8561,
        "lng": -79.3370,
        "temperature": None,
        "humidity": None,
        "wind_speed": None,
        "uv_index": None,
        "pm2_5": None,
        "pm10": None,
        "aqi_us": None,
        "fire_risk": None,
        "last_update": None,
    },
    "pickering-1": {
        "id": "pickering-1",
        "name": "Pickering Lakeside",
        "city": "Pickering",
        "lat": 43.8373,
        "lng": -79.0892,
        "temperature": None,
        "humidity": None,
        "wind_speed": None,
        "uv_index": None,
        "pm2_5": None,
        "pm10": None,
        "aqi_us": None,
        "fire_risk": None,
        "last_update": None,
    },
}

# simple cache for external API refresh
last_refresh = None

# ------------------------------
# LIVE DATA HELPERS (Open-Meteo)
# ------------------------------

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


def fetch_live_weather(lat, lng):
    """Current temperature, humidity, wind, UV (no API key needed)."""
    params = {
        "latitude": lat,
        "longitude": lng,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,uv_index",
        "timezone": "auto",
    }
    try:
        r = requests.get(WEATHER_URL, params=params, timeout=5)
        r.raise_for_status()
        cur = r.json().get("current", {})
        return {
            "temperature": cur.get("temperature_2m"),
            "humidity": cur.get("relative_humidity_2m"),
            "wind_speed": cur.get("wind_speed_10m"),
            "uv_index": cur.get("uv_index"),
        }
    except Exception:
        return {
            "temperature": None,
            "humidity": None,
            "wind_speed": None,
            "uv_index": None,
        }


def fetch_live_air(lat, lng):
    """Current PM2.5, PM10, US AQI, UV index from Open-Meteo Air Quality."""
    params = {
        "latitude": lat,
        "longitude": lng,
        "current": "pm2_5,pm10,us_aqi,uv_index",
        "timezone": "auto",
    }
    try:
        r = requests.get(AIR_QUALITY_URL, params=params, timeout=5)
        r.raise_for_status()
        cur = r.json().get("current", {})
        return {
            "pm2_5": cur.get("pm2_5"),
            "pm10": cur.get("pm10"),
            "aqi_us": cur.get("us_aqi"),
            "uv_index": cur.get("uv_index"),
        }
    except Exception:
        return {
            "pm2_5": None,
            "pm10": None,
            "aqi_us": None,
            "uv_index": None,
        }


def classify_fire_risk(temp, humidity, wind_speed, aqi):
    """Simple custom fire-risk logic for the dashboard."""
    if temp is None or humidity is None or wind_speed is None:
        return "Unknown"

    risk_score = 0

    if temp >= 35:
        risk_score += 3
    elif temp >= 30:
        risk_score += 2
    elif temp >= 25:
        risk_score += 1

    if humidity <= 25:
        risk_score += 3
    elif humidity <= 40:
        risk_score += 2
    elif humidity <= 60:
        risk_score += 1

    if wind_speed >= 30:
        risk_score += 3
    elif wind_speed >= 20:
        risk_score += 2
    elif wind_speed >= 10:
        risk_score += 1

    if aqi is not None:
        if aqi >= 150:
            risk_score += 2
        elif aqi >= 100:
            risk_score += 1

    if risk_score >= 8:
        return "Extreme"
    elif risk_score >= 6:
        return "High"
    elif risk_score >= 3:
        return "Moderate"
    else:
        return "Low"


def refresh_live_data():
    """Update all city sensors with live weather + air quality."""
    for sid, s in sensors.items():
        lat = s.get("lat")
        lng = s.get("lng")
        if lat is None or lng is None:
            continue

        weather = fetch_live_weather(lat, lng)
        air = fetch_live_air(lat, lng)

        # Virtual sensors: temperature from API
        if not sid.startswith("oakville"):
            if weather["temperature"] is not None:
                s["temperature"] = round(weather["temperature"], 1)
        # Oakville: keep sensor temp, fill only if missing
        else:
            if s["temperature"] is None and weather["temperature"] is not None:
                s["temperature"] = round(weather["temperature"], 1)

        s["humidity"] = weather["humidity"]
        s["wind_speed"] = weather["wind_speed"]
        s["uv_index"] = air["uv_index"] if air["uv_index"] is not None else weather["uv_index"]
        s["pm2_5"] = air["pm2_5"]
        s["pm10"] = air["pm10"]
        s["aqi_us"] = air["aqi_us"]

        s["fire_risk"] = classify_fire_risk(
            s["temperature"], s["humidity"], s["wind_speed"], s["aqi_us"]
        )
        s["last_update"] = datetime.utcnow().isoformat()


# ------------------------------
# DASHBOARD HTML
# ------------------------------
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>GreenGuard Wildfire Dashboard</title>

    <link rel="stylesheet"
     href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />

    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #050505;
            color: #f5f5f5;
            font-family: Arial, sans-serif;
        }

        /* TOP NAV */
        .top-bar {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 70px;
            background: #0d0d0d;
            display: flex;
            align-items: center;
            padding: 0 20px;
            border-bottom: 2px solid #222;
            z-index: 1000;
        }

        .top-logo {
            height: 55px;
            width: auto;
            object-fit: contain;
            margin-right: 15px;
        }
        .top-title {
            font-size: 24px;
            font-weight: bold;
            color: #00ff88;
        }

        /* FOOTER */
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 40px;
            background-color: #0d0d0d;
            color: #888;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            border-top: 2px solid #222;
            z-index: 1000;
        }
        .ssu {
            color: #00ff88;
            font-weight: bold;
        }

        /* LAYOUT */
        .main-layout {
            margin-top: 70px;
            margin-bottom: 40px;
            display: flex;
            height: calc(100vh - 110px);
        }

        .left-panel {
            width: 22%;
            background: #111;
            padding: 20px;
            border-right: 2px solid #222;
            display: flex;
            flex-direction: column;
        }

        .map-panel {
            flex: 1;
            position: relative;
        }

        /* THIS IS IMPORTANT: makes the map visible */
        #map {
            width: 100%;
            height: 100%;
        }

        .right-panel {
            width: 25%;
            background: #111;
            padding: 20px;
            border-left: 2px solid #222;
            display: flex;
            flex-direction: column;
        }

        .panel-title {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 10px;
        }

        /* ALERTS */
        .alerts-list {
            list-style: none;
            padding-left: 0;
            margin-top: 10px;
            overflow-y: auto;
            flex: 1;
        }
        .alert-item {
            background: #1a1a1a;
            border-left: 5px solid #ff4d4d;
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 6px;
            font-size: 14px;
        }
        .alert-item.warning {
            border-left-color: #ffcc33;
        }

        /* SENSOR CARDS */
        .sensor-list {
            overflow-y: auto;
            flex: 1;
        }
        .sensor-card {
            background: #1a1a1a;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .sensor-name {
            font-weight: bold;
        }
        .sensor-city {
            font-size: 12px;
            color: #aaa;
        }
        .sensor-temp {
            font-size: 18px;
            font-weight: bold;
            margin-top: 4px;
        }
        .sensor-extra {
            font-size: 12px;
            color: #ccc;
            margin-top: 4px;
            line-height: 1.4;
        }
        .sensor-risk {
            font-size: 12px;
            margin-top: 4px;
        }

        .chip {
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            margin-left: 5px;
        }
        .chip-ok { background: #0b5; color: #000; }
        .chip-warn { background: #ffcc33; color: #000; }
        .chip-critical { background: #ff4d4d; color: #000; }
        .chip-nodata { background: #555; color: #eee; }

        .chip-risk-low { background: #0b5; color: #000; }
        .chip-risk-moderate { background: #ffcc33; color: #000; }
        .chip-risk-high { background: #ff8800; color: #000; }
        .chip-risk-extreme { background: #ff4d4d; color: #000; }
    </style>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
</head>

<body>

    <!-- TOP BAR -->
    <div class="top-bar">
        <img src="/static/prologo.png" class="top-logo">
        <span class="top-title">GreenGuard Wildfire Dashboard</span>
    </div>

    <div class="main-layout">

        <!-- LEFT PANEL (ALERTS) -->
        <div class="left-panel">
            <div class="panel-title">Alerts & Warnings</div>
            <ul id="alerts" class="alerts-list"></ul>
        </div>

        <!-- MAP -->
        <div class="map-panel">
            <div id="map"></div>
        </div>

        <!-- RIGHT PANEL (SENSORS) -->
        <div class="right-panel">
            <div class="panel-title">Live Sensors</div>
            <div id="sensor-list" class="sensor-list"></div>
        </div>
    </div>

    <!-- FOOTER -->
    <div class="footer">
        © 2025 GreenGuard | AI-Driven Disaster Response System |
        <span class="ssu">SSU</span>
    </div>

    <script>
        // ---------------------------
        // INIT LEAFLET MAP
        // ---------------------------
        let map = L.map("map").setView([43.6532, -79.3832], 9);
        let markers = {};

        // Base map
        let baseMap = L.tileLayer(
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            { maxZoom: 18 }
        ).addTo(map);

        // LIVE SMOKE MAP LAYER (NOAA HRRR)
        let smokeLayer = L.tileLayer(
            "https://tiles.airfire.org/hrrr-smoke/v1/forecast/sfc_smoke/{z}/{x}/{y}.png",
            {
                opacity: 0.6,
                attribution: "NOAA HRRR Smoke Model",
                maxZoom: 12
            }
        );
        smokeLayer.addTo(map);

        // Layer toggle
        L.control.layers(
            { "Base Map": baseMap },
            { "Smoke (HRRR Forecast)": smokeLayer }
        ).addTo(map);

        // ---------------------------
        // NASA FIRMS HOTSPOTS (FREE-ish)
        // ---------------------------
        const FIRMS_URL =
          "https://firms.modaps.eosdis.nasa.gov/api/country/csv/CAN/VIIRS_SNPP_NRT/24";

        let fireMarkers = [];

        function parseCSV(csv) {
            const lines = csv.split("\\n");
            const headers = lines[0].split(",");
            let data = [];
            for (let i = 1; i < lines.length; i++) {
                const row = lines[i].split(",");
                if (row.length === headers.length) {
                    let obj = {};
                    headers.forEach((h, idx) => obj[h] = row[idx]);
                    data.push(obj);
                }
            }
            return data;
        }

        function loadFireData() {
            fetch(FIRMS_URL)
                .then(r => r.text())
                .then(csv => {
                    fireMarkers.forEach(m => map.removeLayer(m));
                    fireMarkers = [];

                    const fires = parseCSV(csv);

                    fires.forEach(f => {
                        if (!f.latitude || !f.longitude) return;

                        const marker = L.circleMarker(
                            [parseFloat(f.latitude), parseFloat(f.longitude)],
                            {
                                radius: 6,
                                fillColor: "#ff3300",
                                color: "#660000",
                                weight: 1,
                                fillOpacity: 0.9
                            }
                        ).addTo(map);

                        marker.bindPopup(
                          "<b>🔥 Satellite Fire Detection</b><br>" +
                          "Brightness: " + f.brightness + "<br>" +
                          "Confidence: " + f.confidence + "%<br>" +
                          "Time: " + f.acq_date + " " + f.acq_time
                        );

                        fireMarkers.push(marker);
                    });
                })
                .catch(err => {
                    console.error("FIRMS load failed:", err);
                });
        }

        loadFireData();
        // 15 minutes
        setInterval(loadFireData, 15 * 60 * 1000);

        // ---------------------------
        // SENSOR UPDATES
        // ---------------------------
        function tempStatus(temp) {
            if (temp == null) return "nodata";
            if (temp >= 40) return "critical";
            if (temp >= 35) return "warning";
            return "ok";
        }

        function riskChipClass(risk) {
            if (!risk) return "chip-nodata";
            risk = risk.toLowerCase();
            if (risk === "low") return "chip-risk-low";
            if (risk === "moderate") return "chip-risk-moderate";
            if (risk === "high") return "chip-risk-high";
            if (risk === "extreme") return "chip-risk-extreme";
            return "chip-nodata";
        }

        function aqiLabel(aqi) {
            if (aqi == null) return "Unknown";
            if (aqi <= 50) return "Good";
            if (aqi <= 100) return "Moderate";
            if (aqi <= 150) return "Unhealthy (SG)";
            if (aqi <= 200) return "Unhealthy";
            if (aqi <= 300) return "Very Unhealthy";
            return "Hazardous";
        }

        function updateUI() {
            fetch("/api/temperature")
            .then(r => r.json())
            .then(data => {
                let sensorList = document.getElementById("sensor-list");
                let alertList = document.getElementById("alerts");

                sensorList.innerHTML = "";
                alertList.innerHTML = "";

                data.sensors.forEach(s => {
                    let st = tempStatus(s.temperature);

                    // --- RIGHT PANEL ---
                    let card = document.createElement("div");
                    card.className = "sensor-card";

                    const humTxt = s.humidity != null ? s.humidity + "%" : "--";
                    const windTxt = s.wind_speed != null ? s.wind_speed + " km/h" : "--";
                    const aqiTxt = s.aqi_us != null ? s.aqi_us : "--";
                    const uvTxt = s.uv_index != null ?
                        (s.uv_index.toFixed ? s.uv_index.toFixed(1) : s.uv_index) : "--";
                    const pm25Txt = s.pm2_5 != null ?
                        (s.pm2_5.toFixed ? s.pm2_5.toFixed(1) : s.pm2_5) : "--";
                    const pm10Txt = s.pm10 != null ?
                        (s.pm10.toFixed ? s.pm10.toFixed(1) : s.pm10) : "--";

                    card.innerHTML = `
                        <div class="sensor-name">${s.name}</div>
                        <div class="sensor-city">${s.city}</div>
                        <div class="sensor-temp">
                            ${s.temperature != null ? s.temperature + "°C" : "--°C"}
                            <span class="chip ${
                                st === "ok" ? "chip-ok" :
                                st === "warning" ? "chip-warn" :
                                st === "critical" ? "chip-critical" :
                                "chip-nodata"
                            }">${
                                st === "ok" ? "Normal" :
                                st === "warning" ? "Warning" :
                                st === "critical" ? "Critical" :
                                "No Data"
                            }</span>
                        </div>
                        <div class="sensor-extra">
                            Humidity: ${humTxt} · Wind: ${windTxt}<br>
                            AQI (US): ${aqiTxt} (${aqiLabel(s.aqi_us)}) · UV: ${uvTxt}<br>
                            PM2.5: ${pm25Txt} µg/m³ · PM10: ${pm10Txt} µg/m³
                        </div>
                        <div class="sensor-risk">
                            Fire Risk:
                            <span class="chip ${riskChipClass(s.fire_risk)}">
                                ${s.fire_risk || "Unknown"}
                            </span>
                        </div>
                    `;
                    sensorList.appendChild(card);

                    // --- ALERTS ---
                    if (st === "warning" || st === "critical" ||
                        (s.fire_risk && (s.fire_risk === "High" || s.fire_risk === "Extreme"))) {
                        let alert = document.createElement("li");
                        alert.className =
                          "alert-item " + (st === "warning" ? "warning" : "");
                        alert.innerHTML =
                          `<b>${(s.fire_risk || st).toUpperCase()}</b> — ${s.city} (${s.temperature ?? "--"}°C)`;
                        alertList.appendChild(alert);
                    }

                    // --- MAP MARKERS ---
                    if (s.lat && s.lng) {
                        let color =
                          st === "critical" ? "#ff4d4d" :
                          st === "warning" ? "#ffcc33" : "#0b5";

                        if (!markers[s.id]) {
                            markers[s.id] = L.circleMarker(
                                [s.lat, s.lng],
                                {
                                    radius: 8,
                                    fillColor: color,
                                    color: "#000",
                                    weight: 1,
                                    fillOpacity: 0.8
                                }
                            ).addTo(map);
                        }

                        markers[s.id].setStyle({ fillColor: color });
                        markers[s.id].bindPopup(
                          `<b>${s.name}</b><br>${s.city}<br>` +
                          `Temp: ${s.temperature ?? "--"}°C<br>` +
                          `Humidity: ${humTxt}<br>` +
                          `Wind: ${windTxt}<br>` +
                          `AQI (US): ${aqiTxt} (${aqiLabel(s.aqi_us)})<br>` +
                          `Fire Risk: ${s.fire_risk || "Unknown"}`
                        );
                    }
                });
            });
        }

        // poll every 15 seconds (less spammy, still "live")
        setInterval(updateUI, 15000);
        updateUI();
    </script>

</body>
</html>
"""

# ------------------------------
# FLASK ROUTES
# ------------------------------
@app.route("/")
def dashboard():
    return render_template_string(DASHBOARD_HTML)


@app.route("/api/temperature", methods=["POST"])
def receive_temp():
    """IoT sensors push here. This will mainly be your Oakville devices."""
    data = request.get_json(force=True)
    sid = data.get("sensor_id")
    temp = data.get("temperature")
    loc = data.get("location", "Unknown")

    if sid in sensors:
        s = sensors[sid]
    else:
        sensors[sid] = {
            "id": sid,
            "name": sid,
            "city": loc,
            "lat": None,
            "lng": None,
            "temperature": None,
            "humidity": None,
            "wind_speed": None,
            "uv_index": None,
            "pm2_5": None,
            "pm10": None,
            "aqi_us": None,
            "fire_risk": None,
            "last_update": None,
        }
        s = sensors[sid]

    s["temperature"] = temp
    s["city"] = loc
    s["last_update"] = datetime.utcnow().isoformat()

    print(f"[IoT] {sid} @ {loc}: {temp}°C")
    return jsonify({"success": True})


@app.route("/api/temperature", methods=["GET"])
def get_temps():
    global last_refresh
    now = datetime.utcnow()

    # refresh external APIs at most every 5 minutes
    if last_refresh is None or (now - last_refresh).total_seconds() > 300:
        refresh_live_data()
        last_refresh = now

    return jsonify({"sensors": list(sensors.values())})


# ------------------------------
# RUN
# ------------------------------
if __name__ == "__main__":
    print("Dashboard running at http://0.0.0.0:5000")
    app.run(host="0.0.0.0",port=5000, debug=True)
