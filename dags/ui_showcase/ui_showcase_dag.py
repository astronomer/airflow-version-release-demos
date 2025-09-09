from airflow.sdk import dag, task, Asset
from airflow.timetables.assets import AssetOrTimeSchedule
from airflow.timetables.trigger import CronTriggerTimetable
from datetime import datetime
import random


@dag(
    start_date=datetime(2025, 1, 1),
    schedule=AssetOrTimeSchedule(
        timetable=CronTriggerTimetable("7 7,11,15,19,23 * * *", timezone="UTC"),
        assets=[Asset("trigger_ui_showcase_dag")],
    ),
)
def ui_showcase_dag():
    @task
    def print_hello():
        # fail randomly once every 10 runs
        if random.random() < 0.1:
            raise Exception("Random failure")
        print("Hello, World!")

    print_hello()


ui_showcase_dag()
