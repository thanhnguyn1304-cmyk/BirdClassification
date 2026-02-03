/*
 * ESP32 Bird Audio Recorder - FINAL PRODUCTION
 * 
 * Hardware: ESP32-WROOM-32D, INMP441, RTC DS3231, SD Card
 * Network: Uses Mobile Hotspot for Direct HTTP Upload (Local IP)
 */

#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h> // Keep for legacy, though not used for local HTTP
#include <driver/i2s.h>
#include <SPI.h>
#include <SD.h>
#include <Wire.h>
#include "RTClib.h"
#include <time.h>

// --- USER CONFIGURATION ---
const char* ssid = "thanhf";           // Mobile Hotspot
const char* password = "thanh1304";    // Hotspot Password

const char* uploadUrl = "http://10.234.0.69:8000/upload";

// --- LOCATION ---
// Set to 0.0 to send "None" to server
const float FIXED_LAT = 0.0;
const float FIXED_LON = 0.0;

// --- SETTINGS ---
#define RECORD_TIME_SEC 5
#define SAMPLE_RATE     32000
#define DMA_BUF_LEN     1024

// --- PINS ---
#define I2S_WS    15
#define I2S_SD    32
#define I2S_SCK   14
#define I2S_PORT  I2S_NUM_0
#define SD_CS_PIN 5

RTC_DS3231 rtc;

struct wav_header_t {
  char chunkID[4]; uint32_t chunkSize; char format[4];
  char subchunk1ID[4]; uint32_t subchunk1Size; uint16_t audioFormat;
  uint16_t numChannels; uint32_t sampleRate; uint32_t byteRate;
  uint16_t blockAlign; uint16_t bitsPerSample;
  char subchunk2ID[4]; uint32_t subchunk2Size;
};

// Prototypes
void i2s_install();
void record_audio(const char* filename);
bool streamingUpload(String filename, float lat, float lon, String recTime);
void syncTimeVN();

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n--- BIRD RECORDER: FINAL (Local IP) ---");
  
  Wire.begin(21, 22);
  if (!rtc.begin()) Serial.println("❌ RTC Missing");
  
  if (!SD.begin(SD_CS_PIN)) {
    Serial.println("❌ SD Mount Failed");
    while(1) delay(100);
  }
  
  Serial.printf("Connecting to %s", ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500); Serial.print(".");
  }
  Serial.println("\n✅ WiFi Connected");
  Serial.print("ESP32 IP: "); Serial.println(WiFi.localIP());
  
  syncTimeVN();
}

void loop() {
  // Re-install I2S driver for the new cycle (since we uninstalled it for upload)
  i2s_install();
  
  Serial.println("\n🔴 START RECORDING 🔴");
  
  DateTime now = rtc.now();
  char tsBuf[25];
  sprintf(tsBuf, "%04d-%02d-%02d %02d:%02d:%02d", 
          now.year(), now.month(), now.day(), now.hour(), now.minute(), now.second());
  String timestampISO = String(tsBuf);
  
  char fnBuf[20];
  // Short filename (8.3 format) to be safe: HHMMSS.wav
  sprintf(fnBuf, "/%02d%02d%02d.wav", 
          now.hour(), now.minute(), now.second());
  String filename = String(fnBuf);
  
  Serial.printf("File: %s\n", filename.c_str());
  record_audio(filename.c_str());
  
  // CRITICAL: Uninstall I2S to free up ~32KB RAM for Buffer
  // WROOM-32D runs out of RAM otherwise
  i2s_driver_uninstall(I2S_PORT);
  Serial.println("I2S Driver Uninstalled (RAM Freed)");
  
  if (WiFi.status() == WL_CONNECTED) {
    bool success = streamingUpload(filename, FIXED_LAT, FIXED_LON, timestampISO);
    if(success) {
       SD.remove(filename);
       Serial.println("🗑️ File deleted from SD");
    }
  } else {
    Serial.println("⚠️ No WiFi. Upload skipped.");
    WiFi.reconnect();
  }
  
  Serial.println("Sleeping 60s...");
  delay(60000);
}

