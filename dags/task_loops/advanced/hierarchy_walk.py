import json

from airflow.sdk import dag, task, task_group

MAX_LEVELS = 8

LEVEL_NAMES = [
    "company",
    "state",
    "location",
    "building",
    "floor",
    "unit",
    "asset",
    "subasset",
]


def hierarchy_ends(*, loop):
    """Stop once the level just populated has no child level."""
    return not loop.result["has_more"]


@dag(
    params={"depth": 4},
    tags=["task_loop"],
)
def hierarchy_walk():

    @task
    def seed(params):
        depth = int(params["depth"])
        print(f"This run walks {depth} level(s) (cap: {MAX_LEVELS})")
        return {"depth": depth, "path": []}

    @task_group
    def walk_level(start):
        @task
        def populate(start, *, loop):
            previous = start if loop.index == 0 else loop.previous
            name = LEVEL_NAMES[loop.index]
            path = previous["path"] + [name]
            node = {
                "level": loop.index,
                "name": name,
                "risk_score": round(0.1 * (loop.index + 1), 3),
            }
            print(f"Populating level {loop.index} ({name}), path: {' > '.join(path)}")
            return {"depth": previous["depth"], "path": path, "node": node}

        @task
        def decide(populated, *, loop):
            has_more = loop.index + 1 < populated["depth"]
            print(f"Level {loop.index}: has_more={has_more}")
            return {**populated, "has_more": has_more}

        decide(populate(start))

    @task
    def merge(levels):
        merged = {
            "levels_walked": len(levels),
            "hierarchy": [level["node"] for level in levels],
        }
        print("Final knowledge graph:\n" + json.dumps(merged, indent=2))
        return merged

    _seed = seed()

    _walk_level = walk_level.partial(start=_seed).loop(
        max_iterations=MAX_LEVELS, until=hierarchy_ends
    )

    _merge = merge(_walk_level["decide"].output)


hierarchy_walk()
