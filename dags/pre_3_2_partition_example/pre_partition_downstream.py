from airflow.sdk import dag, task, Asset, chain
from pendulum import datetime, parse
from airflow.providers.standard.operators.bash import BashOperator


asset_1 = Asset("pre_partition_example_asset")


@dag(
    schedule=[asset_1],
    start_date=datetime(2026, 1, 1),
    tags=["Pre-3.2 partition example"],
)
def pre_partition_downstream():

    @task
    def process_yesterday_data_tf(**context):
        triggering_asset_events = context["triggering_asset_events"]
        for asset, asset_list in triggering_asset_events.items():
            print(f"Source run id: {asset_list[0].source_run_id}")
            run_date = parse(asset_list[0].source_run_id.split("__")[1])
            yesterday = run_date.subtract(days=1).date()
            print(f"Yesterday's date: {yesterday}")

    _process_yesterday_data_tf = process_yesterday_data_tf()

    _process_yesterday_data_bash = BashOperator(
        task_id="process_yesterday_data_bash",
        bash_command="echo {{ macros.ds_add((triggering_asset_events.values() | first | first).source_run_id.split('__')[1][:10], -1) }} ",
    )

    @task
    def process_yesterday_data_tf_from_extra(**context):
        triggering_asset_events = context["triggering_asset_events"]
        yesterday = triggering_asset_events[asset_1][0].extra["yesterday"]
        print(f"Yesterday's date: {yesterday}")


    _process_yesterday_data_bash_from_extra = BashOperator(
        task_id="process_yesterday_data_bash_from_extra",
        bash_command="echo {{ macros.ds_add((triggering_asset_events.values() | first | first).extra['yesterday'][:10], -1) }} ",
    )

    _process_yesterday_data_tf_from_extra = process_yesterday_data_tf_from_extra()

    chain(_process_yesterday_data_tf, _process_yesterday_data_bash, _process_yesterday_data_tf_from_extra)


pre_partition_downstream()
