from datetime import timedelta

from airflow.providers.standard.sensors.python import PythonSensor
from airflow.sdk import ExceptionRetryPolicy, RetryAction, RetryRule, dag, task
from airflow.sdk.exceptions import AirflowFailException

retry_everything = ExceptionRetryPolicy(
    rules=[
        RetryRule(
            exception=Exception,
            action=RetryAction.RETRY,
            retry_delay=timedelta(seconds=5),
            reason="Retry every exception",
        ),
    ]
)


@dag(
    tags=["retry_policies"],
    default_args={"retries": 3, "retry_policy": retry_everything},
)
def retry_policy_bypass():

    @task
    def fail_without_retry():
        raise AirflowFailException("Bad input data, retrying won't help")

    PythonSensor(
        task_id="sensor_times_out",
        python_callable=lambda: False,
        poke_interval=2,
        timeout=6,
        mode="poke",
    )

    fail_without_retry()


retry_policy_bypass()
