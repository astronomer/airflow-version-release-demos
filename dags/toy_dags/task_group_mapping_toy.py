"""
### Dynamically map over a task group and pull XComs from specific tasks in the task group

This DAG shows three examples of dynamically mapping over a task group. Both, 
mapping positional arguments and keyword arguments are shown. A downstream task
demonstrates how to pull XComs from specific tasks in the task group.
"""

from airflow.decorators import dag, task_group, task
from pendulum import datetime


@dag(
    dag_id="task_group_mapping_toy",
    start_date=datetime(2022, 12, 1),
    schedule=None,
    catchup=False,
    tags=["task_group", "toy", "dynamic_task_mapping"],
)
def task_group_mapping_toy():
    # TASK GROUP 1: mapping over 1 positional argument
    @task_group(group_id="group1")
    def tg1(my_num):
        @task
        def print_num(num):
            return num

        @task
        def add_42(num):
            return num + 42

        print_num(my_num) >> add_42(my_num)

    # a downstream task to print out resulting XComs
    @task
    def pull_xcom(**context):
        pulled_xcom = context["ti"].xcom_pull(
            task_ids=[
                "group1.add_42"
            ],  # reference a task in a taskgroup with task_group_id.task_id
            map_indexes=[
                2,
                3,
            ],  # only pull xcom from specific mapped task instances (2.5 feature)
            key="return_value",
        )

        # will print out a list of results from map index 2 and 3 of the add_42 task
        print(pulled_xcom)

    # creating 6 mapped task instances of the TaskGroup tg2 (2.5 feature) mapping over one positional argument
    tg1_object = tg1.expand(my_num=[19, 23, 42, 8, 7, 108])

    # setting dependencies
    tg1_object >> pull_xcom()

    # TASK GROUP 2: mapping over 2 positional arguments, cross product
    @task_group(
        group_id="group2",
    )
    def tg2(my_num, my_string):
        @task
        def print_string(my_string):
            return my_string

        @task
        def add_42(num):
            return num + 42

        print_string(my_string) >> add_42(my_num)

    # creating 4 mapped task instances of the TaskGroup tg2 (2.5 feature) of 2 positional arguments
    tg2_object = tg2.expand(my_num=[1, 2], my_string=["A", "B"])

    # TASK GROUP 3: using expand_kwargs
    @task_group(
        group_id="group3",
    )
    def tg3(my_num, my_string):
        @task
        def print_string(my_string):
            return my_string

        @task
        def add_42(num):
            return num + 42

        print_string(my_string) >> add_42(my_num)

    # creating 2 mapped task instances of the TaskGroup using expand kwargs
    # positional arguments like my_num and my_string cannot be refernced in expand kwargs
    tg2_object = tg3.partial(my_num=4, my_string="C").expand_kwargs(
        [
            {
                "tooltip": "This taskgroup always runs all tasks",
                "default_args": {"trigger_rule": "all_done"},
            },
            {
                "tooltip": "This taskgroup needs the first task to be successful to run the second",
                "default_args": {"trigger_rule": "all_success"},
            },
        ]
    )


task_group_mapping_toy()
