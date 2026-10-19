from airflow.sdk import dag, task, task_group


def over_100(*, loop):
    return loop.result[1] > 100


@dag(tags=["task_loop"])
def basic_task_loop_fibonacci():

    @task
    def my_upstream_task():
        return [0, 1]

    @task_group
    def my_task_group(my_pair):
        @task
        def my_task_1(my_pair, *, loop):
            return my_pair if loop.index == 0 else loop.previous

        @task
        def my_task_2(my_pair):
            return [my_pair[1], my_pair[0] + my_pair[1]]

        my_task_2(my_task_1(my_pair))

    @task
    def my_downstream_task(my_results):
        print(my_results[-1])

    _my_upstream_task = my_upstream_task()

    _my_task_group = my_task_group.partial(my_pair=_my_upstream_task).loop(max_iterations=20, until=over_100)

    _my_downstream_task = my_downstream_task(_my_task_group["my_task_2"].output)


basic_task_loop_fibonacci()
