import random

from airflow.sdk import (
    Asset,
    dag,
    task,
    PartitionedAssetTimetable,
)
from airflow.providers.standard.operators.bash import BashOperator

data_ready = Asset("programmatic_partition_segment")

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


@dag(tags=["partitions"])
def programmatic_partition_segment_upstream():

    @task(outlets=[data_ready])
    def my_task(**context):
        context["outlet_events"][data_ready].add_partitions(
            random.sample(DEPARTMENTS, 3)
        )

    my_task()


programmatic_partition_segment_upstream()


@dag(
    schedule=PartitionedAssetTimetable(assets=data_ready),
    tags=["partitions"],
)
def programmatic_partition_segment_downstream():

    @task
    def process_data_from_yesterday(**context):
        print(context["dag_run"].partition_key)

    _process_data_from_yesterday = process_data_from_yesterday()

    BashOperator(
        task_id="process_data_from_yesterday_bash",
        bash_command="echo {{ dag_run.partition_key }}",
    )


programmatic_partition_segment_downstream()
