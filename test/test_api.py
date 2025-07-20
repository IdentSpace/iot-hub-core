import sys
import os
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))



url = "http://localhost:8005/api/device/register"
data = {"key": "value"}
response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Response Body:", response.text)