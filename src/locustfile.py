import csv
import os
import sys
import uuid
from datetime import datetime

import requests
from dotenv import dotenv_values
from locust import HttpUser, between, events, run_single_user, task

ENV = dotenv_values(".env")
site = ENV["site"]

count_user = sys.argv[5]
total_requests = 0
total_failures = 0
total_successes = 0
test_start_time = None
server_up = False


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    host = site

    @task
    def index(self):
        global total_requests, total_failures, total_successes
        response = self.client.get("/")
        total_requests += 1
        if response.status_code == 200:
            total_successes += 1
        else:
            total_failures += 1


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    global total_requests, total_failures, total_successes, test_start_time, server_up

    try:
        response = requests.get(site)
        if response.status_code == 200:
            server_up = True
            print("Servidor está no ar.")
        else:
            print(f"Erro ao acessar o servidor. Status Code: {response.status_code}")
    except Exception as e:
        print(f"Erro ao acessar o servidor: {str(e)}")
        server_up = False
        quit()

    total_requests = 0
    total_failures = 0
    total_successes = 0
    test_start_time = datetime.now()


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    test_end_time = datetime.now()
    test_duration = (test_end_time - test_start_time).total_seconds()
    load_id = uuid.uuid4()
    log_load_test(load_id, test_duration)


def log_load_test(load_id, test_duration):
    global total_requests, total_failures, total_successes, test_start_time
    if server_up:
        data = {
            "load_id": load_id,
            "timestamp": test_start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_requests": total_requests,
            "total_failures": total_failures,
            "total_successes": total_successes,
            "test_duration": test_duration,
            "stress_category": str(count_user),
        }
        print("Carga de Teste:", data)
        file_exists = os.path.exists("load_test_summary.csv")
        with open("load_test_summary.csv", mode="a", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "load_id",
                    "timestamp",
                    "total_requests",
                    "total_failures",
                    "total_successes",
                    "test_duration",
                    "stress_category",
                ],
            )
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)


if __name__ == "__main__":
    run_single_user(WebsiteUser)
