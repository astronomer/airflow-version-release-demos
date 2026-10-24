from datetime import timedelta

from airflow.providers.common.ai.policies.retry import (
    ClassifierRetryPolicy,
    ErrorCategory,
    LLMRetryPolicy,
)
from airflow.sdk import RetryAction, RetryRule, dag, task

llm_policy = LLMRetryPolicy(
    llm_conn_id="pydanticai_default",
    model_id="openai:gpt-6-luna",
    fallback_rules=[
        RetryRule(exception=ConnectionError, action=RetryAction.RETRY, retry_delay=timedelta(seconds=10)),
    ],
)

classifier_policy = ClassifierRetryPolicy(
    llm_conn_id="pydanticai_default",
    model_id="openai-decisions:gpt-6-luna",
    min_confidence=0.8,
    categories={
        "rate_limited": ErrorCategory(
            "The API rejected the request because of a rate limit.",
            retry=True,
            delay=timedelta(minutes=1),
        ),
        "invalid_credentials": ErrorCategory(
            "The API rejected the credentials.",
            retry=False,
        ),
        "other": ErrorCategory("Any other failure.", retry=True),
    },
)


@dag(tags=["retry_policies"])
def ai_retry_policies():

    @task(retries=3, retry_policy=llm_policy)
    def call_api_with_llm_policy():
        raise RuntimeError("429 Too Many Requests: Rate limit exceeded. Retry after 60 seconds.")

    @task(retries=3, retry_policy=classifier_policy)
    def call_api_with_classifier_policy():
        raise RuntimeError("401 Unauthorized: Invalid API key provided.")

    call_api_with_llm_policy()
    call_api_with_classifier_policy()


ai_retry_policies()
