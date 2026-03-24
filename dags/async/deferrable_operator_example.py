from airflow.sdk import dag, task 
from include.custom_deferrable_operator import MyDeferrableOperator

@dag 
def deferrable_operator_example():

    MyDeferrableOperator(
        task_id="deferrable_operator_task",
        wait_for_completion=True,
        poke_interval=10,
        deferrable=True,
    )

deferrable_operator_example()
