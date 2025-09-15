from airflow.sdk import dag, task, Asset
from airflow.timetables.assets import AssetOrTimeSchedule
from airflow.timetables.trigger import CronTriggerTimetable
from datetime import datetime
import random
import logging

t_log = logging.getLogger("airflow.task")


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
        return "Hello, World!"

    print_hello()

    @task
    def log_grouping():
        t_log.info("This is a log message")
        t_log.info("::group:: Outer group")
        t_log.info("This is a second log message")
        t_log.info("::group:: Inner group")
        t_log.info("This is a fourth log message")
        t_log.info("This is a fifth log message")
        t_log.info("::endgroup::")
        t_log.info("This is a sixth log message")
        t_log.info("This is a seventh log message")
        t_log.info("::endgroup::")

    log_grouping()

    @task
    def colorful_json_xcom():
        return {
            "name": "John Doe",
            "age": 30,
            "city": "New York",
            "likes": ["reading", "traveling", "coding"],
            "customer": True,
            "complaints": None
        }

    colorful_json_xcom()


ui_showcase_dag()
