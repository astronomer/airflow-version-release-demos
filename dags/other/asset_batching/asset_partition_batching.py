from airflow.sdk import Asset, PartitionedAssetTimetable, StartOfDayMapper, dag, task

my_asset = Asset("asset_partition_batching_demo")


def _consume(dag_run, triggering_asset_events):
    events = triggering_asset_events[my_asset]
    keys = [e.partition_key for e in events]
    print(f"Run partition key {dag_run.partition_key} consumed {len(events)} event(s): {keys}")


@dag(tags=["asset_event_batching"])
def asset_partition_batching_producer():

    @task(outlets=[my_asset])
    def produce(*, outlet_events):
        outlet_events[my_asset].add_partitions(
            ["2026-10-21T01:00:00", "2026-10-21T02:00:00", "2026-10-22T01:00:00"]
        )

    produce()


@dag(
    schedule=PartitionedAssetTimetable(assets=my_asset, default_partition_mapper=StartOfDayMapper()),
    tags=["asset_event_batching"],
)
def asset_partition_batching_per_event_consumer():

    @task
    def consume(*, dag_run, triggering_asset_events):
        _consume(dag_run, triggering_asset_events)

    consume()


@dag(
    schedule=PartitionedAssetTimetable(
        assets=my_asset,
        default_partition_mapper=StartOfDayMapper(),
        batch_asset_events=True,
    ),
    tags=["asset_event_batching"],
)
def asset_partition_batching_batched_consumer():

    @task
    def consume(*, dag_run, triggering_asset_events):
        _consume(dag_run, triggering_asset_events)

    consume()


asset_partition_batching_producer()
asset_partition_batching_per_event_consumer()
asset_partition_batching_batched_consumer()
