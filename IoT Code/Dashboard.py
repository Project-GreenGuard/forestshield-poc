from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type"]}})

latest_temp = None

# Sample wildfire data
wildfires = [
    {
        "id": 1,
        "name": "Jasper Ridge",
        "lat": 52.873,
        "lng": -118.082,
        "temperature": 42,
        "windSpeed": 22,
        "risk": "High"
    },
    {
        "id": 2,
        "name": "Banff Forest",
        "lat": 51.178,
        "lng": -115.571,
        "temperature": 34,
        "windSpeed": 14,
        "risk": "Moderate"
    }
]

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Temperature Dashboard</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: black;
            color: white;
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-size: 80px;
        }
    </style>
    <script>
        function updateTemp() {
            fetch('/api/temperature')
                .then(response => response.json())
                .then(data => {
                    if (data.temperature !== null) {
                        document.getElementById('temp').textContent = data.temperature + '°C';
                    }
                });
        }
        setInterval(updateTemp, 2000);
        updateTemp();
    </script>
</head>
<body>
    <div id="temp">--°C</div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/temperature', methods=['POST'])
def receive_temperature():
    global latest_temp
    data = request.get_json()
    latest_temp = data['temperature']
    print(f"Received: {latest_temp}°C")
    return jsonify({'success': True})

@app.route('/api/temperature', methods=['GET'])
def get_temperature():
    return jsonify({'temperature': latest_temp})

@app.route('/api/fires', methods=['GET'])
def get_fires():
    """Returns array of active wildfires"""
    return jsonify(wildfires)

@app.route('/api/summary', methods=['GET'])
def get_summary():
    """Returns computed statistics"""
    if not wildfires:
        return jsonify({
            'averageTemperature': 0,
            'highRiskCount': 0,
            'timestamp': datetime.now().isoformat()
        })
    
    temperatures = [fire['temperature'] for fire in wildfires]
    average_temp = sum(temperatures) / len(temperatures)
    high_risk_count = sum(1 for fire in wildfires if fire['risk'] == 'High')
    
    return jsonify({
        'averageTemperature': round(average_temp, 1),
        'highRiskCount': high_risk_count,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("Dashboard running at http://localhost:5001")
    app.run(host='0.0.0.0', port=5001)