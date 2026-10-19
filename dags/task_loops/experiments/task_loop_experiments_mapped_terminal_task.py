from airflow.sdk import dag, task, task_group


def at_least_10(*, loop):
    print(f"until: index={loop.index} previous={loop.previous} result={loop.result}")
    return min(loop.result) >= 10


@dag(tags=["task_loop", "experiments"])
def task_loop_experiments_mapped_terminal_task():

    @task
    def my_upstream_task():
        return 0

    @task_group
    def my_task_group(my_number):
        @task
        def my_count_task(my_number, my_step, *, loop):
            print(f"my_count_task: index={loop.index} previous={loop.previous} result={loop.result}")
            return (my_number if loop.index == 0 else min(loop.previous)) + my_step

        my_count_task.partial(my_number=my_number).expand(my_step=[1, 2, 3])

    @task
    def my_downstream_task(my_numbers):
        print(f"all: {list(my_numbers)} len={len(my_numbers)}")
        print(f"last: {my_numbers[-1]}")

    _my_upstream_task = my_upstream_task()

    _my_task_group = my_task_group.partial(my_number=_my_upstream_task).loop(
        max_iterations=20, until=at_least_10
    )

    _my_downstream_task = my_downstream_task(_my_task_group["my_count_task"].output)


task_loop_experiments_mapped_terminal_task()
