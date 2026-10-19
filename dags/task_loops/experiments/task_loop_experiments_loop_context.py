from airflow.sdk import chain, dag, task, task_group


def print_loop(where, loop):
    print(
        f"{where}: index={loop.index} max_iterations={loop.max_iterations} "
        f"previous={loop.previous} result={loop.result}"
    )


def at_least_10(*, loop):
    print_loop("at_least_10", loop)
    return loop.result >= 10


@dag(tags=["task_loop", "experiments"])
def task_loop_experiments_loop_context():

    @task
    def my_upstream_task():
        return 0

    @task_group
    def my_task_group(my_number):
        @task
        def my_first_task(*, loop):
            print_loop("my_first_task", loop)

        @task
        def my_count_task(my_number, *, loop):
            print_loop("my_count_task", loop)
            return (my_number if loop.index == 0 else loop.previous) + 1

        chain(my_first_task(), my_count_task(my_number))

    @task
    def my_downstream_task(my_numbers):
        print(my_numbers[-1])

    _my_upstream_task = my_upstream_task()

    _my_task_group = my_task_group.partial(my_number=_my_upstream_task).loop(
        max_iterations=20, until=at_least_10
    )

    _my_downstream_task = my_downstream_task(_my_task_group["my_count_task"].output)


task_loop_experiments_loop_context()
