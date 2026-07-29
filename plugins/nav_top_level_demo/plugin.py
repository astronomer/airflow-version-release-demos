from pathlib import Path

from airflow.plugins_manager import AirflowPlugin
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

BASE_DIR = Path(__file__).parent

app = FastAPI(title="Nav Top Level Demo")


@app.get("/hello", response_class=HTMLResponse)
async def hello():
    return "<h1>Hello world!</h1>"


# class NavTopLevelDemoPlugin(AirflowPlugin):
#     name = "nav_top_level_demo"

#     fastapi_apps = [
#         {
#             "app": app,
#             "url_prefix": "/nav-top-level-demo",
#             "name": "My Plugin",
#         }
#     ]

#     external_views = [
#         {
#             "name": "My Plugin",
#             "href": "nav-top-level-demo/hello",
#             "destination": "nav",
#             "url_route": "nav-top-level-demo-promoted",
#             "nav_top_level": True, 
#         }
#     ]
