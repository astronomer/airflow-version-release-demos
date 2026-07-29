from airflow.sdk import dag, task
from pendulum import duration
from airflow.providers.common.ai.policies.retry import LLMRetryPolicy
from airflow.sdk.definitions.retry_policy import RetryAction, RetryRule

# llm_policy =
# the AI chooses the delay:
# LLM error classification: category=rate_limit, should_retry=True, delay=60s, reasoning=The error message indicates a 'Temporary Rate Limit', implying that the API has throttled usage due to exceeding allowed requests. This is a rate limiting issue, which typically resolves with a delay and retry once the limit resets.


@dag(tags=["pluggable retries", "webinar"])
def pluggable_retries_llm():

    @task(
        retries=5,
        retry_delay=duration(minutes=10),
        retry_policy=LLMRetryPolicy(  # let AI decide whether to retry
            llm_conn_id="pydanticai_default",
            timeout=30.0,  # max seconds to wait for LLM response
        ),
    )
    def my_task(**context):
        raise Exception("Temporary Rate Limit")

    my_task()


pluggable_retries_llm()
