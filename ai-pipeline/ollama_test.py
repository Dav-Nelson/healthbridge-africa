import requests
import json

url = "http://localhost:11434/api/generate"

payload = {
    "model": "llama3",
    "prompt": "What are symptoms of AIDS?",
    "stream": False
}

response = requests.post(url, json=payload)

data = response.json()

print("\nAI Response:\n")
print(data["response"])