from airflow.sdk import dag, task, task_group


def at_least_10(*, loop):
    return loop.result >= 10


@dag(tags=["task_loop", "experiments"])
def task_loop_experiments_loop_inside_group():

    @task
    def my_upstream_task():
        return 0

    @task_group
    def my_outer_task_group(my_number):
        @task_group
        def my_task_group(my_number):
            @task
            def my_count_task(my_number, *, loop):
                return (my_number if loop.index == 0 else loop.previous) + 1

            my_count_task(my_number)

        _my_task_group = my_task_group.partial(my_number=my_number).loop(
            max_iterations=20, until=at_least_10
        )

        @task
        def my_downstream_task(my_numbers):
            print(my_numbers[-1])

        my_downstream_task(_my_task_group["my_count_task"].output)

    _my_upstream_task = my_upstream_task()

    _my_outer_task_group = my_outer_task_group(my_number=_my_upstream_task)


task_loop_experiments_loop_inside_group()
