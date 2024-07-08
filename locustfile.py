import pandas as pd
import time
from locust import HttpUser, task, between, events, run_single_user
from datetime import datetime

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    host = "https://ouvirparamudar-homologacao.pe.gov.br"

    @task
    def index(self):
        pass

    def log_server_health(self):
        response = self.client.get("/")
        data = {
            "timestamp": [datetime.now()],
            "status_code": [response.status_code],
            "response_time": [response.elapsed.total_seconds()],
            "content_length": [len(response.content)]
        }
        print('Dados:', data)
        df = pd.DataFrame(data)
        df.to_csv('server_health.csv', mode='a', index=False, header=False)

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    user = WebsiteUser(environment)
    user.log_server_health()
    environment.runner.quit()  # Adiciona um encerramento do Locust após o log

# To add headers to the CSV initially
if __name__ == "__main__":
    columns = ["timestamp", "status_code", "response_time", "content_length"]
    df = pd.DataFrame(columns=columns)
    df.to_csv('server_health.csv', index=False)

    run_single_user(WebsiteUser)
