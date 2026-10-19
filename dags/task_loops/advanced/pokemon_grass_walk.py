import random

from airflow.sdk import dag, task, task_group

MAX_STEPS = 10

ROUTE_POKEMON = ["Caterpie", "Weedle", "Metapod", "Kakuna", "Pidgey"]


def pikachu_found(*, loop):
    """Stop the walk the moment we meet Pikachu."""
    return loop.result["found"]


@dag(
    params={"pikachu_luck": 0.35},
    tags=["task_loop", "webinar"],
)
def pokemon_grass_walk():

    @task
    def enter_forest():
        print("You step into the tall grass of Viridian Forest...")
        return {"seen": []}

    @task_group
    def search_grass(trip):
        @task
        def rustle_grass(trip, *, loop, params):
            previous = trip if loop.index == 0 else loop.previous
            wild = (
                "Pikachu"
                if random.random() < params["pikachu_luck"]
                else random.choice(ROUTE_POKEMON)
            )
            print(
                f"Step {loop.index + 1}: the grass rustles... a wild {wild} appeared!"
            )
            return {"seen": previous["seen"] + [wild], "wild": wild}

        @task
        def check_if_pikachu(encounter):
            found = encounter["wild"] == "Pikachu"
            print("It's Pikachu!" if found else "Not Pikachu, keep walking.")
            return {**encounter, "found": found}

        check_if_pikachu(rustle_grass(trip))

    @task(trigger_rule="all_done")
    def head_home(steps):
        last_step = steps[-1]
        if last_step["found"]:
            print(
                f"Caught Pikachu after {len(steps)} step(s)! Saw: {last_step['seen']}"
            )
        else:
            print(
                f"Walked {len(steps)} step(s), no Pikachu this time. Saw: {last_step['seen']}"
            )

    _enter_forest = enter_forest()

    _search_grass = search_grass.partial(trip=_enter_forest).loop(
        max_iterations=MAX_STEPS, until=pikachu_found
    )

    _head_home = head_home(_search_grass["check_if_pikachu"].output)


pokemon_grass_walk()
