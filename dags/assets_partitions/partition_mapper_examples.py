from airflow.sdk import (
    Asset,
    dag,
    task,
    CronPartitionTimetable,
    PartitionedAssetTimetable,
    ToHourlyMapper,
    ToDailyMapper,
    ToWeeklyMapper,
    ToQuarterlyMapper,
    AllowedKeyMapper
)

asset_mappers_example_1 = Asset("asset_mappers_example_1")
asset_mappers_example_2 = Asset("asset_mappers_example_2")
asset_mappers_example_3 = Asset("asset_mappers_example_3")


@dag(schedule=CronPartitionTimetable("* * * * *", timezone="UTC"))
def asset_mappers_producer_dag_1():

    @task(outlets=[asset_mappers_example_1])
    def task_1(**context):
        print(f"Partition key: {context['dag_run'].partition_key}")

    task_1()


asset_mappers_producer_dag_1()

@dag(schedule=CronPartitionTimetable("* * * * *", timezone="UTC"))
def asset_mappers_producer_dag_2():

    @task(outlets=[asset_mappers_example_2])
    def task_2(**context):
        print(f"Partition key: {context['dag_run'].partition_key}")

    task_2()


asset_mappers_producer_dag_2()


@dag(
    schedule=PartitionedAssetTimetable(
        assets=(asset_mappers_example_1 | asset_mappers_example_2),  # scheduled to run when EITHER asset has an event
        default_partition_mapper=ToDailyMapper(), 
        partition_mapper_config={
            asset_mappers_example_2: ToWeeklyMapper(),
        },
    )
)
def asset_mapper_consumer_dag_1():  

    @task
    def task_1(**context):
        print(f"Partition key: {context['dag_run'].partition_key}")

    task_1()


asset_mapper_consumer_dag_1()



@dag(
    schedule=PartitionedAssetTimetable(
        assets=(asset_mappers_example_1 & asset_mappers_example_2),  # scheduled to run when BOTH assets have an event
        default_partition_mapper=ToQuarterlyMapper(),  # needs to be the same mapper for all assets in the AND condition, or the Dag would never trigger
    )
)
def asset_mapper_consumer_dag_2():  

    @task
    def task_1(**context):
        print(f"Partition key: {context['dag_run'].partition_key}")

    task_1()


asset_mapper_consumer_dag_2()


@dag(
    schedule=PartitionedAssetTimetable(
        assets=(asset_mappers_example_1 & asset_mappers_example_2), 
        default_partition_mapper=AllowedKeyMapper(["Marketing", "Sales"]),  # All other partition keys are ignored
    )
)
def asset_mapper_consumer_dag_3():  

    @task
    def task_1(**context):
        print(f"Partition key: {context['dag_run'].partition_key}")

    task_1()


asset_mapper_consumer_dag_3()