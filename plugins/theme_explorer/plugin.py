from pathlib import Path
from airflow.plugins_manager import AirflowPlugin
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).parent

app = FastAPI(title="Theme Explorer")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


class ThemeExplorerPlugin(AirflowPlugin):
    name = "theme_explorer"

    fastapi_apps = [
        {"app": app, "url_prefix": "/theme-explorer", "name": "Theme Explorer"}
    ]

    react_apps = [
        {
            "name": "Theme Explorer",
            "bundle_url": "/theme-explorer/static/theme-explorer.js",
            "destination": "nav",
            "category": "browse",
            "url_route": "theme-explorer",
        }
    ]
