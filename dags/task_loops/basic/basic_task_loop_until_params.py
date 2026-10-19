from airflow.sdk import dag, task, task_group


def at_least_threshold(*, loop, params):
    return loop.result >= params["threshold"]


@dag(params={"threshold": 10}, tags=["task_loop"])
def basic_task_loop_until_params():
    @task_group
    def my_task_group():
        @task
        def my_count_task(*, loop):
            return (0 if loop.index == 0 else loop.previous) + 1

        my_count_task()

    my_task_group.loop(max_iterations=20, until=at_least_threshold)


basic_task_loop_until_params()
