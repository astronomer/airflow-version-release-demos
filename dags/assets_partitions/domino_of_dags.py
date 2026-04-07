from airflow.sdk import (
    Asset,
    dag,
    task,
    CronPartitionTimetable,
    PartitionedAssetTimetable,
    StartOfHourMapper,
)
from airflow.providers.standard.operators.bash import BashOperator

domino_asset_1 = Asset("domino_asset_1")
domino_asset_2 = Asset("domino_asset_2")
domino_asset_3 = Asset("domino_asset_3")


@dag(schedule=CronPartitionTimetable("* * * * *", timezone="UTC"), tags=["Domino of Dags"])
def domino_dag_1():

    @task(outlets=[domino_asset_1])
    def my_producer_task_1():
        pass

    my_producer_task_1()


domino_dag_1()


@dag(schedule=PartitionedAssetTimetable(assets=domino_asset_1), tags=["Domino of Dags"])
def domino_dag_2():

    @task
    def print_partition_key_2(**context):
        print(context["dag_run"].partition_key)

    print_partition_key_2()

    _bash_print_partition_key = BashOperator(
        task_id="bash_print_partition_key_2",
        bash_command="echo {{ dag_run.partition_key }}",
    )

    @task(outlets=[domino_asset_2])
    def my_producer_task_2():
        pass

    my_producer_task_2()


domino_dag_2()


@dag(schedule=PartitionedAssetTimetable(assets=domino_asset_2), tags=["Domino of Dags"])
def domino_dag_3():

    @task
    def print_partition_key_3(**context):
        print(context["dag_run"].partition_key)

    print_partition_key_3()

    _bash_print_partition_key = BashOperator(
        task_id="bash_print_partition_key_3",
        bash_command="echo {{ dag_run.partition_key }}",
        outlets=[domino_asset_3],
    )


domino_dag_3()


@dag(schedule=PartitionedAssetTimetable(assets=domino_asset_3), tags=["Domino of Dags"])
def domino_dag_4():

    @task
    def print_partition_key_4(**context):
        print(context["dag_run"].partition_key)

    print_partition_key_4()


domino_dag_4()


@dag(
    schedule=PartitionedAssetTimetable(
        assets=domino_asset_2, default_partition_mapper=StartOfHourMapper()
    ),
    tags=["Domino of Dags"],
)
def leaf_dag():

    @task
    def print_partition_key_leaf(**context):
        print(context["dag_run"].partition_key)

    print_partition_key_leaf()


leaf_dag()
