from airflow.sdk import dag, task
from airflow.sdk.definitions.deadline import (
    SyncCallback,
    DeadlineAlert,
    DeadlineReference,
)

from pendulum import duration
from include.callback_functions import custom_async_callback, sync_callback



@dag(
    deadline=DeadlineAlert(
        reference=DeadlineReference.DAGRUN_QUEUED_AT,
        interval=duration(seconds=10),
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