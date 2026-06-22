from airflow.sdk import (
    dag,
    task,
    task_group,
    ExceptionRetryPolicy,  # built-in RetryPolicy that maps exceptions to actions
    RetryRule,  # one exception(s) to behavior mapping for the above policy
    RetryAction,  # 3 retry actions: RetryAction.RETRY, RetryAction.FAIL, RetryAction.DEFAULT (fall through)
)
from airflow.sdk.exceptions import AirflowException
from pendulum import duration


class MyKeyError(KeyError): ...


# Rules evaluated in order!, if none matches -> Default retry logic of the task
MY_RETRY_POLICY = ExceptionRetryPolicy(
    rules=[
        RetryRule(
            exception=ValueError,
            action=RetryAction.RETRY,
            retry_delay=duration(seconds=3),
            reason="A",  # In the logs in post-execute
        ),
        RetryRule(
            exception="airflow.sdk.exceptions.AirflowException",  # can be the dottet path or the class
            action=RetryAction.FAIL,
            reason="B",
        ),
        RetryRule(
            exception=[
                TypeError,
                AttributeError,
            ],  # if any of those are raised the rule is used
            action=RetryAction.DEFAULT,  # uses regular retries logic of the task
            reason="C",
        ),
        RetryRule(
            exception=KeyError,
            action=RetryAction.FAIL,
            reason="D",
            match_subclasses=False,  # default=True then all subclasses of ValueError match as well
        ),
    ],
)


@dag(tags=["pluggable retries"])
def exception_retry_policy_example():

    @task_group
    def examples_exception_retry_policy():

        @task(
            retries=5, retry_policy=MY_RETRY_POLICY
        )  # the retries count is still the MAX retries, even if the policy says retry
        def t0(**context):
            raise ValueError

        t0()

        @task(retries=5, retry_policy=MY_RETRY_POLICY)
        def t1(**context):
            raise AirflowException

        t1()

        @task(retries=1, retry_policy=MY_RETRY_POLICY, retry_delay=duration(seconds=10))
        def t2(**context):
            raise AttributeError

        t2()

        @task(retries=2, retry_policy=MY_RETRY_POLICY, retry_delay=duration(seconds=10))
        def t3(**context):
            raise MyKeyError  # Because this is a subclass and match_subclasses=False, the task does NOT fail

        t3()

    examples_exception_retry_policy()


exception_retry_policy_example()
