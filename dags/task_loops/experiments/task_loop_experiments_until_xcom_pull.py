from airflow.sdk import dag, task, task_group


def at_least_threshold(*, loop, ti):
    threshold = ti.xcom_pull(task_ids="fetch_threshold")
    print(f"index={loop.index} result={loop.result} threshold={threshold}")
    return loop.result >= threshold


@dag(tags=["task_loop", "experiments"])
def task_loop_experiments_until_xcom_pull():

    @task
    def fetch_threshold():
        return 4

    @task_group
    def my_task_group():
        @task
        def my_count_task(*, loop):
            return (0 if loop.index == 0 else loop.previous) + 1

        my_count_task()

    _fetch_threshold = fetch_threshold()
    _my_task_group = my_task_group.loop(max_iterations=10, until=at_least_threshold)
    _fetch_threshold >> _my_task_group


task_loop_experiments_until_xcom_pull()
