import requests
import time

base_url = "http://127.0.0.1:8000"

print("Waiting for server...")
for _ in range(10):
    try:
        if requests.get(base_url).status_code == 200:
            break
    except requests.exceptions.ConnectionError:
        time.sleep(1)

print("Adding documents...")
add_docs_resp = requests.post(
    f"{base_url}/add-docs",
    json={
        "documents": [
            "The capital of France is Paris.",
            "Jupiter is the largest planet in our solar system.",
            "Water boils at 100 degrees Celsius at sea level."
        ]
    }
)
print("Add docs response:", add_docs_resp.json())

print("Testing chat question 1...")
chat_resp = requests.post(
    f"{base_url}/chat",
    json={
        "query": "What is the capital of France?",
        "n_results": 1
    }
)
print("Chat response 1 status:", chat_resp.status_code)
print("Chat response 1 text:", chat_resp.text)
try:
    print("Chat response 1 JSON:", chat_resp.json())
except Exception as e:
    print("Failed to parse JSON:", e)

print("Testing chat question 2...")
chat_resp2 = requests.post(
    f"{base_url}/chat",
    json={
        "query": "Which planet is the largest?",
        "n_results": 1
    }
)
print("Chat response 2:", chat_resp2.json())
