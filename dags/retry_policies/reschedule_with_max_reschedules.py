from datetime import timedelta

from airflow.sdk import ExceptionRetryPolicy, RetryAction, RetryRule, dag, task


class ClusterBusyError(Exception):
    pass


class FlakyNetworkError(Exception):
    pass


policy = ExceptionRetryPolicy(
    rules=[
        RetryRule(
            exception=ClusterBusyError,
            action=RetryAction.RESCHEDULE,
            retry_delay=timedelta(seconds=5),
            max_reschedules=2,
            reason="Cluster has no free capacity yet",
        ),
        RetryRule(
            exception=FlakyNetworkError,
            action=RetryAction.RETRY,
            retry_delay=timedelta(seconds=5),
            reason="Network error, retrying soon",
        ),
    ]
)

OUTCOMES = ["busy", "flaky", "busy", "busy", "busy", "ok"]


@dag(tags=["retry_policies"])
def reschedule_with_max_reschedules():

    @task(retries=2, retry_delay=timedelta(seconds=30), retry_policy=policy)
    def submit_job(**context):
        task_state_store = context["task_state_store"]
        call = task_state_store.get("calls", default=0) + 1
        task_state_store.set("calls", call)
        outcome = OUTCOMES[min(call, len(OUTCOMES)) - 1]
        print(f"Call {call}, try {context['ti'].try_number}: {outcome}")
        if outcome == "busy":
            raise ClusterBusyError("No free executors on cluster 'etl-large'")
        if outcome == "flaky":
            raise FlakyNetworkError("Connection reset by peer")

    submit_job()


reschedule_with_max_reschedules()
