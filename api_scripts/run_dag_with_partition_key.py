import argparse
import os
from datetime import datetime, timezone
import requests

_USERNAME = "admin"
_PASSWORD = "admin"
_HOST = "http://localhost:8080"  # To learn how to send API requests to Airflow running on Astro see: https://www.astronomer.io/docs/astro/airflow-api/

_ENVIRONMENT = os.getenv("ENVIRONMENT", "LOCAL")


def _get_auth_headers() -> dict:
    if _ENVIRONMENT == "ASTRO":
        token = os.environ["ASTRO_ACCESS_TOKEN"]
        return {"Authorization": f"Bearer {token}"}

    url = f"{_HOST}/auth/token"
    response = requests.post(
        url,
        json={"username": _USERNAME, "password": _PASSWORD},
        headers={"Content-Type": "application/json"},
    )
    response.raise_for_status()
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _get_base_url() -> str:
    if _ENVIRONMENT == "ASTRO":
        deployment_url = os.environ["ASTRO_DEPLOYMENT_URL"]
        return f"https://{deployment_url}"
    return _HOST


def trigger_dag_run(dag_id: str, partition_key: str, logical_date: str | None = None):
    url = f"{_get_base_url()}/api/v2/dags/{dag_id}/dagRuns"
    headers = _get_auth_headers()
    payload = {
        "logical_date": logical_date or datetime.now(timezone.utc).isoformat(),
        "partition_key": partition_key,
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("--------------------------------")
        print(f"DAG run triggered successfully for DAG: {dag_id}")
        print(f"DAG Run ID:     {data.get('dag_run_id')}")
        print(f"Partition Key:  {partition_key}")
        print(f"State:          {data.get('state')}")
        print(f"Run After:      {data.get('run_after')}")
        print("--------------------------------")
    else:
        print("--------------------------------")
        print(f"Error {response.status_code} triggering DAG run for: {dag_id}")
        print(f"Response: {response.json()}")
        print("--------------------------------")
        response.raise_for_status()


def main():
    parser = argparse.ArgumentParser(description="Trigger an Airflow DAG run with a partition key.")
    parser.add_argument("dag_id", help="DAG ID to trigger")
    parser.add_argument("partition_key", help="The partition key to pass to the DAG run")
    parser.add_argument("--logical-date", default=None, help="Logical date in ISO 8601 format (default: now)")
    args = parser.parse_args()

    trigger_dag_run(args.dag_id, args.partition_key, args.logical_date)


if __name__ == "__main__":
    main()
