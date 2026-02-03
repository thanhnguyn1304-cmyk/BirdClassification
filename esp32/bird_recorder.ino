/*
 * ESP32 Bird Audio Recorder & Uploader
 * 
 * Hardware Required:
 * - ESP32 DevKit
 * - INMP441 I2S Microphone (or similar)
 * - Optional: GPS Module (for location)
 * 
 * Wiring (INMP441):
 * - VDD  → 3.3V
 * - GND  → GND
 * - SD   → GPIO 32 (Data)
 * - WS   → GPIO 25 (Word Select / LRCK)
 * - SCK  → GPIO 33 (Clock)
 * - L/R  → GND (Left channel)
 * 
 * Libraries Required:
 * - WiFi.h (built-in)
 * - HTTPClient.h (built-in)
 * - driver/i2s.h (built-in)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <driver/i2s.h>
#include <time.h>

// ===== CONFIGURATION =====
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* SERVER_URL = "http://192.168.1.100:8000/upload";  // Change to your server IP

// Recording settings
const int SAMPLE_RATE = 16000;       // BirdNET expects 48kHz, but 16kHz works too
const int RECORD_SECONDS = 15;       // Recording duration (BirdNET analyzes 3-second chunks)
const int RECORD_INTERVAL_MS = 60000; // Time between recordings (1 minute)

// GPS Coordinates (set manually or use GPS module)
const float LATITUDE = 10.7769;      // Example: Ho Chi Minh City
const float LONGITUDE = 106.7009;

// I2S Microphone Pins (INMP441)
#define I2S_WS  25   // Word Select (LRCK)
#define I2S_SD  32   // Serial Data
#define I2S_SCK 33   // Serial Clock

// ===== GLOBALS =====
const int BUFFER_SIZE = SAMPLE_RATE * RECORD_SECONDS;
int16_t* audioBuffer = nullptr;
bool isRecording = false;

// ===== I2S SETUP =====
void setupI2S() {
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 8,
        .dma_buf_len = 1024,
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

    i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    i2s_set_pin(I2S_NUM_0, &pin_config);
    i2s_zero_dma_buffer(I2S_NUM_0);
    
    Serial.println("✅ I2S Microphone initialized");
}

// ===== WIFI SETUP =====
void setupWiFi() {
    Serial.print("📡 Connecting to WiFi");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n✅ WiFi Connected!");
        Serial.print("   IP: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("\n❌ WiFi Failed! Restarting...");
        ESP.restart();
    }
}

// ===== NTP TIME SYNC =====
void setupTime() {
    configTime(7 * 3600, 0, "pool.ntp.org");  // GMT+7 for Vietnam
    Serial.print("⏰ Syncing time");
    
    struct tm timeinfo;
    int attempts = 0;
    while (!getLocalTime(&timeinfo) && attempts < 10) {
        Serial.print(".");
        delay(500);
        attempts++;
    }
    
    if (attempts < 10) {
        Serial.println(" ✅ Time synced!");
    } else {
        Serial.println(" ⚠️ Time sync failed, using defaults");
    }
}

// ===== GET CURRENT TIMESTAMP =====
String getTimestamp() {
    struct tm timeinfo;
    if (!getLocalTime(&timeinfo)) {
        return "2026-01-01 12:00:00";  // Fallback
    }
    
    char buffer[20];
    strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", &timeinfo);
    return String(buffer);
}

// ===== RECORD AUDIO =====
bool recordAudio() {
    Serial.println("🎤 Recording started...");
    isRecording = true;
    
    size_t bytesRead = 0;
    int samplesRecorded = 0;
    
    // Record audio in chunks
    while (samplesRecorded < BUFFER_SIZE) {
        int16_t tempBuffer[512];
        size_t bytesToRead = min(512 * sizeof(int16_t), (BUFFER_SIZE - samplesRecorded) * sizeof(int16_t));
        
        esp_err_t result = i2s_read(I2S_NUM_0, tempBuffer, bytesToRead, &bytesRead, portMAX_DELAY);
        
        if (result == ESP_OK && bytesRead > 0) {
            int samplesRead = bytesRead / sizeof(int16_t);
            memcpy(&audioBuffer[samplesRecorded], tempBuffer, bytesRead);
            samplesRecorded += samplesRead;
        }
        
        // Print progress every second
        if (samplesRecorded % SAMPLE_RATE == 0) {
            Serial.printf("   %d/%d seconds\n", samplesRecorded / SAMPLE_RATE, RECORD_SECONDS);
        }
    }
    
    isRecording = false;
    Serial.printf("✅ Recording complete: %d samples\n", samplesRecorded);
    return true;
}

// ===== CREATE WAV HEADER =====
void writeWavHeader(uint8_t* header, int dataSize) {
    int fileSize = dataSize + 36;
    int byteRate = SAMPLE_RATE * 1 * 16 / 8;  // sampleRate * channels * bitsPerSample / 8
    int blockAlign = 1 * 16 / 8;              // channels * bitsPerSample / 8
    
    // RIFF chunk
    header[0] = 'R'; header[1] = 'I'; header[2] = 'F'; header[3] = 'F';
    header[4] = fileSize & 0xFF;
    header[5] = (fileSize >> 8) & 0xFF;
    header[6] = (fileSize >> 16) & 0xFF;
    header[7] = (fileSize >> 24) & 0xFF;
    header[8] = 'W'; header[9] = 'A'; header[10] = 'V'; header[11] = 'E';
    
    // fmt chunk
    header[12] = 'f'; header[13] = 'm'; header[14] = 't'; header[15] = ' ';
    header[16] = 16; header[17] = 0; header[18] = 0; header[19] = 0;  // Subchunk1Size (16 for PCM)
    header[20] = 1; header[21] = 0;  // AudioFormat (1 = PCM)
    header[22] = 1; header[23] = 0;  // NumChannels (1 = Mono)
    header[24] = SAMPLE_RATE & 0xFF;
    header[25] = (SAMPLE_RATE >> 8) & 0xFF;
    header[26] = (SAMPLE_RATE >> 16) & 0xFF;
    header[27] = (SAMPLE_RATE >> 24) & 0xFF;
    header[28] = byteRate & 0xFF;
    header[29] = (byteRate >> 8) & 0xFF;
    header[30] = (byteRate >> 16) & 0xFF;
    header[31] = (byteRate >> 24) & 0xFF;
    header[32] = blockAlign & 0xFF;
    header[33] = (blockAlign >> 8) & 0xFF;
    header[34] = 16; header[35] = 0;  // BitsPerSample (16)
    
    // data chunk
    header[36] = 'd'; header[37] = 'a'; header[38] = 't'; header[39] = 'a';
    header[40] = dataSize & 0xFF;
    header[41] = (dataSize >> 8) & 0xFF;
    header[42] = (dataSize >> 16) & 0xFF;
    header[43] = (dataSize >> 24) & 0xFF;
}

// ===== UPLOAD TO SERVER =====
bool uploadToServer() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("❌ WiFi not connected!");
        return false;
    }
    
    Serial.println("📤 Uploading to server...");
    
    HTTPClient http;
    http.begin(SERVER_URL);
    http.setTimeout(30000);  // 30 second timeout
    
    // Create multipart form data boundary
    String boundary = "----ESP32Boundary" + String(millis());
    http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);
    
    // Get timestamp
    String timestamp = getTimestamp();
    
    // Calculate sizes
    int audioDataSize = BUFFER_SIZE * sizeof(int16_t);
    int wavSize = 44 + audioDataSize;  // Header + data
    
    // Build the multipart body
    String bodyStart = "";
    bodyStart += "--" + boundary + "\r\n";
    bodyStart += "Content-Disposition: form-data; name=\"file\"; filename=\"recording.wav\"\r\n";
    bodyStart += "Content-Type: audio/wav\r\n\r\n";
    
    String bodyEnd = "";
    bodyEnd += "\r\n--" + boundary + "\r\n";
    bodyEnd += "Content-Disposition: form-data; name=\"lat\"\r\n\r\n";
    bodyEnd += String(LATITUDE, 6) + "\r\n";
    bodyEnd += "--" + boundary + "\r\n";
    bodyEnd += "Content-Disposition: form-data; name=\"lon\"\r\n\r\n";
    bodyEnd += String(LONGITUDE, 6) + "\r\n";
    bodyEnd += "--" + boundary + "\r\n";
    bodyEnd += "Content-Disposition: form-data; name=\"recorded_at\"\r\n\r\n";
    bodyEnd += timestamp + "\r\n";
    bodyEnd += "--" + boundary + "--\r\n";
    
    int contentLength = bodyStart.length() + wavSize + bodyEnd.length();
    http.addHeader("Content-Length", String(contentLength));
    
    // Create WiFiClient for streaming upload
    WiFiClient* client = http.getStreamPtr();
    
    // Start connection
    if (!http.connected()) {
        http.begin(SERVER_URL);
    }
    
    // Send using POST with streaming
    // First, send headers manually
    client->print("POST /upload HTTP/1.1\r\n");
    client->print("Host: " + String(SERVER_URL).substring(7, String(SERVER_URL).indexOf(':', 7)) + "\r\n");
    client->print("Content-Type: multipart/form-data; boundary=" + boundary + "\r\n");
    client->print("Content-Length: " + String(contentLength) + "\r\n");
    client->print("Connection: close\r\n\r\n");
    
    // Send body start
    client->print(bodyStart);
    
    // Send WAV header
    uint8_t wavHeader[44];
    writeWavHeader(wavHeader, audioDataSize);
    client->write(wavHeader, 44);
    
    // Send audio data in chunks (to avoid memory issues)
    int bytesSent = 0;
    int chunkSize = 4096;
    uint8_t* audioBytes = (uint8_t*)audioBuffer;
    
    while (bytesSent < audioDataSize) {
        int toSend = min(chunkSize, audioDataSize - bytesSent);
        client->write(&audioBytes[bytesSent], toSend);
        bytesSent += toSend;
        
        // Progress indicator
        if (bytesSent % 32768 == 0) {
            Serial.printf("   Sent: %d/%d bytes\n", bytesSent, audioDataSize);
        }
    }
    
    // Send body end
    client->print(bodyEnd);
    
    // Wait for response
    delay(100);
    String response = "";
    while (client->available()) {
        response += (char)client->read();
    }
    
    http.end();
    
    // Check response
    if (response.indexOf("200") > 0 || response.indexOf("success") > 0) {
        Serial.println("✅ Upload successful!");
        Serial.println(response);
        return true;
    } else {
        Serial.println("❌ Upload failed!");
        Serial.println(response);
        return false;
    }
}

// ===== SETUP =====
void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("\n====================================");
    Serial.println("🦅 ESP32 Bird Audio Recorder v1.0");
    Serial.println("====================================\n");
    
    // Allocate audio buffer (PSRAM if available)
    if (psramFound()) {
        audioBuffer = (int16_t*)ps_malloc(BUFFER_SIZE * sizeof(int16_t));
        Serial.println("✅ Using PSRAM for audio buffer");
    } else {
        audioBuffer = (int16_t*)malloc(BUFFER_SIZE * sizeof(int16_t));
        Serial.println("⚠️ Using internal RAM (limited)");
    }
    
    if (audioBuffer == nullptr) {
        Serial.println("❌ Failed to allocate audio buffer!");
        return;
    }
    
    setupWiFi();
    setupTime();
    setupI2S();
    
    Serial.println("\n🎤 Ready to record!\n");
}

// ===== MAIN LOOP =====
void loop() {
    static unsigned long lastRecording = 0;
    
    // Check WiFi connection
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("⚠️ WiFi disconnected, reconnecting...");
        setupWiFi();
    }
    
    // Record and upload at intervals
    if (millis() - lastRecording >= RECORD_INTERVAL_MS || lastRecording == 0) {
        lastRecording = millis();
        
        Serial.println("\n--- New Recording Session ---");
        Serial.printf("📍 Location: %.6f, %.6f\n", LATITUDE, LONGITUDE);
        Serial.printf("⏰ Time: %s\n", getTimestamp().c_str());
        
        if (recordAudio()) {
            uploadToServer();
        }
        
        Serial.printf("\n⏳ Next recording in %d seconds...\n", RECORD_INTERVAL_MS / 1000);
    }
    
    delay(100);
}
