from airflow.sdk import (
    Asset,
    dag,
    task,
    CronPartitionTimetable,
    PartitionedAssetTimetable,
)
from airflow.providers.standard.operators.bash import BashOperator

data_ready = Asset("simple_asset_partition_example_asset")


@dag(
    schedule=CronPartitionTimetable(
        "0 0 * * *", timezone="UTC", run_offset=-1
    ),  # run at midnight UTC, offset key by -1 day
    tags=["Simple asset partition example"],
)
def simple_asset_partition_example_upstream():

    @task(outlets=[data_ready])
    def process_yesterday_data(**context):
        print(f"Partition key: {context['dag_run'].partition_key}")

    process_yesterday_data()


simple_asset_partition_example_upstream()


@dag(
    schedule=PartitionedAssetTimetable(assets=data_ready),
    tags=["Simple asset partition example"],
)
def simple_asset_partition_example_downstream():

    @task
    def process_data_from_yesterday(**context):
        print(context["dag_run"].partition_key)

    _process_data_from_yesterday = process_data_from_yesterday()

    BashOperator(
        task_id="process_data_from_yesterday_bash",
        bash_command="echo {{ dag_run.partition_key }}",
    )


simple_asset_partition_example_downstream()