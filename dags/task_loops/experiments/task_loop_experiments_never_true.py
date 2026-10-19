from airflow.sdk import dag, task, task_group


def below_0(*, loop):
    return loop.result < 0


@dag(tags=["task_loop", "experiments"])
def task_loop_experiments_never_true():

    @task
    def my_upstream_task():
        return 0

    @task_group
    def my_task_group(my_number):
        @task
        def my_count_task(my_number, *, loop):
            return (my_number if loop.index == 0 else loop.previous) + 1

        my_count_task(my_number)

    @task
    def my_downstream_task(my_numbers):
        print(my_numbers[-1])

    _my_upstream_task = my_upstream_task()

    _my_task_group = my_task_group.partial(my_number=_my_upstream_task).loop(max_iterations=10, until=below_0)

    _my_downstream_task = my_downstream_task(_my_task_group["my_count_task"].output)


task_loop_experiments_never_true()
