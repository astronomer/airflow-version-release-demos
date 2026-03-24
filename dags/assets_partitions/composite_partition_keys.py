from airflow.sdk import (
    dag,
    PartitionedAssetTimetable,
    Asset,
    ProductMapper,
    IdentityMapper,
    ToDailyMapper,
    AllowedKeyMapper,
    task,
)


@dag(
    schedule=PartitionedAssetTimetable(
        assets=Asset(
            "my_partitioned_asset"
        ),  # the partition key needs to be provided in the format `Finance|2026-03-16T09:00:00|Revenue`
        partition_mapper_config={
            Asset("my_partitioned_asset"): ProductMapper(
                IdentityMapper(), ToDailyMapper(), AllowedKeyMapper(["Revenue", "ARR"])
            ),
        },
    )
)
def my_composite_dag():

    @task
    def my_task(**context):
        partition_key = context["dag_run"].partition_key
        print(
            partition_key
        )  # prints the partition key in the format `Finance|2026-03-16|Revenue`

    my_task()


my_composite_dag()