// Reliable HTTPClient Upload (Raw Body + Query Params)
bool streamingUpload(String filename, float lat, float lon, String recTime) {
  Serial.println("📤 Uploading via Local HTTP (Stream)...");
  
  File file = SD.open(filename, FILE_READ);
  if (!file) { Serial.println("❌ File error"); return false; }
  size_t fileSize = file.size();

  // Use Standard WiFiClient (NO SSL overhead)
  WiFiClient client;
  client.setTimeout(600000); // 10 minutes timeout

  HTTPClient http;
  
  // URL Encode Timestamp (Simple version)
  recTime.replace(" ", "%20");
  recTime.replace(":", "%3A");
  
  // Construct URL with Query Params
  String url = String(uploadUrl) + "?recorded_at=" + recTime;
  
  // Only add location if set (User requested "None" capability)
  if (lat != 0.0 || lon != 0.0) {
     url += "&lat=" + String(lat, 6) + "&lon=" + String(lon, 6);
  }
               
  Serial.print("Target URL: "); Serial.println(url);

  // HTTPClient auto-manages the connection via WiFiClient
  if (!http.begin(client, url)) {
    Serial.println("❌ HTTP Begin Failed");
    file.close();
    return false;
  }

  http.addHeader("Content-Type", "audio/wav"); // Raw Audio Body
  
  // SEND REQUEST with STREAM
  // This function automatically streams from SD to Network
  // managing the buffer internally.
  int httpCode = http.sendRequest("POST", &file, fileSize);
  
  if (httpCode > 0) {
    Serial.printf("✅ HTTP Code: %d\n", httpCode);
    if (httpCode == 200 || httpCode == 201) {
      String payload = http.getString();
      Serial.println(payload);
      file.close();
      http.end();
      return true;
    }
  } else {
    Serial.printf("❌ POST Failed: %s\n", http.errorToString(httpCode).c_str());
  }

  file.close();
  http.end();
  return false;
}

void i2s_install() {
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8, .dma_buf_len = DMA_BUF_LEN, .use_apll = false 
  };
  i2s_pin_config_t pin_config = { .bck_io_num=I2S_SCK, .ws_io_num=I2S_WS, .data_out_num=-1, .data_in_num=I2S_SD };
  i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_PORT, &pin_config);
  i2s_zero_dma_buffer(I2S_PORT);
}

void record_audio(const char* filename) {
  Serial.printf("Recording to %s...\n", filename);
  if (SD.exists(filename)) SD.remove(filename);
  
  File file = SD.open(filename, FILE_WRITE);
  if (!file) {
    Serial.println("❌ FAILED to create file!");
    return;
  }
  
  wav_header_t header; memset(&header, 0, sizeof(header));
  file.write((uint8_t*)&header, sizeof(header));
  
  uint32_t totalBytes = SAMPLE_RATE * RECORD_TIME_SEC * 2;
  uint32_t written = 0;
  int32_t i2s_buf[DMA_BUF_LEN];
  size_t bytes_read;
  
  while (written < totalBytes) {
    i2s_read(I2S_PORT, &i2s_buf, sizeof(i2s_buf), &bytes_read, portMAX_DELAY);
    if(bytes_read==0) continue;
    int samples = bytes_read/4;
    int16_t wav_buf[samples];
    for(int i=0; i<samples; i++) wav_buf[i] = i2s_buf[i] >> 14; 
    file.write((uint8_t*)wav_buf, samples*2);
    written += samples*2;
  }
  
  memcpy(header.chunkID,"RIFF",4); header.chunkSize = written+36; memcpy(header.format,"WAVE",4);
  memcpy(header.subchunk1ID,"fmt ",4); header.subchunk1Size = 16; header.audioFormat = 1; 
  header.numChannels = 1; header.sampleRate = SAMPLE_RATE; header.byteRate = SAMPLE_RATE*2;
  header.blockAlign = 2; header.bitsPerSample = 16; memcpy(header.subchunk2ID,"data",4);
  header.subchunk2Size = written;
  
  file.seek(0); file.write((uint8_t*)&header, sizeof(header)); file.close();
}

void syncTimeVN() {
  configTime(7*3600,0, "pool.ntp.org");
  struct tm timeinfo;
  if(getLocalTime(&timeinfo)){
    rtc.adjust(DateTime(timeinfo.tm_year+1900, timeinfo.tm_mon+1, timeinfo.tm_mday, 
                        timeinfo.tm_hour, timeinfo.tm_min, timeinfo.tm_sec));
    Serial.println("Time Synced");
  }
}
