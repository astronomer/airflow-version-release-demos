"""
## Run types

Dag with a cron and an asset schedule, used for the Airflow UI screenshot that shows
the run type icons in the grid view: one scheduled, one manual, one backfill, and one
asset-triggered run.
"""

from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.timetables.assets import AssetOrTimeSchedule
from airflow.timetables.trigger import CronTriggerTimetable
from pendulum import datetime

from airflow.sdk import Asset, chain, dag, task_group


@dag(
    schedule=AssetOrTimeSchedule(
        timetable=CronTriggerTimetable("0 0 * * *", timezone="UTC"),
        assets=Asset("run_types_source"),
    ),
    start_date=datetime(2026, 10, 22),
    catchup=True,
    tags=["ui_features"],
)
def run_types():
    start = EmptyOperator(task_id="start")

    @task_group
    def extract():
        BashOperator(task_id="extract_orders", bash_command="sleep 4")
        BashOperator(task_id="extract_customers", bash_command="sleep 2")

    @task_group
    def transform():
        clean = BashOperator(task_id="clean", bash_command="sleep 3")
        join = BashOperator(task_id="join", bash_command="sleep 2")
        chain(clean, join)

    load = BashOperator(task_id="load", bash_command="sleep 3")
    report = EmptyOperator(task_id="report")
    end = EmptyOperator(task_id="end")

    chain(start, extract(), transform(), load, report, end)


run_types()
