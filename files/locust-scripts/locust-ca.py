from locust import HttpUser, task, between, events
import time
import gevent
import csv
from datetime import datetime

# ====================== CONFIGURATION =========================
HOST = "http://tienphatng237.it.com"  # domain app
RAMP_UP_USERS = 100                   # bắt đầu 100 user
PEAK_USERS = 2000                     # tải cực đại
RAMP_UP_RATE = 100                    # thêm 100 user mỗi 5s
RAMP_UP_INTERVAL = 5
STABLE_TIME = 600                     # giữ tải cao 10 phút
COOLDOWN_TIME = 180                   # 3 phút giảm tải
LOG_FILE = "locust-ca-results.csv"    # file ghi log
# ===============================================================

class PetclinicHeavyUser(HttpUser):
    wait_time = between(0.5, 1.5)
    host = HOST

    @task(5)
    def home(self):
        self.client.get("/", name="Home")

    @task(3)
    def find_owners(self):
        self.client.get("/owners/find", name="Find Owner")

    @task(3)
    def vets(self):
        self.client.get("/vets.html", name="List Vets")

    @task(2)
    def api_customers(self):
        self.client.get("/api/customers", name="API Customers")

    @task(2)
    def api_visits(self):
        self.client.get("/api/visits", name="API Visits")

    @task(2)
    def api_vets(self):
        self.client.get("/api/vets", name="API Vets")


# ====================== CSV LOGGING ============================
@events.request.add_listener
def log_request(request_type, name, response_time, response_length, response, context, exception, **kw):
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
    with open(LOG_FILE, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "method", "endpoint", "response_time_ms", "response_length", "is_error"])

    def benchmark_flow():
        # Ramp-up
        print(f"[CA BENCHMARK] 🚀 Ramp up từ 0 → {PEAK_USERS} users ...")
        current_users = 0
        while current_users < PEAK_USERS:
            current_users += RAMP_UP_RATE
            environment.runner.start(current_users, spawn_rate=RAMP_UP_RATE)
            time.sleep(RAMP_UP_INTERVAL)

        # Stable high load (ép node đầy)
        print(f"[CA BENCHMARK] 📈 Giữ tải cực đại {PEAK_USERS} users trong {STABLE_TIME}s ...")
        time.sleep(STABLE_TIME)

        # Cooldown
        print(f"[CA BENCHMARK] 💤 Giảm tải dần trong {COOLDOWN_TIME}s ...")
        steps = int(COOLDOWN_TIME / 10)
        for i in range(steps):
            remaining = max(PEAK_USERS - int(i * (PEAK_USERS / steps)), 0)
            environment.runner.start(remaining, spawn_rate=RAMP_UP_RATE)
            time.sleep(10)

        print("[CA BENCHMARK] ✅ Kết thúc test.")
        environment.runner.quit()

    gevent.spawn(benchmark_flow)
