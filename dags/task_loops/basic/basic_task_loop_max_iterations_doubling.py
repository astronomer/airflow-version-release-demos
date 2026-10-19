from airflow.sdk import dag, task, task_group, chain


@dag(tags=["task_loop"])
def basic_task_loop_max_iterations_doubling():

    @task
    def my_upstream_task():
        import random

        return random.randint(1, 10)

    @task_group
    def my_task_group(my_number):
        @task
        def my_task_1(my_number, *, loop):
            return my_number if loop.index == 0 else loop.previous

        @task
        def my_task_2(my_number):
            print(f"Still looping, the number is: {my_number}")

        @task
        def my_task_3(my_number):
            return my_number * 2

        _my_task_1 = my_task_1(my_number)
        _my_task_2 = my_task_2(my_number=_my_task_1)
        _my_task_3 = my_task_3(my_number=_my_task_1)

        chain(_my_task_2, _my_task_3)

    @task
    def my_downstream_task(my_results):
        print(my_results[-1])

    _my_upstream_task = my_upstream_task()

    _my_task_group = my_task_group.partial(my_number=_my_upstream_task).loop(
        max_iterations=10  # no until condition means this will always loop 10 times
    )

    _my_downstream_task = my_downstream_task(_my_task_group["my_task_3"].output)


basic_task_loop_max_iterations_doubling()
