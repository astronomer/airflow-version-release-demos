from airflow.sdk import dag, task, Asset
import random

my_asset = Asset("my_asset_state_example")

@dag
def my_upstream_dag():

    @task(outlets=[my_asset])
    def my_upstream_task(**context):
        my_num = random.randint(1, 100)
        context["asset_state_store"][my_asset].set("my_num", my_num)

    my_upstream_task()


my_upstream_dag()


@dag
def my_downstream_dag():

    @task(inlets=[my_asset])
    def my_downstream_task(**context):
        my_num = context["asset_state_store"][my_asset].get("my_num")

    my_downstream_task()

my_downstream_dag()