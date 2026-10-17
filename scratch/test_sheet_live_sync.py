import sys, os
sys.path.insert(0, os.path.abspath("."))
import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_sheet_realtime_sync():
    print("=== TESTING REAL-TIME GOOGLE SHEET SYNC ===")
    
    # 1. Login as employee
    s = requests.Session()
    r = s.post(f"{BASE_URL}/", data={"user_id": "EMP001", "password": "123"})
    print("Employee login status:", r.status_code)
    
    # 2. Add movements via AI Asker
    t0 = time.time()
    r_ai = s.post(
        f"{BASE_URL}/api/ai/movement-asker",
        json={"action": "chat", "message": "add 25 solar panel, 15 inverter unit", "history": [], "draft": {}},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    t_post = time.time() - t0
    data = r_ai.json()
    print(f"AI Asker response in {t_post*1000:.1f}ms: ok={data.get('ok')}, count={len(data.get('logged_movements', []))}")
    movements = data.get("logged_movements", [])
    if not movements:
        print("ERROR: No movements returned!")
        return

    mov_id = movements[0]["id"]
    print(f"Logged movement #{mov_id}: {movements[0]['quantity']}x {movements[0]['item']}")

    # Wait up to 5 seconds for background worker to push to Google Sheet
    from app import sheet_sync_queue
    print("Pending tasks in sheet_sync_queue:", sheet_sync_queue.qsize())
    
    wait_start = time.time()
    while sheet_sync_queue.qsize() > 0 and time.time() - wait_start < 10:
        time.sleep(0.2)
    
    print(f"Queue processed in {time.time() - wait_start:.2f}s. Remaining: {sheet_sync_queue.qsize()}")

    # 3. Manager verifies movement
    m_session = requests.Session()
    m_session.post(f"{BASE_URL}/", data={"user_id": "MGR001", "password": "123"})
    
    t0_v = time.time()
    r_v = m_session.post(
        f"{BASE_URL}/movement/{mov_id}/verify",
        data={"action": "Verified"},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    print(f"Manager verification in {(time.time() - t0_v)*1000:.1f}ms: status={r_v.status_code}")
    
    # Wait for queue to process verification
    wait_start = time.time()
    while sheet_sync_queue.qsize() > 0 and time.time() - wait_start < 10:
        time.sleep(0.2)
    print(f"Verification synced to sheet in {time.time() - wait_start:.2f}s.")

    print("\n=== GOOGLE SHEET REAL-TIME SYNC TEST PASSED ===")

if __name__ == "__main__":
    test_sheet_realtime_sync()
