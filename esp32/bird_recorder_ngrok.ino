/*
 * ESP32-WROOM-32D Bird Audio Recorder - Ngrok HTTPS Edition v4.0
 * Optimized for ESP32 WITHOUT PSRAM (uses streaming upload)
 * 
 * Hardware: ESP32-WROOM-32D, INMP441, RTC DS3231, SD Card
 */

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <driver/i2s.h>
#include <SPI.h>
#include <SD.h>
#include <Wire.h>
#include "RTClib.h"
#include <time.h>

// --- USER CONFIGURATION ---
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

// Ngrok URL - MUST be your active ngrok URL
const char* ngrokHost = "calfless-heliotypically-darrel.ngrok-free.dev";
const char* uploadPath = "/upload";

// --- LOCATION ---
const float FIXED_LAT = 20.9931;
const float FIXED_LON = 105.9579;

// --- RECORDING SETTINGS ---
#define RECORD_TIME_SEC 10
#define SAMPLE_RATE     48000
#define DMA_BUF_LEN     1024

// --- PIN DEFINITIONS ---
#define I2S_WS    15
#define I2S_SD    32
#define I2S_SCK   14
#define I2S_PORT  I2S_NUM_0
#define SD_CS_PIN 5

// --- GLOBALS ---
RTC_DS3231 rtc;

struct wav_header_t {
  char chunkID[4]; uint32_t chunkSize; char format[4];
  char subchunk1ID[4]; uint32_t subchunk1Size; uint16_t audioFormat;
  uint16_t numChannels; uint32_t sampleRate; uint32_t byteRate;
  uint16_t blockAlign; uint16_t bitsPerSample;
  char subchunk2ID[4]; uint32_t subchunk2Size;
};

void i2s_install();
void record_audio(const char* filename);
bool streamingUpload(String filename, float lat, float lon, String recTime);
void syncTimeVN();

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n====================================");
  Serial.println("🦅 BIO-RECORDER v4.0 (WROOM-32D)");
  Serial.println("====================================\n");
  
  // Check available memory
  Serial.printf("📊 Free heap: %d bytes\n", ESP.getFreeHeap());
  
  Wire.begin(21, 22);
  delay(100);
  
  if (!rtc.begin()) {
    Serial.println("❌ RTC not found!");
  } else {
    Serial.println("✅ RTC OK");
  }
  
  Serial.print("📁 SD Card...");
  if (!SD.begin(SD_CS_PIN)) {
    Serial.println(" ❌ FAILED!");
    while (1) delay(1000);
  }
  Serial.printf(" ✅ %lluMB\n", SD.cardSize() / (1024 * 1024));
  
  i2s_install();
  
  Serial.printf("📡 WiFi: %s", ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 40) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf(" ✅ %s\n", WiFi.localIP().toString().c_str());
    syncTimeVN();
  } else {
    Serial.println(" ❌ Failed!");
  }
  
  Serial.printf("📊 Free heap after init: %d bytes\n", ESP.getFreeHeap());
  Serial.println("\n🎤 Ready!\n");
}

void loop() {
  Serial.println("\n=== NEW RECORDING ===");
  Serial.printf("📊 Free heap: %d bytes\n", ESP.getFreeHeap());
  
  DateTime now = rtc.now();
  
  char tsBuf[25];
  sprintf(tsBuf, "%04d-%02d-%02d %02d:%02d:%02d",
          now.year(), now.month(), now.day(),
          now.hour(), now.minute(), now.second());
  String timestampISO = String(tsBuf);
  
  char filenameBuf[30];
  sprintf(filenameBuf, "/%04d%02d%02d_%02d%02d%02d.wav",
          now.year(), now.month(), now.day(),
          now.hour(), now.minute(), now.second());
  String currentFilename = String(filenameBuf);
  
  Serial.printf("📍 %.4f, %.4f\n", FIXED_LAT, FIXED_LON);
  Serial.printf("⏰ %s\n", timestampISO.c_str());
  Serial.printf("📄 %s\n", currentFilename.c_str());
  
  Serial.printf("🎤 Recording %ds...\n", RECORD_TIME_SEC);
  record_audio(currentFilename.c_str());
  
  if (WiFi.status() == WL_CONNECTED) {
    if (!streamingUpload(currentFilename, FIXED_LAT, FIXED_LON, timestampISO)) {
      Serial.println("⚠️ Upload failed, file saved locally");
    }
  } else {
    Serial.println("⚠️ No WiFi");
    WiFi.reconnect();
  }
  
  Serial.println("\n💤 Sleeping 60s...");
  delay(60000);
}

