from airflow.sdk import dag, task 
from pendulum import duration
from airflow.providers.common.ai.policies.retry import LLMRetryPolicy
from airflow.sdk.definitions.retry_policy import RetryAction, RetryRule

llm_policy = LLMRetryPolicy(
    llm_conn_id="pydanticai_default",
    timeout=30.0,  # max seconds to wait for LLM response
    fallback_rules=[  # used when LLM call fails
        RetryRule(exception=ConnectionError, action=RetryAction.RETRY, retry_delay=duration(seconds=10)),
        RetryRule(exception=PermissionError, action=RetryAction.FAIL),
    ],
)
# the AI chooses the delay:
# LLM error classification: category=rate_limit, should_retry=True, delay=60s, reasoning=The error message indicates a 'Temporary Rate Limit', implying that the API has throttled usage due to exceeding allowed requests. This is a rate limiting issue, which typically resolves with a delay and retry once the limit resets.

@dag(tags=["pluggable retries"])
def pluggable_retries_llm():

    @task(
        retries=5,
        retry_delay=duration(seconds=5),
        retry_policy=llm_policy
    )
    def my_task(**context):
        raise Exception("Temporary Rate Limit")


    my_task()


pluggable_retries_llm()