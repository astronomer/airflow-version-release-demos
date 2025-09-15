import requests
from datetime import datetime
import json

_USERNAME = "admin"
_PASSWORD = "admin"
_HOST = "http://localhost:8080/"  # To learn how to send API requests to Airflow running on Astro see: https://www.astronomer.io/docs/astro/airflow-api/

_DAG_ID = "sync_dag_execution"


def _get_jwt_token():
    token_url = f"{_HOST}/auth/token"
    payload = {"username": _USERNAME, "password": _PASSWORD}
    headers = {"Content-Type": "application/json"}
    response = requests.post(token_url, json=payload, headers=headers)

    token = response.json().get("access_token")
    return token


def _trigger_dag_run(dag_id: str):
    url = f"{_HOST}/api/v2/dags/{dag_id}/dagRuns"
    headers = {
        "Authorization": f"Bearer {_get_jwt_token()}",
        "Content-Type": "application/json",
    }
    payload = {
        "logical_date": None,
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()["dag_run_id"]


def _wait_for_dag_run_completion(dag_id: str, dag_run_id: str):
    url = f"{_HOST}/api/v2/dags/{dag_id}/dagRuns/{dag_run_id}/wait"
    headers = {
        "Authorization": f"Bearer {_get_jwt_token()}",
        "Accept": "application/x-ndjson",
    }
    params = {
        "interval": 5,
        "result": ["print_hello"],
    }
    response = requests.get(url, headers=headers, params=params, stream=True)

    json_objects = []

    for line in response.iter_lines(chunk_size=None,decode_unicode=True):
        if line: 
            json_obj = json.loads(line)
            json_objects.append(json_obj)
            print(f"Status: {json_obj.get('state', 'unknown')}", flush=True)

    if json_objects:
        last_status_update = json_objects[-1]
        xcom_results = last_status_update.get("results", {})
        print("Last status update:", last_status_update)
        print("XCom results:", xcom_results)


if __name__ == "__main__":
    _dag_run_id = _trigger_dag_run(_DAG_ID)
    _wait_for_dag_run_completion(_DAG_ID, _dag_run_id)
