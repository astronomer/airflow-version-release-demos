from airflow.sdk import dag, task, Asset
import random

my_asset = Asset("my_asset_state_example")


@dag(tags=["asset state store"])
def my_upstream_dag():

    @task(outlets=[my_asset])
    def my_upstream_task(asset_state_store):
        my_num = random.randint(1, 100)
        asset_state_store[my_asset].set("my_num", my_num)

    my_upstream_task()


my_upstream_dag()


@dag(tags=["asset state store"])
def my_downstream_dag():

    @task(inlets=[my_asset])
    def my_downstream_task(asset_state_store):
        my_num = asset_state_store[my_asset].get("my_num")
        print(my_num)

    my_downstream_task()


my_downstream_dag()
