from airflow.plugins_manager import AirflowPlugin
from fastapi import FastAPI

app = FastAPI(title="Hello World FastAPI App", version="1.0.0")


@app.get("/hello")
async def hello_world():
    return {"message": "Hello from Airflow!"}


class FastAPIAppPlugin(AirflowPlugin):
    name = "hello_fastapi_app"

    fastapi_apps = [
        {"app": app, "url_prefix": "/hello-app", "name": "Hello World FastAPI App"}
    ]
