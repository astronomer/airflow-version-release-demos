from airflow.sdk import dag, task, task_group


def at_least_3(*, loop):
    return loop.result >= 3


@dag(tags=["task_loop", "experiments"])
def task_loop_experiments_prior_dates_xcom():
    @task_group
    def my_task_group():
        @task
        def my_count_task(*, loop):
            return (0 if loop.index == 0 else loop.previous) + 1

        my_count_task()

    @task
    def my_downstream_task(*, ti):
        value = ti.xcom_pull(task_ids="my_task_group.my_count_task", include_prior_dates=True)
        print(f"include_prior_dates=True returned: {value!r}")

    my_task_group.loop(max_iterations=10, until=at_least_3) >> my_downstream_task()


task_loop_experiments_prior_dates_xcom()
