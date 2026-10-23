"""
## AI orchestration

Uncolored version of the rainbow Dag, used for Airflow UI screenshots.

A complex Dag structure showing:
- Dynamically mapped tasks
- A branch with labeled edges
- A regular task group
- A dynamically mapped task group
- A looped task group
- Setup and teardown tasks
- An asset outlet
- A human-in-the-loop approval task
"""

from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.hitl import ApprovalOperator
from airflow.providers.standard.operators.python import BranchPythonOperator, PythonOperator
from pendulum import datetime

from airflow.sdk import Asset, Label, chain, dag, task_group


def named_operator(base, name):
    return type(name, (base,), {})


StartOperator = named_operator(EmptyOperator, "StartOperator")
CheckApiConnectionOperator = named_operator(EmptyOperator, "CheckApiConnectionOperator")
CheckStorageConnectionOperator = named_operator(EmptyOperator, "CheckStorageConnectionOperator")

ExtractFromObjectStorageOperator = named_operator(BashOperator, "ExtractFromObjectStorageOperator")
TransformOperator = named_operator(EmptyOperator, "TransformOperator")
LoadToDwhOperator = named_operator(EmptyOperator, "LoadToDwhOperator")

ExtractFromApiOperator = named_operator(BashOperator, "ExtractFromApiOperator")
LoadTypeBranchOperator = named_operator(BranchPythonOperator, "LoadTypeBranchOperator")
LoadApiToDwhOperator = named_operator(EmptyOperator, "LoadApiToDwhOperator")

ExtractFromCrmOperator = named_operator(EmptyOperator, "ExtractFromCrmOperator")
DeduplicateOperator = named_operator(EmptyOperator, "DeduplicateOperator")
ValidateOperator = named_operator(EmptyOperator, "ValidateOperator")
EnrichOperator = named_operator(EmptyOperator, "EnrichOperator")
MergeOperator = named_operator(EmptyOperator, "MergeOperator")
LoadCrmOperator = named_operator(EmptyOperator, "LoadCrmOperator")

GetRegionsOperator = named_operator(PythonOperator, "GetRegionsOperator")
PrepareReportOperator = named_operator(BashOperator, "PrepareReportOperator")
BuildChartsOperator = named_operator(EmptyOperator, "BuildChartsOperator")
BuildTablesOperator = named_operator(EmptyOperator, "BuildTablesOperator")
PublishReportOperator = named_operator(EmptyOperator, "PublishReportOperator")
CombineReportsOperator = named_operator(EmptyOperator, "CombineReportsOperator")

SpinUpGpuOperator = named_operator(EmptyOperator, "SpinUpGpuOperator")
GetTrainingDataOperator = named_operator(EmptyOperator, "GetTrainingDataOperator")
TrainModelOperator = named_operator(PythonOperator, "TrainModelOperator")
TearDownGpuOperator = named_operator(EmptyOperator, "TearDownGpuOperator")

CheckFreshnessOperator = named_operator(EmptyOperator, "CheckFreshnessOperator")
RunQualityCheckOperator = named_operator(BashOperator, "RunQualityCheckOperator")
SendSummaryOperator = named_operator(EmptyOperator, "SendSummaryOperator")


def choose_load_type():
    import random

    return random.choice(["internal_api_load_full", "internal_api_load_incremental"])


def get_regions():
    return ["emea", "amer", "apac"]


def train_and_score_model(loop):
    return round(0.7 + 0.1 * loop.index, 2)


def model_good_enough(*, loop):
    return loop.result >= 0.9


