from airflow.sdk import (
    Asset,
    dag,
    task,
    PartitionedAssetTimetable,
)
from airflow.providers.standard.operators.bash import BashOperator

data_ready = Asset("simple_segment_partition_asset")


@dag(tags=["Simple segment partition"])
def simple_segment_partition_upstream():

    @task(outlets=[data_ready])
    def process_yesterday_data(**context):
        print(f"Partition key: {context['dag_run'].partition_key}")

    process_yesterday_data()


simple_segment_partition_upstream()


@dag(
    schedule=PartitionedAssetTimetable(assets=data_ready),
    tags=["Simple segment partition"],
)
def simple_segment_partition_downstream():

    @task
    def process_data_from_yesterday(**context):
        print(context["dag_run"].partition_key)

    _process_data_from_yesterday = process_data_from_yesterday()
    
    BashOperator(
        task_id="process_data_from_yesterday_bash",
        bash_command="echo '{{ dag_run.partition_key }}'",
    )


simple_segment_partition_downstream()
