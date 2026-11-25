import sys, time
sys.path.insert(0, 'src')
from npa_ews.api import app
from fastapi.testclient import TestClient

print("Starting TestClient with app...", flush=True)
t0 = time.time()
with TestClient(app) as client:
    print(f"TestClient entered in {time.time()-t0:.2f}s", flush=True)
    r = client.get("/")
    print("GET / ->", r.status_code, r.json(), flush=True)
print("Exited TestClient successfully!", flush=True)
