from airflow.sdk import dag, task
from pendulum import datetime


def create_dag(dag_id, schedule, dag_number, default_args):
    @dag(dag_id=dag_id, schedule=schedule, default_args=default_args)
    def hello_world_dag():
        @task()
        def hello_world(*args):
            print("Hello World")
            print("This is DAG: {}".format(str(dag_number)))

        hello_world()

    generated_dag = hello_world_dag()

    return generated_dag


# build a dag for each number in range(1, 4)
for n in range(1, 4):
    dag_id = "hello_world_{}".format(str(n))

    default_args = {"owner": "airflow", "start_date": datetime(2026, 10, 18)}

    schedule = "@daily"

    dag_number = n

    globals()[dag_id] = create_dag(dag_id, schedule, dag_number, default_args)
