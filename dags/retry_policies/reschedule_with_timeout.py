from datetime import timedelta

from airflow.sdk import ExceptionRetryPolicy, RetryAction, RetryRule, dag, task


class ClusterBusyError(Exception):
    pass


policy = ExceptionRetryPolicy(
    rules=[
        RetryRule(
            exception=ClusterBusyError,
            action=RetryAction.RESCHEDULE,
            retry_delay=timedelta(seconds=10),
            reschedule_timeout=timedelta(seconds=25),
            reason="Cluster has no free capacity yet",
        ),
    ]
)


@dag(tags=["retry_policies"])
def reschedule_with_timeout():

    @task(retries=2, retry_delay=timedelta(seconds=30), retry_policy=policy)
    def submit_job(**context):
        try_number = context["ti"].try_number
        print(f"Try {try_number}")
        if try_number < 3:
            raise ClusterBusyError("No free executors on cluster 'etl-large'")

    submit_job()


reschedule_with_timeout()
