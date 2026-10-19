from datetime import timedelta

from airflow.sdk import dag, task, task_group


def at_least_10(*, loop, ti):
    print(f"until: index={loop.index} try_number={ti.try_number} max_tries={ti.max_tries}")
    if loop.index == 2 and ti.try_number == 1:
        raise RuntimeError("Failing the first try of the gate in iteration 2")
    return loop.result >= 10


@dag(tags=["task_loop", "experiments"])
def task_loop_experiments_gate_retries():

    @task
    def my_upstream_task():
        return 0

    @task_group(default_args={"retries": 2, "retry_delay": timedelta(seconds=1)})
    def my_task_group(my_number):
        @task
        def my_count_task(my_number, *, loop):
            return (my_number if loop.index == 0 else loop.previous) + 1

        my_count_task(my_number)

    @task
    def my_downstream_task(my_numbers):
        print(my_numbers[-1])

    _my_upstream_task = my_upstream_task()

    _my_task_group = my_task_group.partial(my_number=_my_upstream_task).loop(
        max_iterations=20, until=at_least_10
    )

    _my_downstream_task = my_downstream_task(_my_task_group["my_count_task"].output)


task_loop_experiments_gate_retries()
