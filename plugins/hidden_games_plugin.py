from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from airflow.plugins_manager import AirflowPlugin

URL_PREFIX = "/hidden-games"
TAG = "scoped_plugin_example"

app = FastAPI()
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "hidden_games_static"), name="hidden_games")


class HiddenGamesPlugin(AirflowPlugin):
    name = "hidden_games"
    fastapi_apps = [{"app": app, "url_prefix": URL_PREFIX, "name": "Hidden games static files"}]
    react_apps = [
        {
            "name": "Tic-tac-toe",
            "bundle_url": f"{URL_PREFIX}/static/tic_tac_toe.js",
            "destination": "dag_overview",
            "applies_to": {"dag.tags.name": [TAG]},
        },
        {
            "name": "Minesweeper",
            "bundle_url": f"{URL_PREFIX}/static/minesweeper.js",
            "destination": "task_overview",
            "applies_to": {"dag.tags.name": [TAG], "task_id": ["minesweeper"]},
        },
        {
            "name": "Slitherlink",
            "bundle_url": f"{URL_PREFIX}/static/slitherlink.js",
            "destination": "task_overview",
            "applies_to": {"dag.tags.name": [TAG], "task_id": ["slitherlink"]},
        },
        {
            "name": "Battleships",
            "bundle_url": f"{URL_PREFIX}/static/battleships.js",
            "destination": "asset",
            "url_route": "battleships",
            "applies_to": {"name": ["the_high_seas"]},
        },
    ]
