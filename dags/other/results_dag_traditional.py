from airflow.sdk import DAG, chain
from airflow.providers.standard.operators.python import PythonOperator


def _my_task_func():
    return "hello!"


def _my_task_2_func():
    return "bye!"


with DAG("results_dag_traditional", tags=["wait result"]) as dag:
    _my_task = PythonOperator(task_id="my_task", python_callable=_my_task_func)
    _my_task_2 = PythonOperator(task_id="my_task_2", python_callable=_my_task_2_func)

    chain(_my_task_2, _my_task)

    dag.add_result(_my_task_2.output)
