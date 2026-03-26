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

# Similar/Paraphrased questions based on the CSV content
questions = [
    "How do I get the activation code for the app?",
    "I'm a new user but some features are missing in the app.",
    "Why am I not getting any push notifications on my phone?",
    "I'm receiving phone calls from foreign numbers for gate pass, why?",
    "How can I change my status from 'moving in' to 'resident'?",
    "What is the process to add my car or bike to my profile?",
    "How do I report or send a notice to the RWA?",
    "I paid my maintenance dues but the status hasn't updated.",
    "How can I download or see my past payment receipts?",
    "The app keeps lagging and is very slow, help!"
]

print("--- Testing RAG API with 10 SIMILAR questions ---")

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
            print(f"[Context Used]: {data.get('context_used', [])}")
            print(f"[Answer {i}]: {data.get('answer', '').strip()}")
        else:
            print(f"[Error {i}]: {resp.status_code} - {resp.text}")
            
    except Exception as e:
        print(f"[Failed {i}]: {e}")
        
    print("-" * 50)
    # Delay to avoid Gemini API rate limits (15 RPM for free tier)
    time.sleep(10)
