from airflow.sdk import dag, task, task_group


def quota_full_or_done(*, loop):
    return loop.result["used_mb"] >= 100 or loop.result["file_sizes_mb"] == []


@dag(tags=["task_loop"])
def basic_task_loop_upload_until_quota():

    @task
    def my_upstream_task():
        import random

        return {
            "used_mb": 0,
            "file_sizes_mb": [
                random.randint(10, 50) for _ in range(random.randint(5, 10))
            ],
        }

    @task_group
    def my_task_group(my_storage):
        @task
        def my_task_1(my_storage, *, loop):
            return my_storage if loop.index == 0 else loop.previous

        @task
        def my_task_2(my_storage):
            file_size_mb = my_storage["file_sizes_mb"][0]
            used_mb = my_storage["used_mb"] + file_size_mb
            print(f"Uploaded {file_size_mb} MB file, {used_mb} MB of quota used")
            return {"used_mb": used_mb, "file_sizes_mb": my_storage["file_sizes_mb"][1:]}

        my_task_2(my_task_1(my_storage))

    @task
    def my_downstream_task(my_results):
        print(f"Quota used: {my_results[-1]['used_mb']} MB")

    _my_upstream_task = my_upstream_task()

    _my_task_group = my_task_group.partial(my_storage=_my_upstream_task).loop(
        max_iterations=10, until=quota_full_or_done
    )

    _my_downstream_task = my_downstream_task(_my_task_group["my_task_2"].output)


basic_task_loop_upload_until_quota()
