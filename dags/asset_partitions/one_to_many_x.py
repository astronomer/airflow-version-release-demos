from airflow.sdk import (
    dag,
    task,
    Asset,
    CronPartitionTimetable,
    PartitionedAssetTimetable,
    FanOutMapper,
    StartOfDayMapper,
    DayWindow,
)

from airflow.providers.standard.operators.bash import BashOperator

data_ready = Asset("one_to_many_asset")


@dag(
    schedule=CronPartitionTimetable(
        "0 0 * * *", timezone="UTC", run_offset=-1
    ),  # run once per day at midnight UTC, partition key offset by -1 day
    tags=["partitions", "webinar"],
)
def one_to_many_upstream():

    @task(outlets=[data_ready])
    def my_task(**context):
        print(f"Partition key: {context['dag_run'].partition_key}")

    my_task()


one_to_many_upstream()


@dag(
    schedule=PartitionedAssetTimetable(
        assets=data_ready,
        # one daily upstream partition fans out into its 24 hourly downstream runs
        # (DayWindow defaults its downstream mapper to StartOfHourMapper)
        default_partition_mapper=FanOutMapper(
            upstream_mapper=StartOfDayMapper(), window=DayWindow(), #max_downstream_keys=10
        ),
    ),
    tags=["partitions",  "webinar"],
)
def one_to_many_downstream():

    @task
    def process_per_hour(**context):
        print(context["dag_run"].partition_key)

    process_per_hour()

    BashOperator(
        task_id="process_per_hour_bash",
        bash_command="echo {{ dag_run.partition_key }}",
    )


one_to_many_downstream()
