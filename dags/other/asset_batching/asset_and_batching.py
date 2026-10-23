from airflow.sdk import Asset, dag, task

asset_a = Asset("asset_and_batching_a")
asset_b = Asset("asset_and_batching_b")


@dag(tags=["asset_event_batching"])
def asset_and_batching_produce_a():

    @task(outlets=[asset_a])
    def produce_a():
        pass

    produce_a()


@dag(tags=["asset_event_batching"])
def asset_and_batching_produce_b():

    @task(outlets=[asset_b])
    def produce_b():
        pass

    produce_b()


@dag(schedule=(asset_a & asset_b), tags=["asset_event_batching"])
def asset_and_batching_consumer_expression():

    @task
    def consume(*, triggering_asset_events):
        for asset, events in triggering_asset_events.items():
            print(f"{asset.name}: {len(events)} event(s)")

    consume()


@dag(schedule=[asset_a, asset_b], tags=["asset_event_batching"])
def asset_and_batching_consumer_list():

    @task
    def consume(*, triggering_asset_events):
        for asset, events in triggering_asset_events.items():
            print(f"{asset.name}: {len(events)} event(s)")

    consume()


asset_and_batching_produce_a()
asset_and_batching_produce_b()
asset_and_batching_consumer_expression()
asset_and_batching_consumer_list()
