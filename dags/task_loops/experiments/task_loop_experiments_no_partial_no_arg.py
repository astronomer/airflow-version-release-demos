from airflow.sdk import dag, task, task_group


def at_least_10(*, loop):
    return loop.result >= 10


@dag(tags=["task_loop", "experiments"])
def task_loop_experiments_no_partial_no_arg():
    @task_group
    def my_task_group():
        @task
        def my_count_task(*, loop):
            return (0 if loop.index == 0 else loop.previous) + 1

        my_count_task()

    my_task_group.loop(max_iterations=20, until=at_least_10)


task_loop_experiments_no_partial_no_arg()