@dag(schedule="0 0 * * *", start_date=datetime(2026, 10, 1), catchup=False, tags=["ui_features"])
def ai_orchestration():
    start = StartOperator(task_id="start")
    end = EmptyOperator(
        task_id="end", trigger_rule="none_failed", outlets=[Asset("dag_completed")]
    )

    @task_group
    def preflight_checks():
        CheckApiConnectionOperator(task_id="check_api_connection")
        CheckStorageConnectionOperator(task_id="check_storage_connection")

    preflight = preflight_checks()

    sales_data_extract = ExtractFromObjectStorageOperator.partial(
        task_id="sales_data_extract"
    ).expand(bash_command=["echo 1", "echo 2", "echo 3", "echo 4"])
    sales_data_transform = TransformOperator(task_id="sales_data_transform")
    sales_data_load = LoadToDwhOperator(task_id="sales_data_load")

    internal_api_extract = ExtractFromApiOperator.partial(task_id="internal_api_extract").expand(
        bash_command=["echo 1", "echo 2", "echo 3", "echo 4"]
    )
    determine_load_type = LoadTypeBranchOperator(
        task_id="determine_load_type", python_callable=choose_load_type
    )
    internal_api_load_full = LoadApiToDwhOperator(task_id="internal_api_load_full")
    internal_api_load_incremental = LoadApiToDwhOperator(task_id="internal_api_load_incremental")

    crm_extract = ExtractFromCrmOperator(task_id="crm_extract")

    @task_group
    def crm_integration():
        deduplicate = DeduplicateOperator(task_id="deduplicate")
        validate = ValidateOperator(task_id="validate")
        enrich = EnrichOperator(task_id="enrich")
        merge = MergeOperator(task_id="merge")
        chain(deduplicate, [validate, enrich], merge)

    crm_load = LoadCrmOperator(task_id="crm_load")

    regions = GetRegionsOperator(task_id="get_regions", python_callable=get_regions)

    @task_group
    def sales_reporting(region):
        prepare_report = PrepareReportOperator(
            task_id="prepare_report",
            bash_command="echo Preparing report for $REGION",
            env={"REGION": region},
            append_env=True,
        )
        build_charts = BuildChartsOperator(task_id="build_charts")
        build_tables = BuildTablesOperator(task_id="build_tables")
        publish_report = PublishReportOperator(task_id="publish_report")
        chain(prepare_report, [build_charts, build_tables], publish_report)

    combine_reports = CombineReportsOperator(task_id="combine_reports")

    spin_up_gpu = SpinUpGpuOperator(task_id="spin_up_gpu")

    @task_group
    def train_model():
        get_training_data = GetTrainingDataOperator(task_id="get_training_data")
        train = TrainModelOperator(task_id="train", python_callable=train_and_score_model)
        chain(get_training_data, train)

    approve_model = ApprovalOperator(
        task_id="approve_model",
        subject="Approve the trained model",
        body="Review the model score before tearing down the GPU.",
    )

    tear_down_gpu = TearDownGpuOperator(task_id="tear_down_gpu").as_teardown(setups=spin_up_gpu)

    check_freshness = CheckFreshnessOperator(task_id="check_freshness", retries=3)
    run_quality_check = RunQualityCheckOperator.partial(task_id="run_quality_check").expand(
        bash_command=["echo nulls", "echo duplicates", "echo ranges"]
    )
    send_summary = SendSummaryOperator(task_id="send_summary")
    notify_team = EmptyOperator(task_id="notify_team")

    chain(start, preflight)

    chain(preflight, sales_data_extract, sales_data_transform, sales_data_load, end)

    chain(preflight, internal_api_extract, determine_load_type)
    chain(determine_load_type, Label("old data edited"), internal_api_load_full, end)
    chain(determine_load_type, Label("additional data"), internal_api_load_incremental, end)

    chain(preflight, crm_extract, crm_integration(), crm_load, end)

    chain(
        preflight,
        regions,
        sales_reporting.expand(region=regions.output),
        combine_reports,
        end,
    )

    chain(
        preflight,
        spin_up_gpu,
        train_model.loop(max_iterations=5, until=model_good_enough),
        approve_model,
        tear_down_gpu,
        end,
    )

    chain(preflight, check_freshness, run_quality_check, send_summary, notify_team, end)


ai_orchestration()
