from airflow.sdk import (
    Asset,
    AssetAndTimeSchedule,
    AssetOrTimeSchedule,
    CronTriggerTimetable,
    dag,
    task,
)
from pendulum import datetime

orders = Asset("asset_and_time_orders")
customers = Asset("asset_and_time_customers")


@dag(tags=["asset_and_time_schedule"])
def asset_and_time_update_orders():

    @task(outlets=[orders])
    def update_orders():
        pass

    update_orders()


@dag(tags=["asset_and_time_schedule"])
def asset_and_time_update_customers():

    @task(outlets=[customers])
    def update_customers():
        pass

    update_customers()


@dag(
    start_date=datetime(2026, 10, 1),
    schedule=AssetAndTimeSchedule(
        timetable=CronTriggerTimetable("*/5 * * * *", timezone="UTC"),
        assets=(orders & customers),
    ),
    tags=["asset_and_time_schedule"],
)
def asset_and_time_report():

    @task
    def build_report(*, triggering_asset_events):
        for asset, events in triggering_asset_events.items():
            print(f"{asset.name}: {len(events)} event(s)")

    build_report()


@dag(
    start_date=datetime(2026, 10, 1),
    schedule=AssetOrTimeSchedule(
        timetable=CronTriggerTimetable("*/5 * * * *", timezone="UTC"),
        assets=(orders & customers),
    ),
    tags=["asset_and_time_schedule"],
)
def asset_or_time_report():

    @task
    def build_report(*, triggering_asset_events):
        for asset, events in triggering_asset_events.items():
            print(f"{asset.name}: {len(events)} event(s)")

    build_report()


asset_and_time_update_orders()
asset_and_time_update_customers()
asset_and_time_report()
asset_or_time_report()
