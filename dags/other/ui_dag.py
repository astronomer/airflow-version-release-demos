from airflow.sdk import dag, task_group, task, Param
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.sdk import Asset, Label, chain, chain_linear, dag, task, task_group
from airflow.providers.standard.operators.hitl import HITLOperator
from datetime import timedelta


@dag(
    schedule="@daily",
    params={
        "sleeptime": Param(
            "PT15M",
            type="string",
            format="duration",
            description="Enter ISO 8601 duration (e.g. PT15M, PT1H)",
        )
    },
    tags=["webinar"],
)
def ui_dag():

    start = EmptyOperator(task_id="start")

    sales_data_extract = BashOperator.partial(task_id="sales_data_extract").expand(
        bash_command=["echo 10", "echo 2", "echo 3", "echo 4"]
    )
    internal_api_extract = BashOperator.partial(task_id="internal_api_extract").expand(
        bash_command=["echo 1", "echo 2", "echo 3", "echo 4"]
    )

    @task.branch
    def determine_load_type() -> str:
        import random

        print("[orchestrator] load-strategy agent starting | model=claude-sonnet-5")
        print(
            "[orchestrator] context: source=internal_api partitions=4 "
            "last_sync=2026-07-01T00:00:00Z"
        )
        print(
            "[agent] tool_call inspect_schema_drift() -> drift_detected=true changed_ratio=0.42"
        )
        print("[agent] tokens: prompt=1284 completion=207 | latency=0.83s")

        if random.choice([True, False]):
            print(
                "[agent] decision=FULL reload | reason=schema drift above threshold "
                "| confidence=0.91"
            )
            return "internal_api_load_full"
        print(
            "[agent] decision=INCREMENTAL load | reason=append-only delta detected "
            "| confidence=0.87"
        )
        return "internal_api_load_incremental"

    sales_data_transform = EmptyOperator(task_id="sales_data_transform")

    determine_load_type_obj = determine_load_type()

    sales_data_load = HITLOperator(
        task_id="hitl_task",
        subject="Expense Approval Required",
        body="Review expense report and approve vendor payment method.",
        options=["ACH Transfer", "Wire Transfer", "Corporate Check", "CC"],
        defaults=["Wire Transfer"],
        multiple=False,
        params={
            "expense_amount": Param(
                10000,
                type="number",
            )
        },
        execution_timeout=timedelta(minutes=1),
    )
    internal_api_load_full = EmptyOperator(task_id="internal_api_load_full")
    internal_api_load_incremental = EmptyOperator(
        task_id="internal_api_load_incremental"
    )

    @task_group
    def sales_data_reporting(a):
        prepare_report = EmptyOperator(
            task_id="prepare_report", trigger_rule="all_done"
        )
        publish_report = EmptyOperator(task_id="publish_report")

        chain(prepare_report, publish_report)

    sales_data_reporting_obj = sales_data_reporting.expand(a=[1, 2, 3, 4, 5, 6])

    @task_group
    def cre_integration():

        cre_extract = EmptyOperator(task_id="cre_extract", trigger_rule="all_done")
        cre_transform = EmptyOperator(task_id="cre_transform")
        cre_load = EmptyOperator(task_id="cre_load")

        chain(cre_extract, cre_transform, cre_load)

    cre_integration_obj = cre_integration()

    @task_group
    def mlops():

        set_up_cluster = EmptyOperator(
            task_id="set_up_cluster", trigger_rule="all_done"
        )

        train_model = EmptyOperator(task_id="train_model")
        tear_down_cluster = EmptyOperator(task_id="tear_down_cluster")

        chain(set_up_cluster, train_model, tear_down_cluster)

        tear_down_cluster.as_teardown(setups=set_up_cluster)

    mlops_obj = mlops()

    end = EmptyOperator(task_id="end", outlets=[Asset("dag_completed")])

    chain(
        start,
        sales_data_extract,
        sales_data_transform,
        sales_data_load,
        [sales_data_reporting_obj, cre_integration_obj],
        end,
    )
    chain(
        start,
        internal_api_extract,
        determine_load_type_obj,
        [internal_api_load_full, internal_api_load_incremental],
        mlops_obj,
        end,
    )

    chain_linear(
        [sales_data_load, internal_api_load_full],
        [sales_data_reporting_obj, cre_integration_obj],
    )

    chain(
        determine_load_type_obj, Label("additional data"), internal_api_load_incremental
    )
    chain(
        determine_load_type_obj, Label("changed existing data"), internal_api_load_full
    )


ui_dag()
