from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.sdk import dag, task_group


@dag
def simple_task_group_dag():
    t0 = EmptyOperator(task_id="start")

    # Start task group definition
    @task_group(group_id="my_task_group")
    def tg1():
        t1 = EmptyOperator(task_id="task_1")
        t2 = EmptyOperator(task_id="task_2")

        t1 >> t2

    # End task group definition

    t3 = EmptyOperator(task_id="end")

    # Set task group's (tg1) dependencies
    t0 >> tg1() >> t3


simple_task_group_dag()
