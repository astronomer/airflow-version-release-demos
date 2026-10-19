from airflow.sdk import dag, task, task_group


def at_least_3(*, loop):
    return loop.result >= 3


@dag(tags=["task_loop", "experiments"])
def task_loop_experiments_get_previous_ti():

    @task_group
    def my_task_group():
        @task
        def my_count_task(*, loop, ti):
            previous_ti = ti.get_previous_ti()
            print(f"index={loop.index} run_id={ti.run_id} previous_ti={previous_ti!r}")
            if previous_ti is not None:
                print(
                    f"index={loop.index} own_region_index={ti.region_index} previous_ti run_id={previous_ti.run_id} "
                    f"region_index={previous_ti.region_index} state={previous_ti.state}"
                )
            return (0 if loop.index == 0 else loop.previous) + 1

        my_count_task()

    my_task_group.loop(max_iterations=10, until=at_least_3)


task_loop_experiments_get_previous_ti()
