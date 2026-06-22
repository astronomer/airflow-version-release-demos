from airflow.sdk import (
    dag,
    task,
    Asset,
    CronPartitionTimetable,
    PartitionedAssetTimetable,
    RollupMapper,
    StartOfDayMapper,
    DayWindow,
)

from airflow.providers.standard.operators.bash import BashOperator

data_ready = Asset("many_to_one_asset")


@dag(
    schedule=CronPartitionTimetable(
        "0 * * * *", timezone="UTC", run_offset=-1
    ),  # run once per hour, partition key offset by -1 hour
    tags=["Many to one partition"],
)
def many_to_one_upstream():

    @task(outlets=[data_ready])
    def my_task(**context):
        print(f"Partition key: {context['dag_run'].partition_key}")

    my_task()


many_to_one_upstream()


@dag(
    schedule=PartitionedAssetTimetable(
        assets=data_ready,
        # the 24 hourly upstream partitions of a day roll up into one daily
        # downstream run (WaitForAll default: fires once all 24 hourly keys arrive)
        default_partition_mapper=RollupMapper(
            upstream_mapper=StartOfDayMapper(), window=DayWindow()
        ),
    ),
    tags=["Many to one partition"],
)
def many_to_one_downstream():

    @task
    def process_per_day(**context):
        print(context["dag_run"].partition_key)

    process_per_day()

    BashOperator(
        task_id="process_per_day_bash",
        bash_command="echo {{ dag_run.partition_key }}",
    )


many_to_one_downstream()
