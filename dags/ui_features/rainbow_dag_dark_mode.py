"""
## Rainbow Dag (dark mode)

A complex Dag structure showing:
- Dynamically mapped tasks
- A branch with labeled edges
- A regular task group
- A dynamically mapped task group
- A looped task group
- Setup and teardown tasks
- An asset outlet

With all task groups collapsed, each lane has its own color.
"""

from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.python import BranchPythonOperator, PythonOperator
from airflow.sdk import Asset, Label, chain, dag, task_group

COLORS = {
    "red": ("#E22016", "#FFFFFF"),
    "orange": ("#F28917", "#000000"),
    "yellow": ("#EFE524", "#000000"),
    "green": ("#78B82A", "#000000"),
    "blue": ("#2C58A4", "#FFFFFF"),
    "violet": ("#6D2380", "#FFFFFF"),
    "sunflower": ("#FDD817", "#6D2380"),
    "charcoal": ("#000000", "#FFFFFF"),
    "brown": ("#945516", "#FFFFFF"),
    "lemon": ("#FCF434", "#000000"),
    "white": ("#FFFFFF", "#000000"),
    "lavender": ("#9C59D1", "#FFFFFF"),
    "graphite": ("#2C2C2C", "#FFFFFF"),
    "black": ("#000000", "#FFFFFF"),
    "gray": ("#A3A3A3", "#000000"),
    "plum": ("#800080", "#FFFFFF"),
    "sky_blue": ("#7BCCE5", "#000000"),
    "pink": ("#F4AEC8", "#000000"),
}


def add_color(base, name, color):
    ui_color, ui_fgcolor = COLORS[color]
    return type(name, (base,), {"ui_color": ui_color, "ui_fgcolor": ui_fgcolor})


StartOperator = add_color(EmptyOperator, "StartOperator", "sunflower")
CheckApiConnectionOperator = add_color(EmptyOperator, "CheckApiConnectionOperator", "charcoal")
CheckStorageConnectionOperator = add_color(
    EmptyOperator, "CheckStorageConnectionOperator", "brown"
)

ExtractFromObjectStorageOperator = add_color(BashOperator, "ExtractFromObjectStorageOperator", "red")
TransformOperator = add_color(EmptyOperator, "TransformOperator", "red")
LoadToDwhOperator = add_color(EmptyOperator, "LoadToDwhOperator", "red")

ExtractFromApiOperator = add_color(BashOperator, "ExtractFromApiOperator", "orange")
LoadTypeBranchOperator = add_color(BranchPythonOperator, "LoadTypeBranchOperator", "orange")
LoadApiToDwhOperator = add_color(EmptyOperator, "LoadApiToDwhOperator", "orange")

ExtractFromCrmOperator = add_color(EmptyOperator, "ExtractFromCrmOperator", "yellow")
DeduplicateOperator = add_color(EmptyOperator, "DeduplicateOperator", "lemon")
ValidateOperator = add_color(EmptyOperator, "ValidateOperator", "white")
EnrichOperator = add_color(EmptyOperator, "EnrichOperator", "lavender")
MergeOperator = add_color(EmptyOperator, "MergeOperator", "graphite")
LoadCrmOperator = add_color(EmptyOperator, "LoadCrmOperator", "yellow")

GetRegionsOperator = add_color(PythonOperator, "GetRegionsOperator", "green")
PrepareReportOperator = add_color(BashOperator, "PrepareReportOperator", "black")
BuildChartsOperator = add_color(EmptyOperator, "BuildChartsOperator", "gray")
BuildTablesOperator = add_color(EmptyOperator, "BuildTablesOperator", "white")
PublishReportOperator = add_color(EmptyOperator, "PublishReportOperator", "plum")
CombineReportsOperator = add_color(EmptyOperator, "CombineReportsOperator", "green")

SpinUpGpuOperator = add_color(EmptyOperator, "SpinUpGpuOperator", "blue")
GetTrainingDataOperator = add_color(EmptyOperator, "GetTrainingDataOperator", "sky_blue")
TrainModelOperator = add_color(PythonOperator, "TrainModelOperator", "pink")
TearDownGpuOperator = add_color(EmptyOperator, "TearDownGpuOperator", "blue")

CheckFreshnessOperator = add_color(EmptyOperator, "CheckFreshnessOperator", "violet")
RunQualityCheckOperator = add_color(BashOperator, "RunQualityCheckOperator", "violet")
SendSummaryOperator = add_color(EmptyOperator, "SendSummaryOperator", "violet")


def choose_load_type():
    import random

    return random.choice(["internal_api_load_full", "internal_api_load_incremental"])


def get_regions():
    return ["emea", "amer", "apac"]


def train_and_score_model(loop):
    return round(0.7 + 0.1 * loop.index, 2)


def model_good_enough(*, loop):
    return loop.result >= 0.9


@dag(tags=["rainbow"])
def rainbow_dag_dark_mode():
    start = StartOperator(task_id="start")
    end = EmptyOperator(
        task_id="end", trigger_rule="none_failed", outlets=[Asset("rainbow_complete")]
    )

    @task_group(ui_color=COLORS["brown"][0], ui_fgcolor=COLORS["brown"][1])
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

    @task_group(ui_color=COLORS["yellow"][0], ui_fgcolor=COLORS["yellow"][1])
    def crm_integration():
        deduplicate = DeduplicateOperator(task_id="deduplicate")
        validate = ValidateOperator(task_id="validate")
        enrich = EnrichOperator(task_id="enrich")
        merge = MergeOperator(task_id="merge")
        chain(deduplicate, [validate, enrich], merge)

    crm_load = LoadCrmOperator(task_id="crm_load")

    regions = GetRegionsOperator(task_id="get_regions", python_callable=get_regions)

    @task_group(ui_color=COLORS["green"][0], ui_fgcolor=COLORS["green"][1])
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

    @task_group(ui_color=COLORS["blue"][0], ui_fgcolor=COLORS["blue"][1])
    def train_model():
        get_training_data = GetTrainingDataOperator(task_id="get_training_data")
        train = TrainModelOperator(task_id="train", python_callable=train_and_score_model)
        chain(get_training_data, train)

    tear_down_gpu = TearDownGpuOperator(task_id="tear_down_gpu").as_teardown(setups=spin_up_gpu)

    check_freshness = CheckFreshnessOperator(task_id="check_freshness")
    run_quality_check = RunQualityCheckOperator.partial(task_id="run_quality_check").expand(
        bash_command=["echo nulls", "echo duplicates", "echo ranges"]
    )
    send_summary = SendSummaryOperator(task_id="send_summary")

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
        tear_down_gpu,
        end,
    )

    chain(preflight, check_freshness, run_quality_check, send_summary, end)


rainbow_dag_dark_mode()
