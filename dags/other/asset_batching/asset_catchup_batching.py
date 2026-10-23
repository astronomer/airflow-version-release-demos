from pendulum import datetime

from airflow.sdk import Asset, AssetTriggeredTimetable, dag, task

my_asset = Asset("asset_catchup_batching_demo")


def _consume(triggering_asset_events):
    events = triggering_asset_events[my_asset]
    print(f"This run consumed {len(events)} event(s): {[e.extra for e in events]}")


@dag(tags=["asset_event_batching"])
def asset_catchup_batching_producer():

    @task(outlets=[my_asset])
    def produce(*, outlet_events, run_id):
        outlet_events[my_asset].extra = {"producer_run_id": run_id}

    produce()


@dag(schedule=my_asset, catchup=False, tags=["asset_event_batching"])
def asset_catchup_batching_catchup_false():

    @task
    def consume(*, triggering_asset_events):
        _consume(triggering_asset_events)

    consume()


@dag(
    schedule=my_asset,
    catchup=True,
    start_date=datetime(2026, 1, 1),
    tags=["asset_event_batching"],
)
def asset_catchup_batching_catchup_true():

    @task
    def consume(*, triggering_asset_events):
        _consume(triggering_asset_events)

    consume()


@dag(
    schedule=AssetTriggeredTimetable(assets=my_asset, batch_asset_events=True),
    catchup=True,
    start_date=datetime(2026, 1, 1),
    tags=["asset_event_batching"],
)
def asset_catchup_batching_catchup_true_batched():

    @task
    def consume(*, triggering_asset_events):
        _consume(triggering_asset_events)

    consume()


asset_catchup_batching_producer()
asset_catchup_batching_catchup_false()
asset_catchup_batching_catchup_true()
asset_catchup_batching_catchup_true_batched()
