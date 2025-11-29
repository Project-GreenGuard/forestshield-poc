#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
// DHT11 Sensor Configuration
#define DHTPIN 15         // GPIO pin connected to DHT11 DATA pin (D15)
#define DHTTYPE DHT11     // DHT11 sensor type
DHT dht(DHTPIN, DHTTYPE);
// WiFi credentials - REPLACE WITH YOUR NETWORK INFO
const char* ssid = "SSID";
const char* password = "PASSWORD";
// Server URL - Your dashboard IP
const char* serverURL = "http://192.168.2.164:5000/api/temperature";
// Sensor Information - CUSTOMIZE THIS FOR EACH SENSOR
const char* sensorID = "sensor01";
const char* sensorLocation = "Sheridan Forest Oakville";
// Timing
unsigned long lastSendTime = 0;
const unsigned long sendInterval = 10000; // 10 seconds
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\nIoT Device Starting...");
  
  // Initialize DHT sensor
  dht.begin();
  Serial.println("DHT11 sensor initialized");
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nWiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.print("WiFi Signal: ");
  Serial.print(WiFi.RSSI());
  Serial.println(" dBm");
  Serial.print("Sending to: ");
  Serial.println(serverURL);
  Serial.print("Sensor ID: ");
  Serial.println(sensorID);
  Serial.print("Location: ");
  Serial.println(sensorLocation);
  Serial.println("Reading temperature every 10 seconds...\n");
}
void loop() {
  unsigned long currentTime = millis();
  
  // Send temperature every 10 seconds
  if (currentTime - lastSendTime >= sendInterval) {
    lastSendTime = currentTime;
    sendTemperature();
  }
}
void sendTemperature() {
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected! Reconnecting...");
    WiFi.reconnect();
    return;
  }
  
  // Read temperature from DHT11
  float temp = dht.readTemperature();
  
  // Check if reading failed
  if (isnan(temp)) {
    Serial.println("✗ Failed to read from DHT11 sensor!");
    return;
  }
  
  // Round to 1 decimal place
  temp = round(temp * 10.0) / 10.0;
  
  Serial.print("[");
  Serial.print(sensorID);
  Serial.print("] ");
  Serial.print(temp, 1);
  Serial.print("°C  ");
  
  HTTPClient http;
  http.begin(serverURL);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(5000); // 5 second timeout
  
  // Create JSON payload with sensor info
  StaticJsonDocument<300> doc;
  doc["temperature"] = temp;
  doc["sensor_id"] = sensorID;
  doc["location"] = sensorLocation;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  // Send POST request
  int httpResponseCode = http.POST(jsonString);
  
  if (httpResponseCode == 200) {
    Serial.println("✓ Sent successfully");
  } else if (httpResponseCode == -1) {
    Serial.println("✗ Connection failed");
  } else {
    Serial.print("✗ Error: ");
    Serial.println(httpResponseCode);
  }
  
  http.end();
}