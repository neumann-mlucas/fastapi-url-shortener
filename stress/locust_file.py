import random

from locust import FastHttpUser, task

data = (
    "AAAAAAAC",
    "AAAAAAAB",
    "AAAAAAAD",
    "AAAAAAAF",
    "AAAAAAAG",
    "AAAAAAAH",
    "AAAAAAAI",
    "AAAAAAAJ",
    "AAAAAAAK",
    "AAAAAAAL",
)


class StressTests(FastHttpUser):
    @task
    def redirect_route(self):
        for i in data:
            self.client.get(f"/api/v1/{i}")
