from airflow.sdk import dag, task, Asset, Metadata
import random

my_asset = Asset("my_asset_extra_example")


@dag(tags=["Asset event extra"])
def my_upstream_dag_2():

    @task(outlets=[my_asset])
    def my_upstream_task(**context):
        my_num = random.randint(1, 100)
        yield Metadata(my_asset, {"my_num": my_num})

    my_upstream_task()


my_upstream_dag_2()


@dag(schedule=my_asset)
def my_downstream_dag_2():

    @task(inlets=[my_asset])
    def my_downstream_task_1(**context):
        # inlet_events are listed earliest to latest by timestamp
        asset_events = context["inlet_events"][my_asset]
        # protect against the asset not existing
        if len(asset_events) == 0:
            print(f"No asset_events for {my_asset.name}")
        else:
            # accessing the latest asset event for this asset
            # if the extra does not exist, return None
            my_extra = asset_events[-1].extra
            print(my_extra)

    my_downstream_task_1()

    @task
    def my_downstream_task_2(**context):
        for asset, asset_list in context["triggering_asset_events"].items():
            my_num = asset_list[0].extra["my_num"]
            print(my_num)

    my_downstream_task_2()


my_downstream_dag_2()
