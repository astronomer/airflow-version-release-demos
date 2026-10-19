from airflow.sdk import chain, dag, task, task_group


def at_least_10(*, loop):
    return loop.result >= 10


@dag(tags=["task_loop", "experiments"])
def task_loop_experiments_group_inside_loop():

    @task
    def my_upstream_task():
        return 0

    @task_group
    def my_task_group(my_number):
        @task_group
        def my_inner_task_group():
            @task
            def my_inner_task(*, loop):
                print(f"Inner task group, iteration {loop.index}")

            my_inner_task()

        @task
        def my_count_task(my_number, *, loop):
            return (my_number if loop.index == 0 else loop.previous) + 1

        _my_inner_task_group = my_inner_task_group()
        _my_count_task = my_count_task(my_number)

        chain(_my_inner_task_group, _my_count_task)

    @task
    def my_downstream_task(my_numbers):
        print(my_numbers[-1])

    _my_upstream_task = my_upstream_task()

    _my_task_group = my_task_group.partial(my_number=_my_upstream_task).loop(
        max_iterations=20, until=at_least_10
    )

    _my_downstream_task = my_downstream_task(_my_task_group["my_count_task"].output)


task_loop_experiments_group_inside_loop()
