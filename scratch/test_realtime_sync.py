import requests
import threading
import time
import json
import sys

BASE_URL = "http://127.0.0.1:5000"

def create_authenticated_session(user_id, password):
    s = requests.Session()
    r = s.post(f"{BASE_URL}/", data={"user_id": user_id, "password": password}, allow_redirects=True)
    if r.status_code != 200:
        raise Exception(f"Failed to login {user_id}: {r.status_code}")
    return s

class SseListener:
    def __init__(self, name, session):
        self.name = name
        self.session = session
        self.events = []
        self.running = True
        self.connected = False
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        try:
            resp = self.session.get(f"{BASE_URL}/api/live_activity/stream", stream=True, timeout=15)
            if resp.status_code != 200:
                print(f"[{self.name}] Stream status error: {resp.status_code}")
                return
            for line in resp.iter_lines():
                if not self.running:
                    break
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith("data:"):
                        recv_time = time.time()
                        try:
                            data = json.loads(line_str[5:].strip())
                            self.events.append((recv_time, data))
                            if data.get("status") == "connected":
                                self.connected = True
                            # print(f"[{self.name}] Event received: {data.get('action') or data.get('status')} at {recv_time}")
                        except Exception as parse_err:
                            pass
        except Exception as e:
            if self.running:
                print(f"[{self.name}] Stream exception: {e}")

    def wait_for_action(self, action_name, since_time, timeout=4.0):
        start = time.time()
        while time.time() - start < timeout:
            for recv_time, data in self.events:
                if recv_time >= since_time and data.get("action") == action_name:
                    return recv_time, data
            time.sleep(0.02)
        return None, None

def run_realtime_benchmark():
    print("=== STARTING MULTI-ROLE REAL-TIME LATENCY BENCHMARK ===")
    
    # 1. Login Supervisor, Manager, Employee
    sup_session = create_authenticated_session("SUP001", "admin123")
    mgr_session = create_authenticated_session("MGR001", "123")
    emp_session = create_authenticated_session("EMP001", "123")
    print("1. All 3 role sessions logged in successfully.")

    # 2. Start SSE streams for all 3 roles
    sup_sse = SseListener("SUPERVISOR", sup_session)
    mgr_sse = SseListener("MANAGER", mgr_session)
    emp_sse = SseListener("EMPLOYEE", emp_session)

    # Wait for streams to connect
    time.sleep(1.0)
    print(f"2. SSE Streams connected: Sup={sup_sse.connected}, Mgr={mgr_sse.connected}, Emp={emp_sse.connected}")

    # TEST A: Employee logs item via AI Movement Asker
    print("\n--- TEST A: Employee logs item movement ---")
    t0 = time.time()
    r = emp_session.post(
        f"{BASE_URL}/api/ai/movement-asker",
        json={"action": "chat", "message": "add 65 steel beams", "history": [], "draft": {}},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    t_post_end = time.time()
    resp_data = r.json()
    mov_id = resp_data.get("logged_movements", [{}])[0].get("id")
    print(f"Employee POST finished in {(t_post_end - t0)*1000:.1f}ms. Logged movement ID: {mov_id}")

    # Check Supervisor reception
    sup_time, sup_data = sup_sse.wait_for_action("created", t0)
    if sup_time:
        print(f"-> SUPERVISOR received created event in {(sup_time - t0)*1000:.1f}ms (from POST start) / {(sup_time - t_post_end)*1000:.1f}ms (from commit)")
    else:
        print("-> SUPERVISOR failed to receive created event!")

    # Check Manager reception
    mgr_time, mgr_data = mgr_sse.wait_for_action("created", t0)
    if mgr_time:
        print(f"-> MANAGER received created event in {(mgr_time - t0)*1000:.1f}ms (from POST start) / {(mgr_time - t_post_end)*1000:.1f}ms (from commit)")
    else:
        print("-> MANAGER failed to receive created event!")

    # TEST B: Manager verifies movement
    print(f"\n--- TEST B: Manager verifies movement #{mov_id} ---")
    t0 = time.time()
    r_ver = mgr_session.post(
        f"{BASE_URL}/movement/{mov_id}/verify",
        data={"action": "Verified"},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    t_ver_end = time.time()
    print(f"Manager verify POST finished in {(t_ver_end - t0)*1000:.1f}ms")

    # Check Supervisor reception
    sup_time, sup_data = sup_sse.wait_for_action("verified", t0)
    if sup_time:
        print(f"-> SUPERVISOR received verified event in {(sup_time - t0)*1000:.1f}ms")
    else:
        print("-> SUPERVISOR failed to receive verified event!")

    # Check Employee reception
    emp_time, emp_data = emp_sse.wait_for_action("verified", t0)
    if emp_time:
        print(f"-> EMPLOYEE received verified event in {(emp_time - t0)*1000:.1f}ms")
    else:
        print("-> EMPLOYEE failed to receive verified event!")

    # TEST C: Manager deletes movement
    print(f"\n--- TEST C: Manager deletes movement #{mov_id} ---")
    t0 = time.time()
    r_del = mgr_session.post(
        f"{BASE_URL}/movement/{mov_id}/delete",
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    t_del_end = time.time()
    print(f"Manager delete POST finished in {(t_del_end - t0)*1000:.1f}ms")

    # Check Supervisor reception (manager_deleted)
    sup_time, sup_data = sup_sse.wait_for_action("manager_deleted", t0)
    if sup_time:
        print(f"-> SUPERVISOR received manager_deleted event in {(sup_time - t0)*1000:.1f}ms")
    else:
        print("-> SUPERVISOR failed to receive manager_deleted event!")

    # Check Employee reception (manager_deleted)
    emp_time, emp_data = emp_sse.wait_for_action("manager_deleted", t0)
    if emp_time:
        print(f"-> EMPLOYEE received manager_deleted event in {(emp_time - t0)*1000:.1f}ms")
    else:
        print("-> EMPLOYEE failed to receive manager_deleted event!")

    # TEST D: Supervisor restores movement
    print(f"\n--- TEST D: Supervisor restores movement #{mov_id} ---")
    t0 = time.time()
    r_res = sup_session.post(
        f"{BASE_URL}/movement/{mov_id}/restore",
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    t_res_end = time.time()
    print(f"Supervisor restore POST finished in {(t_res_end - t0)*1000:.1f}ms")

    # Check Manager reception (restored)
    mgr_time, mgr_data = mgr_sse.wait_for_action("restored", t0)
    if mgr_time:
        print(f"-> MANAGER received restored event in {(mgr_time - t0)*1000:.1f}ms")
    else:
        print("-> MANAGER failed to receive restored event!")

    # Check Employee reception (restored)
    emp_time, emp_data = emp_sse.wait_for_action("restored", t0)
    if emp_time:
        print(f"-> EMPLOYEE received restored event in {(emp_time - t0)*1000:.1f}ms")
    else:
        print("-> EMPLOYEE failed to receive restored event!")

    print("\n=== BENCHMARK COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_realtime_benchmark()
