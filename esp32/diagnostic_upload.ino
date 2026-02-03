/*
 * ESP32 Hyper-Critical Diagnostic Tool
 * Purpose: Isolate fail point (Network vs SD vs RAM)
 * Method: Generates synthetic data (no SD) to test pure upload stability.
 */

#include <WiFi.h>
#include <WiFiClientSecure.h>

// --- CONFIG ---
const char* ssid = "thanhf";
const char* password = "thanh1304";
const char* host = "calfless-heliotypically-darrel.ngrok-free.dev";
const char* path = "/upload";

// Settings
const int TEST_FILE_SIZE = 320000; // 320KB (Approx 5s @ 32kHz)

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n--- DIAGNOSTIC MODE ---");
  Serial.printf("Target File Size: %d bytes\n", TEST_FILE_SIZE);
  
  WiFi.begin(ssid, password);
  Serial.print("WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500); Serial.print(".");
  }
  Serial.println(" Connected!");
  
  testSyntheticUpload();
}

void loop() {}

void testSyntheticUpload() {
  WiFiClientSecure client;
  client.setInsecure();
  client.setTimeout(60000); // 60s
  
  Serial.print("Connecting to Ngrok...");
  if (!client.connect(host, 443)) {
    Serial.println("❌ Connect Failed!");
    return;
  }
  Serial.println("✅ Connected");

  String boundary = "----DiagBoundary";
  String head = "--" + boundary + "\r\n" +
                "Content-Disposition: form-data; name=\"recorded_at\"\r\n\r\n2025-01-01 12:00:00\r\n" +
                "--" + boundary + "\r\n" +
                "Content-Disposition: form-data; name=\"file\"; filename=\"diag.wav\"\r\n" +
                "Content-Type: audio/wav\r\n\r\n";
  String tail = "\r\n--" + boundary + "--\r\n";
  
  size_t totalLen = head.length() + TEST_FILE_SIZE + tail.length();
  
  // Headers
  client.println("POST " + String(path) + " HTTP/1.1");
  client.println("Host: " + String(host));
  client.println("Content-Type: multipart/form-data; boundary=" + boundary);
  client.println("Content-Length: " + String(totalLen));
  client.println("ngrok-skip-browser-warning: true");
  client.println("Connection: close");
  client.println();
  
  client.print(head);
  
  // Synthetic Data Stream
  uint8_t chunk[2048];
  memset(chunk, 0xAA, 2048); // Fill with dummy data
  
  int remaining = TEST_FILE_SIZE;
  int sent = 0;
  unsigned long startTime = millis();
  
  while (remaining > 0) {
    int toSend = (remaining > 2048) ? 2048 : remaining;
    
    // Check connection before writing
    if (!client.connected()) {
      Serial.println("\n❌ DISCONNECTED during upload!");
      return;
    }
    
    size_t written = client.write(chunk, toSend);
    if (written == 0) {
      Serial.println("\n❌ Write Failed (Stall)");
      return;
    }
    
    remaining -= written;
    sent += written;
    
    // Progress Bar
    if (sent % 32768 == 0) Serial.print("#");
    
    delay(10); // Stability Delay
  }
  
  client.print(tail);
  Serial.printf("\n✅ Uploaded %d bytes in %lu ms\n", sent, millis() - startTime);
  
  // Response
  while (client.connected() || client.available()) {
    if (client.available()) {
      String line = client.readStringUntil('\n');
      Serial.println(line);
      if (line.indexOf("200 OK") >= 0) {
        Serial.println("🎉 SERVER CONFIRMED SUCCESS!");
        return;
      }
    }
  }
}
