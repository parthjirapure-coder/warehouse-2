import requests
import threading
import time
import json

session1 = requests.Session()
# Login as supervisor via POST /
r = session1.post("http://127.0.0.1:5000/", data={"user_id": "SUP001", "password": "admin123"}, allow_redirects=True)
print("Supervisor login:", r.status_code, "url:", r.url)

received_events = []

def listen_sse():
    try:
        resp = session1.get("http://127.0.0.1:5000/api/live_activity/stream", stream=True, timeout=10)
        print("Connected to SSE stream, status:", resp.status_code)
        for line in resp.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith("data:"):
                    recv_time = time.time()
                    data = json.loads(line_str[5:].strip())
                    received_events.append((recv_time, data))
                    print(f"[{recv_time}] SSE received: {data.get('action') or data.get('status')}")
    except Exception as e:
        print("SSE listen error:", e)

t = threading.Thread(target=listen_sse, daemon=True)
t.start()

# Wait for SSE to connect
time.sleep(1.0)

# Now in session2, login as employee and post a movement
session2 = requests.Session()
r = session2.post("http://127.0.0.1:5000/", data={"user_id": "EMP001", "password": "123"}, allow_redirects=True)
print("Employee login:", r.status_code, "url:", r.url)

# Send AI movement asker message
post_time = time.time()
r_post = session2.post(
    "http://127.0.0.1:5000/api/ai/movement-asker",
    json={"action": "chat", "message": "add 55 pallet", "history": [], "draft": {}},
    headers={"X-Requested-With": "XMLHttpRequest"}
)
post_end = time.time()
print(f"Posted movement at {post_time}, took {post_end - post_time:.3f}s. Response:", r_post.status_code)

# Wait up to 3 seconds for event to arrive
wait_start = time.time()
matched = False
while time.time() - wait_start < 4:
    for recv_time, data in received_events:
        if data.get("action") in ("created", "batch_created"):
            latency = recv_time - post_time
            print(f"SUCCESS! Total elapsed from employee POST to supervisor SSE reception: {latency*1000:.1f}ms")
            matched = True
            break
    if matched:
        break
    time.sleep(0.05)

time.sleep(0.5)
print(f"Total events received: {len(received_events)}")
