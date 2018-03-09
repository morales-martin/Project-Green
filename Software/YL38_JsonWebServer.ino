// Now using ESP8266.....
// Sample Arduino Json Web Server
// Created by Benoit Blanchon.
// Heavily inspired by "Web Server" from David A. Mellis and Tom Igoe


#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
//////////////////////////////
// DHT21 / AMS2301 is at GPIO2
//////////////////////////////

// needed to avoid link error on ram check
extern "C" 
{
#include "user_interface.h"
}
ADC_MODE(ADC_VCC);

WiFiServer server(80);
WiFiClient client;
const char* ssid = "Restricted Wireless";
const char* password = "B=SP7e&aNK";
double moistLevel = 0.0;
double analogValue = 0.0;

bool readRequest(WiFiClient& client) {
  bool currentLineIsBlank = true;
  while (client.connected()) {
    if (client.available()) {
      char c = client.read();
      if (c == '\n' && currentLineIsBlank) {
        return true;
      } else if (c == '\n') {
        currentLineIsBlank = true;
      } else if (c != '\r') {
        currentLineIsBlank = false;
      }
    }
  }
  return false;
}

JsonObject& prepareResponse(JsonBuffer& jsonBuffer) {
  JsonObject& root = jsonBuffer.createObject();
  JsonArray& moistureValues = root.createNestedArray("moisture");
    moistureValues.add(moistLevel);
  return root;
}

void writeResponse(WiFiClient& client, JsonObject& json) {
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: application/json");
  client.println("Connection: close");
  client.println();

  json.prettyPrintTo(client);
}

void setup() {
  Serial.begin(115200);
  delay(2000);
  
  // inital connect
  WiFi.mode(WIFI_STA);
  delay(1000);
  
  // Connect to WiFi network
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  WiFi.begin(ssid,password);  
  while (WiFi.status() != WL_CONNECTED) 
  {
    delay(500);
  }
  Serial.println("");
  Serial.println("WiFi connected");
 
  server.begin();

    // Start the server
  server.begin();
  Serial.println("Server started");
  
  // Print the IP address
  Serial.println(WiFi.localIP());
}
void loop() {
  
  WiFiClient client = server.available();
  if (client) {
    bool success = readRequest(client);
    if (success) {
    
    analogValue = analogRead(A0);
    moistLevel = (analogValue * 100) / 400;
    moistLevel = 100 - moistLevel;
   
    delay(1000);
    Serial.print("Analog Value: ");
    Serial.print(analogValue);
    Serial.println();

    Serial.print("Scalable Value: ");
    Serial.print(moistLevel);
    Serial.println();
    
   delay(500);
      StaticJsonBuffer<500> jsonBuffer;
      JsonObject& json = prepareResponse(jsonBuffer);
      writeResponse(client, json);
    }
    delay(1);
    client.stop();
  }
}
