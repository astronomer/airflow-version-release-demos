from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from airflow.plugins_manager import AirflowPlugin

app = FastAPI()
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "page_context_static"), name="page_context")


class PageContextPlugin(AirflowPlugin):
    name = "page_context"
    fastapi_apps = [{"app": app, "url_prefix": "/page-context", "name": "Page context static files"}]
    react_apps = [
        {
            "name": "Page context",
            "bundle_url": "/page-context/static/page_context.js",
            "destination": "task_instance",
            "url_route": "page-context",
        },
    ]
