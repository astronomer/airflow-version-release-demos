from airflow.sdk import dag, task, task_group, chain


# function for the until condition
def over_100(*, loop):
    loop_result = loop.result["doubled_number"]
    print(f"Loop result: {loop_result}")
    return loop_result > 100  # Loop stops if True


@dag(tags=["task_loop", "webinar"])
def basic_task_loop_doubling():

    @task
    def my_upstream_task():
        import random

        return random.randint(1, 10)

    @task_group
    def my_task_group(my_number):
        @task
        def my_task_1(my_number, *, loop):
            return my_number if loop.index == 0 else loop.previous["doubled_number"]

        @task
        def my_task_2(my_number):
            print(f"Still looping, the number is: {my_number}")

        @task
        def my_task_3(my_number):
            return {"doubled_number": my_number * 2}

        _my_task_1 = my_task_1(my_number)
        _my_task_2 = my_task_2(my_number=_my_task_1)
        _my_task_3 = my_task_3(my_number=_my_task_1)

        # this dependency is needed because looped task group need a singular final task
        chain(_my_task_2, _my_task_3)

    @task
    def my_downstream_task(my_results):
        print(my_results[-1])

    _my_upstream_task = my_upstream_task()

    _my_task_group = my_task_group.partial(my_number=_my_upstream_task).loop(
        max_iterations=5, until=over_100
    )

    _my_downstream_task = my_downstream_task(_my_task_group["my_task_3"].output)


basic_task_loop_doubling()
