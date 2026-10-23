from datetime import timedelta

from airflow.providers.common.ai.policies.retry import ClassifierRetryPolicy, ErrorCategory
from airflow.sdk import (
    ChainRetryPolicy,
    ExceptionRetryPolicy,
    RetryAction,
    RetryRule,
    dag,
    task,
)

DECISION_MODEL_CONN_ID = "decision_default"


class ClusterBusyError(Exception):
    pass


known_failures = ExceptionRetryPolicy(
    rules=[
        RetryRule(
            exception=PermissionError,
            action=RetryAction.FAIL,
            reason="Missing permissions, a person has to fix the grants",
        ),
        RetryRule(
            exception=ClusterBusyError,
            action=RetryAction.RESCHEDULE,
            retry_delay=timedelta(seconds=30),
            max_reschedules=3,
            reason="Cluster has no free capacity yet",
        ),
    ]
)

decision_model = ClassifierRetryPolicy(
    llm_conn_id=DECISION_MODEL_CONN_ID,
    min_confidence=0.8,
    categories={
        "warehouse_suspended": ErrorCategory(
            "The warehouse is suspended and will auto-resume.",
            delay=timedelta(seconds=30),
        ),
        "queued": ErrorCategory(
            "Statement queued or a concurrency limit reached; the warehouse is busy.",
            delay=timedelta(minutes=2),
        ),
        "schema_drift": ErrorCategory(
            "A referenced column, table, or view does not exist; a person has to fix the schema.",
            retry=False,
        ),
        "permanent": ErrorCategory(
            "A code or configuration error that fails the same way on every attempt.",
            retry=False,
            min_confidence=0.9,
        ),
    },
)

floor = ExceptionRetryPolicy(
    rules=[
        RetryRule(
            exception=ConnectionError,
            action=RetryAction.RETRY,
            retry_delay=timedelta(seconds=10),
            reason="Network error, retrying soon",
        ),
    ]
)

retry_policy = ChainRetryPolicy([known_failures, decision_model, floor])


@dag(
    tags=["retry_policies"],
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=1),
        "retry_policy": retry_policy,
    },
)
def chain_retry_policy():

    @task
    def load_with_missing_grants():
        raise PermissionError("Insufficient privileges to operate on table 'ORDERS'")

    @task
    def submit_to_busy_cluster():
        raise ClusterBusyError("No free executors on cluster 'etl-large'")

    @task
    def query_suspended_warehouse():
        raise RuntimeError(
            "000606 (57P03): Warehouse 'ANALYTICS_WH' is suspended; auto-resume pending."
        )

    @task
    def query_dropped_table():
        raise RuntimeError(
            "002003 (42S02): SQL compilation error: Object 'ORDERS_V2' does not exist."
        )

    @task
    def call_flaky_api():
        raise ConnectionError("Connection reset by peer")

    load_with_missing_grants()
    submit_to_busy_cluster()
    query_suspended_warehouse()
    query_dropped_table()
    call_flaky_api()


chain_retry_policy()
