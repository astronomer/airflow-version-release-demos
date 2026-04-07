from airflow.sdk import dag, task, Asset, chain, Metadata
from pendulum import datetime
from airflow.providers.standard.operators.bash import BashOperator


asset_1 = Asset("pre_partition_example_asset")


@dag(
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    tags=["Pre-3.2 partition example"],
)
def pre_partition_upstream():

    @task
    def processing_yesterday_data_tf(**context):
        logical_date = context["logical_date"]
        yesterday = logical_date.subtract(days=1)
        print(f"Processing data for {yesterday}")

    _processing_yesterday_data_tf = processing_yesterday_data_tf()

    _processing_yesterday_data_bash = BashOperator(
        task_id="processing_yesterday_data_bash",
        bash_command="echo {{ macros.ds_add(ds, -1) }}",
    )

    @task(outlets=[asset_1])
    def start_downstream_dag(**context):
        logical_date = context["logical_date"]
        yesterday = logical_date.subtract(days=1)
        yield Metadata(asset_1, {"yesterday": yesterday})

    _start_downstream_dag = start_downstream_dag()


    chain(_processing_yesterday_data_tf, _processing_yesterday_data_bash, _start_downstream_dag)


pre_partition_upstream()
