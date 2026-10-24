from datetime import timedelta

from airflow.providers.common.ai.policies.retry import ClassifierRetryPolicy, ErrorCategory
from airflow.sdk import ChainRetryPolicy, ExceptionRetryPolicy, RetryAction, RetryRule, dag, task

known_failures = ExceptionRetryPolicy(
    rules=[
        RetryRule(exception=PermissionError, action=RetryAction.FAIL),
    ]
)

decision_model = ClassifierRetryPolicy(
    llm_conn_id="pydanticai_default",
    model_id="openai-decisions:gpt-6-luna",
    min_confidence=0.8,
    categories={
        "warehouse_suspended": ErrorCategory(
            "The warehouse is suspended and will auto-resume.",
            retry=True,
            delay=timedelta(seconds=30),
        ),
        "other": ErrorCategory("Any other failure.", retry=True),
    },
)

chain_policy = ChainRetryPolicy([known_failures, decision_model])


@dag(
    tags=["retry_policies"],
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=1),
        "retry_policy": chain_policy,
    },
)
def chain_retry_policy():

    @task
    def load_with_missing_grants():
        raise PermissionError("Insufficient privileges to operate on table 'ORDERS'")

    @task
    def query_suspended_warehouse():
        raise RuntimeError(
            "000606 (57P03): Warehouse 'ANALYTICS_WH' is suspended; auto-resume pending."
        )

    @task
    def parse_invalid_date():
        raise ValueError("Invalid date format in row 42")

    load_with_missing_grants()
    query_suspended_warehouse()
    parse_invalid_date()


chain_retry_policy()
