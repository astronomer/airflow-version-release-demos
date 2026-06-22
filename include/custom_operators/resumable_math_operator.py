from airflow.sdk import ResumableJobMixin
from airflow.sdk.bases.operator import BaseOperator


class MyResumableMathOperator(ResumableJobMixin, BaseOperator):
    """
    Basic arithmetic Operator that uses ResumableJobMixin to save information between retries.

    :param first_number: first number to put into an equation
    :param second_number: second number to put into an equation
    :param operation: mathematical operation to perform
    :param simulate_crash: if True, crash once after submit to demo the resume
    """

    valid_operations = ("+", "-", "*", "/")
    template_fields = ("first_number", "second_number")
    result_key = "math_result"

    def __init__(
        self,
        first_number: float,
        second_number: float,
        operation: str,
        simulate_crash: bool = True,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.first_number = first_number
        self.second_number = second_number
        self.operation = operation
        self.simulate_crash = simulate_crash

        if self.operation not in self.valid_operations:
            raise ValueError(
                f"{self.operation} is not a valid operation. Choose one of {self.valid_operations}"
            )

    def execute(self, context):
        return self.execute_resumable(context)

    def submit_job(self, context):
        res = self._compute()
        store = context.get("task_state_store")
        if store is not None:
            store.set(self.result_key, res)
        job_id = f"math-{self.operation}-{self.first_number}-{self.second_number}"
        self.log.info(f"Submitted math job {job_id}; cached result {res} in task_state_store.")
        return job_id

    def get_job_status(self, external_id, context):
        store = context.get("task_state_store")
        if store is not None and store.get(self.result_key) is not None:
            return "SUCCEEDED"
        return "PENDING"

    def is_job_active(self, status):
        return status == "PENDING"

    def is_job_succeeded(self, status):
        return status == "SUCCEEDED"

    def poll_until_complete(self, external_id, context):
        if self.simulate_crash and context["ti"].try_number == 1:
            raise RuntimeError(
                "Simulated crash after submit. The result and job id are already in the "
                "task_state_store; the retry will reconnect and return the cached result."
            )
        self.log.info(f"Job {external_id} complete.")

    def get_job_result(self, external_id, context):
        store = context.get("task_state_store")
        res = store.get(self.result_key) if store is not None else self._compute()
        self.log.info(f"Returning result {res} for job {external_id} (read from task_state_store, no recompute).")
        return res

    def _compute(self):
        self.log.info(
            f"Equation: {self.first_number} {self.operation} {self.second_number}"
        )
        if self.operation == "+":
            return self.first_number + self.second_number
        if self.operation == "-":
            return self.first_number - self.second_number
        if self.operation == "*":
            return self.first_number * self.second_number
        if self.operation == "/":
            try:
                return self.first_number / self.second_number
            except ZeroDivisionError:
                self.log.critical(
                    "If you have set up an equation where you are trying to divide by zero, "
                    "you have done something WRONG. - Randall Munroe, 2006"
                )
                raise
