from airflow.sdk import chain, dag, task, task_group


def at_least_threshold(*, loop, ti):
    threshold = ti.xcom_pull(task_ids="my_fetch_threshold_task")
    print(f"Iteration {loop.index}: result {loop.result}, threshold {threshold}")
    return loop.result >= threshold


@dag(tags=["task_loop"])
def basic_task_loop_until_upstream_threshold():
    @task
    def my_fetch_threshold_task():
        # for example, read the threshold from a file in object storage
        return 4

    @task_group
    def my_task_group():
        @task
        def my_count_task(*, loop):
            return (0 if loop.index == 0 else loop.previous) + 1

        my_count_task()

    _my_fetch_threshold_task = my_fetch_threshold_task()
    _my_task_group = my_task_group.loop(max_iterations=20, until=at_least_threshold)

    chain(_my_fetch_threshold_task, _my_task_group)


basic_task_loop_until_upstream_threshold()
