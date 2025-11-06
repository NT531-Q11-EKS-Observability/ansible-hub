from locust import HttpUser, task, between, events
import time
import gevent
import csv
from datetime import datetime

# ====================== CONFIGURATION =========================
HOST = "http://tienphatng237.it.com"  # domain app
RAMP_UP_USERS = 50                    # bắt đầu với 50 user
PEAK_USERS = 500                      # tải cực đại
RAMP_UP_RATE = 10                     # tốc độ tăng user (mỗi 5 giây)
RAMP_UP_INTERVAL = 5
STABLE_TIME = 180                     # 3 phút giữ tải cao
COOLDOWN_TIME = 180                   # 3 phút giảm tải
LOG_FILE = "locust-hpa-results.csv"   # file ghi log
# ===============================================================

class PetclinicUser(HttpUser):
    wait_time = between(1, 3)
    host = HOST

    # -------- TASKS (Gọi cả frontend và backend REST API) --------
    @task(3)
    def home(self):
        self.client.get("/", name="Home")

    @task(2)
    def find_owners(self):
        self.client.get("/owners/find", name="Find Owner")

    @task(2)
    def vets(self):
        self.client.get("/vets.html", name="List Vets")

    @task(1)
    def api_customers(self):
        self.client.get("/api/customers", name="API Customers")

    @task(1)
    def api_visits(self):
        self.client.get("/api/visits", name="API Visits")

    @task(1)
    def api_vets(self):
        self.client.get("/api/vets", name="API Vets")


# ====================== CSV LOGGING ============================
@events.request.add_listener
def log_request(request_type, name, response_time, response_length, response, context, exception, **kw):
    """Ghi log chi tiết mỗi request ra CSV để phân tích latency, throughput, error rate."""
    with open(LOG_FILE, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.utcnow().isoformat(),
            request_type,
            name,
            response_time,
            response_length,
            1 if exception else 0
        ])


@events.test_start.add_listener
def on_test_start(environment, **_kwargs):
    """Chuỗi giai đoạn: ramp-up → giữ tải → giảm tải."""
    with open(LOG_FILE, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "method", "endpoint", "response_time_ms", "response_length", "is_error"])

    def benchmark_flow():
        # Ramp-up
        print(f"[HPA BENCHMARK] 🚀 Ramp up từ 0 → {PEAK_USERS} users ...")
        current_users = 0
        while current_users < PEAK_USERS:
            current_users += RAMP_UP_RATE
            environment.runner.start(current_users, spawn_rate=RAMP_UP_RATE)
            time.sleep(RAMP_UP_INTERVAL)

        # Stable high load
        print(f"[HPA BENCHMARK] 📈 Giữ tải cao {PEAK_USERS} users trong {STABLE_TIME}s ...")
        time.sleep(STABLE_TIME)

        # Cooldown
        print(f"[HPA BENCHMARK] 💤 Giảm tải dần trong {COOLDOWN_TIME}s ...")
        steps = int(COOLDOWN_TIME / 10)
        for i in range(steps):
            remaining = max(PEAK_USERS - int(i * (PEAK_USERS / steps)), 0)
            environment.runner.start(remaining, spawn_rate=RAMP_UP_RATE)
            time.sleep(10)

        print("[HPA BENCHMARK] ✅ Kết thúc test.")
        environment.runner.quit()

    gevent.spawn(benchmark_flow)
