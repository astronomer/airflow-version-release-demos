import random

from airflow.sdk import (
    Asset,
    dag,
    task,
    PartitionedAssetTimetable,
    PartitionAtRuntime,
    AssetOrTimeSchedule,
)
from airflow.providers.standard.operators.bash import BashOperator

data_ready = Asset("my_partition_at_runtime_asset")

DEPARTMENTS = [
    "Engineering",
    "Product",
    "Legal",
    "Sales",
    "Marketing",
    "Finance",
    "HR",
    "Operations",
]


@dag
def my_partition_at_runtime_dag():

    @task(outlets=[data_ready])
    def my_task(**context):
        context["outlet_events"][data_ready].add_partitions(
            random.sample(DEPARTMENTS, 3)
        )

    my_task()


my_partition_at_runtime_dag()

@dag(
    schedule=PartitionedAssetTimetable(assets=data_ready),
    tags=["Custom asset partition"],
)
def custom_asset_partition_downstream():

    @task
    def process_data_from_yesterday(**context):
        print(context["dag_run"].partition_key)

    _process_data_from_yesterday = process_data_from_yesterday()

    BashOperator(
        task_id="process_data_from_yesterday_bash",
        bash_command="echo {{ dag_run.partition_key }}",
    )


custom_asset_partition_downstream()
