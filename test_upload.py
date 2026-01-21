import requests

# 1. The URL of your local server
url = "http://localhost:8000/upload"

# 2. The Data (GPS)
payload = {
    "lat": "10.762",
    "lon": "106.660"
}

# 3. The File (Audio)
# REPLACE THIS with the actual path to one of your test files
file_path = "my_forest_audio/test_bird.wav" 

try:
    with open(file_path, "rb") as f:
        files = {"file": f}
        
        print(f"🚀 Sending {file_path} to server...")
        response = requests.post(url, data=payload, files=files)
        
    print(f"📡 Status Code: {response.status_code}")
    print(f"📄 Response: {response.json()}")

except FileNotFoundError:
    print("❌ Error: Could not find the audio file. Check the path!")