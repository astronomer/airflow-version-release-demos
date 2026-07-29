from airflow.sdk import dag, task
from airflow.sdk.definitions.deadline import (
    SyncCallback,
    AsyncCallback,
    DeadlineAlert,
    DeadlineReference,
)

from datetime import timedelta


async def custom_async_callback(**kwargs):
    """Handle deadline violation with custom logic."""
    print(f"Deadline exceeded for Dag {kwargs.get("dag_id")}!")
    print(f"Alert type: {kwargs.get("alert_type")}")


def sync_callback(**kwargs):
    """Handle deadline violation with custom logic."""
    print(f"Deadline exceeded for Dag {kwargs.get("dag_id")}!")
    print(f"Alert type: {kwargs.get("alert_type")}")


@dag(
    deadline=DeadlineAlert(
        reference=DeadlineReference.DAGRUN_QUEUED_AT,
        interval=timedelta(seconds=10),
        callback=SyncCallback(
            sync_callback,
            kwargs={"alert_type": "time_exceeded", "dag_id": "deadline_alerts_dag"},
        ),
    ),
)
def deadline_alerts_sync_callback():
    @task
    def print_hello():
        import time

        time.sleep(15)
        print("Hello, World!")

    print_hello()


deadline_alerts_sync_callback()


@dag(
    deadline=DeadlineAlert(
        reference=DeadlineReference.DAGRUN_QUEUED_AT,
        interval=timedelta(seconds=10),
        callback=AsyncCallback(
            custom_async_callback,
            kwargs={"alert_type": "time_exceeded", "dag_id": "deadline_alerts_dag"},
        ),
    ),
)
def deadline_alerts_async_callback():
    @task
    def print_hello():
        import time

        time.sleep(15)
        print("Hello, World!")

    print_hello()


deadline_alerts_async_callback()