// Streaming upload - uses minimal RAM by reading file in small chunks
bool streamingUpload(String filename, float lat, float lon, String recTime) {
  Serial.println("📤 Starting streaming upload...");
  
  File file = SD.open(filename, FILE_READ);
  if (!file) {
    Serial.println("❌ Can't open file");
    return false;
  }
  
  size_t fileSize = file.size();
  Serial.printf("   File: %d bytes\n", fileSize);
  Serial.printf("   Host: %s\n", ngrokHost);
  
  // Create secure client
  WiFiClientSecure client;
  client.setInsecure(); // Skip cert verification for ngrok
  
  Serial.print("   Connecting (HTTPS)... ");
  
  // Try connection with explicit timeout
  unsigned long connectStart = millis();
  bool connected = false;
  
  // Attempt connection
  connected = client.connect(ngrokHost, 443);
  
  if (!connected) {
    Serial.println("❌ FAILED");
    Serial.printf("   Connection took: %lums\n", millis() - connectStart);
    Serial.println("   Possible causes:");
    Serial.println("   1. Ngrok tunnel not running");
    Serial.println("   2. URL expired or wrong");
    Serial.println("   3. Network/firewall issue");
    file.close();
    return false;
  }
  
  Serial.printf("✅ (%lums)\n", millis() - connectStart);
  
  // Build multipart form data
  String boundary = "----ESP32" + String(millis());
  
  // Pre-build form parts
  String formStart = "";
  formStart += "--" + boundary + "\r\n";
  formStart += "Content-Disposition: form-data; name=\"lat\"\r\n\r\n";
  formStart += String(lat, 6) + "\r\n";
  formStart += "--" + boundary + "\r\n";
  formStart += "Content-Disposition: form-data; name=\"lon\"\r\n\r\n";
  formStart += String(lon, 6) + "\r\n";
  formStart += "--" + boundary + "\r\n";
  formStart += "Content-Disposition: form-data; name=\"recorded_at\"\r\n\r\n";
  formStart += recTime + "\r\n";
  formStart += "--" + boundary + "\r\n";
  formStart += "Content-Disposition: form-data; name=\"file\"; filename=\"audio.wav\"\r\n";
  formStart += "Content-Type: audio/wav\r\n\r\n";
  
  String formEnd = "\r\n--" + boundary + "--\r\n";
  
  size_t contentLength = formStart.length() + fileSize + formEnd.length();
  
  // Send HTTP headers
  client.print("POST ");
  client.print(uploadPath);
  client.println(" HTTP/1.1");
  client.print("Host: ");
  client.println(ngrokHost);
  client.print("Content-Type: multipart/form-data; boundary=");
  client.println(boundary);
  client.print("Content-Length: ");
  client.println(contentLength);
  client.println("Connection: close");
  client.println("ngrok-skip-browser-warning: true");
  client.println(); // End headers
  
  // Send form start (metadata)
  client.print(formStart);
  
  // Stream file in small chunks (4KB buffer - safe for WROOM-32D)
  Serial.print("   Streaming file");
  const size_t CHUNK_SIZE = 4096;
  uint8_t* chunk = (uint8_t*)malloc(CHUNK_SIZE);
  
  if (!chunk) {
    Serial.println("\n❌ Can't allocate chunk buffer");
    file.close();
    client.stop();
    return false;
  }
  
  size_t totalSent = 0;
  int dots = 0;
  
  while (file.available()) {
    size_t bytesRead = file.read(chunk, CHUNK_SIZE);
    size_t bytesSent = client.write(chunk, bytesRead);
    
    if (bytesSent != bytesRead) {
      Serial.println("\n❌ Send error");
      free(chunk);
      file.close();
      client.stop();
      return false;
    }
    
    totalSent += bytesSent;
    
    // Progress dots (every ~100KB)
    if (totalSent / 100000 > dots) {
      Serial.print(".");
      dots = totalSent / 100000;
    }
    
    yield(); // Allow WiFi stack to process
  }
  
  free(chunk);
  file.close();
  Serial.printf(" ✅ %d bytes\n", totalSent);
  
  // Send form end
  client.print(formEnd);
  client.flush();
  
  // Wait for response
  Serial.print("   Waiting for response... ");
  unsigned long timeout = millis();
  
  while (!client.available() && millis() - timeout < 30000) {
    delay(100);
  }
  
  if (!client.available()) {
    Serial.println("❌ Timeout");
    client.stop();
    return false;
  }
  
  // Read response
  String statusLine = client.readStringUntil('\n');
  Serial.println(statusLine);
  
  bool success = (statusLine.indexOf("200") > 0 || statusLine.indexOf("201") > 0);
  
  // Skip headers to get body
  while (client.available()) {
    String line = client.readStringUntil('\n');
    if (line.length() <= 1) break;
  }
  
  // Read response body
  String body = "";
  while (client.available()) {
    body += (char)client.read();
  }
  
  if (body.length() > 0) {
    Serial.printf("   Body: %s\n", body.c_str());
  }
  
  client.stop();
  
  if (success) {
    Serial.println("🎉 UPLOAD SUCCESS!");
    return true;
  } else {
    Serial.println("❌ Server returned error");
    return false;
  }
}

