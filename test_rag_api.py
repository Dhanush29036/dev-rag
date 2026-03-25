import requests
import time

base_url = "http://127.0.0.1:8001"

print("Waiting for API server to start...")
for _ in range(15):
    try:
        if requests.get(base_url).status_code == 200:
            print("API Server is up!\n")
            break
    except requests.exceptions.ConnectionError:
        time.sleep(1)
else:
    print("Could not connect to API server. Please ensure it is running.")
    exit(1)

questions = [
    "how to i get my Activation code",
    "I recently do sign up in App but iam unable to see All tiles",
    "Iam not receiving notifications.",
    "Notifications not getting?",
    "why iam getting IVR calls from international number",
    "How i have to change my moving in status to CURRENT RESIDING",
    "How to edit profile",
    "how to add my vehicles",
    "How to contact RWA within the society in the App",
    "How to send the society notices"
]

print("--- Testing RAG API with 10 questions ---")

for i, q in enumerate(questions, 1):
    print(f"\n[Question {i}]: {q}")
    
    try:
        resp = requests.post(
            f"{base_url}/chat",
            json={
                "query": q,
                "n_results": 2
            }
        )
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"[Context]: {data.get('context_used', [])}")
            print(f"[Answer {i}]: {data.get('answer', '').strip()}")
        else:
            print(f"[Error {i}]: {resp.status_code} - {resp.text}")
            
    except Exception as e:
        print(f"[Failed {i}]: {e}")
        
    print("-" * 50)
    time.sleep(10)
