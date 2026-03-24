from airflow.sdk import (
    Asset,
    dag,
    task,
    CronPartitionTimetable,
    PartitionedAssetTimetable,
    ToHourlyMapper,
)
from airflow.providers.standard.operators.bash import BashOperator

chain_asset_1 = Asset("chain_asset_1")
chain_asset_2 = Asset("chain_asset_2")
chain_asset_3 = Asset("chain_asset_3")


@dag(schedule=CronPartitionTimetable("* * * * *", timezone="UTC"))
def chain_dag_1():

    @task(outlets=[chain_asset_1])
    def my_producer_task_1():
        pass

    my_producer_task_1()


chain_dag_1()


@dag(schedule=PartitionedAssetTimetable(assets=chain_asset_1))
def chain_dag_2():

    @task
    def print_partition_key_2(**context):
        print(context["dag_run"].partition_key)

    print_partition_key_2()

    _bash_print_partition_key = BashOperator(
        task_id="bash_print_partition_key_2",
        bash_command="echo {{ dag_run.partition_key }}",
    )

    @task(outlets=[chain_asset_2])
    def my_producer_task_2():
        pass

    my_producer_task_2()


chain_dag_2()


@dag(schedule=PartitionedAssetTimetable(assets=chain_asset_2))
def chain_dag_3():

    @task
    def print_partition_key_3(**context):
        print(context["dag_run"].partition_key)

    print_partition_key_3()

    _bash_print_partition_key = BashOperator(
        task_id="bash_print_partition_key_3",
        bash_command="echo {{ dag_run.partition_key }}",
        outlets=[chain_asset_3],
    )


chain_dag_3()


@dag(schedule=PartitionedAssetTimetable(assets=chain_asset_3))
def chain_dag_4():

    @task
    def print_partition_key_4(**context):
        print(context["dag_run"].partition_key)

    print_partition_key_4()


chain_dag_4()


@dag(
    schedule=PartitionedAssetTimetable(
        assets=chain_asset_2, default_partition_mapper=ToHourlyMapper()
    )
)
def leaf_dag():

    @task
    def print_partition_key_leaf(**context):
        print(context["dag_run"].partition_key)

    print_partition_key_leaf()


leaf_dag()
