import errno
from datetime import timedelta

from airflow.sdk import ExceptionRetryPolicy, RetryAction, RetryRule, dag, task

FILE_RETRY_POLICY = ExceptionRetryPolicy(
    rules=[
        RetryRule(
            exception=TimeoutError,
            action=RetryAction.RETRY,
            retry_delay=timedelta(seconds=30),
            reason="Request timed out",
        ),
        RetryRule(
            exception="builtins.OSError",
            match_subclasses=False,
            action=RetryAction.RETRY,
            retry_delay=timedelta(minutes=2),
            reason="Transient I/O error",
        ),
        RetryRule(
            exception=[FileNotFoundError, "builtins.PermissionError"],
            action=RetryAction.FAIL,
            reason="Missing file or permissions, a person needs to fix it",
        ),
    ],
)


@dag(
    tags=["retry_policies"],
    default_args={
        "retries": 4,
        "retry_delay": timedelta(seconds=30),
        "retry_policy": FILE_RETRY_POLICY,
    },
)
def exception_retry_policy():

    @task
    def request_times_out(**context):
        if context["ti"].try_number == 1:
            raise TimeoutError("Read timed out after 30 seconds")

    @task
    def io_error(**context):
        if context["ti"].try_number == 1:
            raise OSError(errno.EIO, "Input/output error")

    @task
    def file_not_found():
        raise FileNotFoundError("No such file: 'include/orders.csv'")

    @task
    def permission_denied():
        raise PermissionError("Permission denied: 'include/orders.csv'")

    @task
    def no_matching_rule(**context):
        if context["ti"].try_number == 1:
            raise ValueError("Invalid date format in row 42")

    request_times_out()
    io_error()
    file_not_found()
    permission_denied()
    no_matching_rule()


exception_retry_policy()
