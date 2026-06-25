from locust import HttpUser, task, between

class TargetAppUser(HttpUser):
    wait_time = between(0.5, 2)

    @task(5)
    def process(self):
        self.client.get("/process")

    @task(2)
    def health(self):
        self.client.get("/")

    @task(1)
    def fault_memory(self):
        self.client.get("/fault/memory")

    @task(1)
    def fault_cpu(self):
        self.client.get("/fault/cpu")

    @task(1)
    def fault_error(self):
        self.client.get("/fault/error")
