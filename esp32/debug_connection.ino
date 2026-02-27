/*
 * ESP32 Simple Upload Tester v2 (HTTPClient Version)
 * Uses HTTPClient library which handles TLS handshakes more reliably
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>

// --- CONFIG ---
const char* ssid = "thanhf";
const char* password = "thanh1304";
const char* url = "https://calfless-heliotypically-darrel.ngrok-free.dev/upload";

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n--- ESP32 UPLOAD TESTER v2 (HTTPClient) ---");
  
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500); Serial.print(".");
  }
  Serial.println("\nWiFi Connected! IP: " + WiFi.localIP().toString());
  
  testUpload();
}

void loop() {
  // Do nothing
}

void testUpload() {
  Serial.println("\n--- STARTING UPLOAD TEST ---");

  // 1. Setup Secure Client
  WiFiClientSecure client;
  client.setInsecure(); // Skip verification
  client.setTimeout(30000); // 30s timeout
  
  // 2. Setup HTTP Client
  HTTPClient http;
  
  Serial.print("Begin HTTP connection to: "); Serial.println(url);
  
  // This step handles DNS + TLS Handshake
  if (!http.begin(client, url)) {
    Serial.println("❌ FAILED at http.begin() - Likely SSL Handshake Error");
    return;
  }

  // 3. Prepare Dummy Data
  String boundary = "----ESP32TestBoundary";
  http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);
  http.addHeader("ngrok-skip-browser-warning", "true");
  
  String body = "--" + boundary + "\r\n";
  body += "Content-Disposition: form-data; name=\"lat\"\r\n\r\n20.0\r\n";
  body += "--" + boundary + "\r\n";
  body += "Content-Disposition: form-data; name=\"lon\"\r\n\r\n105.0\r\n";
  body += "--" + boundary + "\r\n";
  body += "Content-Disposition: form-data; name=\"recorded_at\"\r\n\r\n2025-01-01 12:00:00\r\n";
  body += "--" + boundary + "\r\n";
  body += "Content-Disposition: form-data; name=\"file\"; filename=\"test.wav\"\r\n";
  body += "Content-Type: audio/wav\r\n\r\n";
  body += "DUMMY_AUDIO_DATA"; // Tiny body
  body += "\r\n--" + boundary + "--\r\n";

  Serial.println("Sending POST Request...");
  int httpCode = http.POST(body);

  if (httpCode > 0) {
    Serial.printf("✅ HTTP CODE: %d\n", httpCode);
    String payload = http.getString();
    Serial.println("RESPONSE BODY:");
    Serial.println(payload);
  } else {
    Serial.printf("❌ POST FAILED. Error: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
}
