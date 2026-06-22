"""http://apache-airflow-docs.s3-website.eu-central-1.amazonaws.com/docs/apache-airflow/stable/authoring-and-scheduling/assets.html#segment-categorical-rollup"""

from airflow.sdk import (
    dag,
    task,
    Asset,
    PartitionedAssetTimetable,
    RollupMapper,
    FixedKeyMapper,
    SegmentWindow,
)
import random

from airflow.providers.standard.operators.bash import BashOperator

data_ready = Asset("process_sales_contracts")

DEPARTMENTS = [
    "Engineering",
    "Product",
    "Legal",
    "Sales",
]


@dag(tags=["Many to one segment partition"])
def many_to_one_segment_upstream():

    @task(outlets=[data_ready])
    def my_task(**context):
        context["outlet_events"][data_ready].add_partitions(
            random.sample(DEPARTMENTS, 1)
        )

    my_task()


many_to_one_segment_upstream()


@dag(
    schedule=PartitionedAssetTimetable(
        assets=data_ready,
        default_partition_mapper=RollupMapper(
            upstream_mapper=FixedKeyMapper("legal_and_sales"),
            window=SegmentWindow(["Legal", "Sales"]),
        ),
    ),
    tags=["Many to one segment partition"],
)
def many_to_one_segment_downstream():

    @task
    def process_per_day(**context):
        print(context["dag_run"].partition_key)

    process_per_day()

    BashOperator(
        task_id="process_per_day_bash",
        bash_command="echo {{ dag_run.partition_key }}",
    )


many_to_one_segment_downstream()