void syncTimeVN() {
  Serial.print("⏰ NTP...");
  configTime(7 * 3600, 0, "pool.ntp.org", "time.nist.gov");
  
  struct tm timeinfo;
  int attempts = 0;
  while (!getLocalTime(&timeinfo) && attempts < 10) {
    delay(500);
    attempts++;
  }
  
  if (attempts < 10) {
    rtc.adjust(DateTime(timeinfo.tm_year + 1900, timeinfo.tm_mon + 1, 
                        timeinfo.tm_mday, timeinfo.tm_hour, 
                        timeinfo.tm_min, timeinfo.tm_sec));
    Serial.println(" ✅");
  } else {
    Serial.println(" ⚠️");
  }
}

void i2s_install() {
  Serial.print("🎤 I2S...");
  
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8,
    .dma_buf_len = DMA_BUF_LEN,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
  };
  
  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_SD
  };
  
  i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_PORT, &pin_config);
  i2s_zero_dma_buffer(I2S_PORT);
  delay(100);
  
  Serial.println(" ✅");
}

void record_audio(const char* filename) {
  if (SD.exists(filename)) SD.remove(filename);
  
  File file = SD.open(filename, FILE_WRITE);
  if (!file) {
    Serial.println("❌ Can't create file!");
    return;
  }
  
  wav_header_t header;
  memset(&header, 0, sizeof(header));
  file.write((uint8_t*)&header, sizeof(header));
  
  uint32_t totalBytesTarget = (uint32_t)SAMPLE_RATE * RECORD_TIME_SEC * 2;
  uint32_t bytesWritten = 0;
  
  int32_t i2s_buf[DMA_BUF_LEN];
  size_t bytes_read = 0;
  
  Serial.print("   ");
  int lastSecond = -1;
  unsigned long startTime = millis();
  
  while (bytesWritten < totalBytesTarget) {
    i2s_read(I2S_PORT, &i2s_buf, sizeof(i2s_buf), &bytes_read, portMAX_DELAY);
    if (bytes_read == 0) continue;
    
    int samples = bytes_read / 4;
    int16_t wav_buf[samples];
    
    for (int i = 0; i < samples; i++) {
      wav_buf[i] = (int16_t)(i2s_buf[i] >> 14);
    }
    
    size_t bytesToWrite = samples * 2;
    if (bytesWritten + bytesToWrite > totalBytesTarget) {
      bytesToWrite = totalBytesTarget - bytesWritten;
    }
    
    file.write((uint8_t*)wav_buf, bytesToWrite);
    bytesWritten += bytesToWrite;
    
    int currentSecond = (millis() - startTime) / 1000;
    if (currentSecond > lastSecond && currentSecond <= RECORD_TIME_SEC) {
      Serial.printf("%d..", currentSecond);
      lastSecond = currentSecond;
    }
  }
  
  Serial.printf(" ✅ %d bytes\n", bytesWritten);
  
  memcpy(header.chunkID, "RIFF", 4);
  header.chunkSize = bytesWritten + 36;
  memcpy(header.format, "WAVE", 4);
  memcpy(header.subchunk1ID, "fmt ", 4);
  header.subchunk1Size = 16;
  header.audioFormat = 1;
  header.numChannels = 1;
  header.sampleRate = SAMPLE_RATE;
  header.byteRate = SAMPLE_RATE * 2;
  header.blockAlign = 2;
  header.bitsPerSample = 16;
  memcpy(header.subchunk2ID, "data", 4);
  header.subchunk2Size = bytesWritten;
  
  file.seek(0);
  file.write((uint8_t*)&header, sizeof(header));
  file.close();
}
