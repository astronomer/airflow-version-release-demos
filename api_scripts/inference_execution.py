import requests
from datetime import datetime
import json
import argparse
import sys
from result_formatter import format_and_display_results

_USERNAME = "admin"
_PASSWORD = "admin"
_HOST = "http://localhost:8080/"  # To learn how to send API requests to Airflow running on Astro see: https://www.astronomer.io/docs/astro/airflow-api/

_DAG_ID = "sync_inference_execution_multi_agent"
_TASK_ID = "finalize_strategic_report"

def _get_jwt_token():
    token_url = f"{_HOST}/auth/token"
    payload = {"username": _USERNAME, "password": _PASSWORD}
    headers = {"Content-Type": "application/json"}
    response = requests.post(token_url, json=payload, headers=headers)

    token = response.json().get("access_token")
    return token


def _trigger_dag_run(dag_id: str, user_input: str):
    url = f"{_HOST}/api/v2/dags/{dag_id}/dagRuns"
    headers = {
        "Authorization": f"Bearer {_get_jwt_token()}",
        "Content-Type": "application/json",
    }
    payload = {
        "logical_date": None,
        "conf": {
            "user_input": user_input
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"Triggered DAG with request: {user_input}")
    return response.json()["dag_run_id"]


def _wait_for_dag_run_completion(dag_id: str, dag_run_id: str):
    url = f"{_HOST}/api/v2/dags/{dag_id}/dagRuns/{dag_run_id}/wait"
    headers = {
        "Authorization": f"Bearer {_get_jwt_token()}",
    }
    params = {
        "interval": 1,
        "result": [_TASK_ID],
    }
    response = requests.get(url, headers=headers, params=params)
    print(f"Status Code: {response.status_code}")

    lines = response.text.strip().split("\n")
    json_objects = []

    for line in lines:
        if line.strip():
            json_obj = json.loads(line)
            json_objects.append(json_obj)

    if json_objects:
        last_status_update = json_objects[-1]
        xcom_results = last_status_update.get("results", {})
        
        format_and_display_results(xcom_results)
        return xcom_results


def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "user_input",
        help="The LLM request/prompt to send to the DAG"
    )
    
    parser.add_argument(
        "--dag-id",
        default=_DAG_ID,
        help=f"DAG ID to trigger (default: {_DAG_ID})"
    )
    
    args = parser.parse_args()
    
    
    _dag_run_id = _trigger_dag_run(args.dag_id, args.user_input)
    _wait_for_dag_run_completion(args.dag_id, _dag_run_id)


if __name__ == "__main__":
    main()
