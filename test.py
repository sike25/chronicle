"""
Quick local smoke test for the Chronicle API.
Run the server first: uvicorn app:app --reload
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    print(f"[health] {r.json()}")

def test_chronicle(query="Election crises and violence"):
    # 1. Start a job
    r = requests.post(f"{BASE_URL}/chronicle", json={"query": query})
    assert r.status_code == 202, f"Expected 202, got {r.status_code}: {r.text}"
    job_id = r.json()["job_id"]
    print(f"[chronicle] Job started: {job_id}")

    # 2. Stream results
    print(f"[stream] Listening on /chronicle/{job_id}/stream ...")
    with requests.get(f"{BASE_URL}/chronicle/{job_id}/stream", stream=True) as stream:
        for line in stream.iter_lines():
            if not line:
                continue
            decoded = line.decode("utf-8")
            if decoded.startswith("event:"):
                print(f"\n  {decoded}")
            elif decoded.startswith("data:"):
                data = json.loads(decoded[5:].strip())
                if "title" in data:
                    print(f"  --> [{data.get('index')}] {data['title']}")
                else:
                    print(f"  {data}")

if __name__ == "__main__":
    test_health()
    test_chronicle()
