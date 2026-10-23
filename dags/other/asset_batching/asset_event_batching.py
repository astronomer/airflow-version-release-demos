from airflow.sdk import Asset, AssetTriggeredTimetable, dag, task

my_asset = Asset("asset_event_batching_demo")


@dag(tags=["asset_event_batching"])
def asset_event_batching_producer():

    @task(outlets=[my_asset])
    def produce(number, *, outlet_events):
        outlet_events[my_asset].extra = {"number": number}

    produce.expand(number=[1, 2, 3])


@dag(schedule=my_asset, tags=["asset_event_batching"])
def asset_event_batching_per_event_consumer():

    @task
    def consume(*, triggering_asset_events):
        events = triggering_asset_events[my_asset]
        print(f"This run consumed {len(events)} event(s): {[e.extra for e in events]}")

    consume()


@dag(
    schedule=AssetTriggeredTimetable(assets=my_asset, batch_asset_events=True),
    tags=["asset_event_batching"],
)
def asset_event_batching_batched_consumer():

    @task
    def consume(*, triggering_asset_events):
        events = triggering_asset_events[my_asset]
        print(f"This run consumed {len(events)} event(s): {[e.extra for e in events]}")

    consume()


asset_event_batching_producer()
asset_event_batching_per_event_consumer()
asset_event_batching_batched_consumer()
