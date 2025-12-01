from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

latest_data = {
    'temperature': None,
    'sensor_id': None,
    'location': None
}

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Disaster Dashboard</title>

    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />

    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #000;
            color: white;
            font-family: Arial, sans-serif;
            display: flex;
            height: 100vh;
        }

        /* LEFT PANEL */
        .info-panel {
            width: 35%;
            background-color: #111;
            padding: 40px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            border-right: 2px solid #333;
            display: flex;
            margin-top: 70px;
        }

        .sensor-info {
            font-size: 28px;
            color: #ccc;
            margin-bottom: 15px;
        }

        .temperature {
            font-size: 95px;
            font-weight: bold;
            color: #00ff00;
        }

        .temperature.high {
            color: #ff0000;
        }

        .location {
            font-size: 35px;
            color: #aaa;
            margin-top: 15px;
        }

        .fire-warning {
            display: none;
            background-color: #ff0000;
            color: white;
            padding: 20px 40px;
            font-size: 40px;
            font-weight: bold;
            border-radius: 10px;
            margin-top: 30px;
            animation: blink 1s infinite;
        }

        .fire-warning.show {
            display: block;
        }

        @keyframes blink {
            0%, 50%, 100% { opacity: 1; }
            25%, 75% { opacity: 0.3; }
        }

        /* MAP PANEL */
        #map {
            width: 65%;
            height: 100%;
        }
        /* TOP BAR */
        .top-bar {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 70px;             /* thin bar */
            background-color: #0d0d0d;
            display: flex;
            align-items: center;
            padding: 0 20px;
            border-bottom: 2px solid #222;
            z-index: 1000;
        }

        .top-logo {
            height: 55px;             /* fits inside bar */
            width: auto;
            object-fit: contain;
            margin-right: 15px;
        }

        .top-title {
            font-size: 24px;
            font-weight: bold;
            color: #00ff00;
        }



    </style>

    <!-- Leaflet JS -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
</head>

<body>

<div class="top-bar">
    <img src="/static/prologo.png" class="top-logo">
    <span class="top-title">Project GreenGuard</span>
</div>

    <!-- LEFT INFO PANEL -->
    <div class="info-panel">
        <div class="sensor-info" id="sensor">Sensor: --</div>
        <div class="temperature" id="temp">--°C</div>
        <div class="location" id="location">Location: --</div>
        <div class="fire-warning" id="fire-warning">🔥 FIRE WARNING – HIGH TEMP 🔥</div>
    </div>

    <!-- RIGHT MAP -->
    <div id="map"></div>

    <script>
        // Initialize map centered on GTA (Toronto)
        var map = L.map('map').setView([43.6532, -79.3832], 10);

        // Load map tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18,
        }).addTo(map);

        // Example 10 locations (GTA)
        var sampleLocations = [
            { name: "Toronto", coords: [43.6532, -79.3832] },
            { name: "Mississauga", coords: [43.5890, -79.6441] },
            { name: "Brampton", coords: [43.7315, -79.7624] },
            { name: "Markham", coords: [43.8561, -79.3370] },
            { name: "Vaughan", coords: [43.8372, -79.5083] },
            { name: "Richmond Hill", coords: [43.8828, -79.4403] },
            { name: "Oakville", coords: [43.4675, -79.6877] },
            { name: "Scarborough", coords: [43.7764, -79.2318] },
            { name: "Etobicoke", coords: [43.6205, -79.5132] },
            { name: "Pickering", coords: [43.8373, -79.0892] }
        ];

        // Add markers to the map
        sampleLocations.forEach(loc => {
            L.marker(loc.coords).addTo(map)
                .bindPopup("<b>" + loc.name + "</b>");
        });

        // Fetch sensor data every 2 seconds
        function updateTemp() {
            fetch('/api/temperature')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('temp').textContent =
                        data.temperature !== null ? data.temperature + '°C' : '--°C';

                    document.getElementById('sensor').textContent =
                        data.sensor_id !== null ? "Sensor: " + data.sensor_id : "Sensor: --";

                    document.getElementById('location').textContent =
                        data.location !== null ? "Location: " + data.location : "Location: --";

                    // Fire warning logic
                    const tempEl = document.getElementById('temp');
                    const fireEl = document.getElementById('fire-warning');

                    if (data.temperature > 35) {
                        tempEl.classList.add('high');
                        fireEl.classList.add('show');
                    } else {
                        tempEl.classList.remove('high');
                        fireEl.classList.remove('show');
                    }
                });
        }

        setInterval(updateTemp, 2000);
        updateTemp();
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/temperature', methods=['POST'])
def receive_temperature():
    global latest_data
    data = request.get_json()
    latest_data['temperature'] = data.get('temperature')
    latest_data['sensor_id'] = data.get('sensor_id', 'Unknown')
    latest_data['location'] = data.get('location', 'Unknown')
    
    print(f"Received from {latest_data['sensor_id']} ({latest_data['location']}): {latest_data['temperature']}°C")
    return jsonify({'success': True})

@app.route('/api/temperature', methods=['GET'])
def get_temperature():
    return jsonify(latest_data)

if __name__ == '__main__':
    print("Dashboard running at http://192.168.2.23:5000")
    app.run(host='192.168.2.23', port=5000, debug=True)
