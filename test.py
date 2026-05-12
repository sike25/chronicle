"""
Quick smoke test for the Chronicle API.
"""

import requests
import json

BASE_URL = "https://chronicle-435397225968.us-central1.run.app"
QUERY = "Jay Jay Okocha"

import time

def test_cache(query="Election crises and violence"):
    # first run — should be a cache miss, pipeline runs in full
    print("\n--- RUN 1 (expect MISS) ---")
    start = time.time()
    test_chronicle(query)
    print(f"Run 1 took {time.time() - start:.1f}s")

    # second run — should be a cache hit, replays instantly
    print("\n--- RUN 2 (expect HIT) ---")
    start = time.time()
    test_chronicle(query)
    print(f"Run 2 took {time.time() - start:.1f}s")


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
                event_type = decoded.split(":", 1)[1].strip()
            elif decoded.startswith("data:"):
                data = json.loads(decoded[5:].strip())
                if event_type == "cluster_enriched":
                    print("\n =================================================================================")
                    print(f"\nCluster {data['index']}: {data['title']} ({data['label']})")
                    for i, entry in enumerate(data["entries"]):
                        print(f"  -----> Entry {i}: {entry['filename']} - https://archivi.ng/search/{entry['id']}")
                else:
                    print(f"\n  event: {event_type}")
                    print(f"  {data}")

if __name__ == "__main__":
    test_health()
    test_cache(QUERY)