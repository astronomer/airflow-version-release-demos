from airflow.sdk import Asset, dag, task

data_ready = Asset("data_ready")


@dag
def my_etl_dag():

    @task(outlets=[data_ready])
    def load():
        return 1

    load()


my_etl_dag()


@dag(schedule=[data_ready])
def my_ml_dag():

    @task
    def task_2():
        return 2

    task_2()


my_ml_dag()
