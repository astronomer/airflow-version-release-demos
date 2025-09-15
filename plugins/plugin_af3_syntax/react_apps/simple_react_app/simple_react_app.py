from pathlib import Path
from airflow.plugins_manager import AirflowPlugin
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse

PLUGIN_DIR = Path(__file__).parent
app = FastAPI(title="Simple React App", version="1.0.0")


@app.get("/hello-world.js")
async def serve_react_component():
    js_file_path = PLUGIN_DIR / "hello-world.js"
    if js_file_path.exists():
        return FileResponse(
            path=str(js_file_path),
            media_type="application/javascript",
            filename="hello-world.js",
        )
    return HTMLResponse(content="// React component not found", status_code=404)


@app.get("/")
async def root():
    return {
        "message": "🌟 Simple React App Plugin",
        "type": "react_app",
        "component_url": "/simple-react/hello-world.js",
        "description": "Embeds a React component directly in Airflow UI",
    }


class SimpleReactAppPlugin(AirflowPlugin):

    name = "simple_react_app"

    fastapi_apps = [
        {"app": app, "url_prefix": "/simple-react", "name": "Simple React App"}
    ]

    react_apps = [
        {
            "name": "React Example Plugin",
            "bundle_url": "/simple-react/hello-world.js",
            "destination": "nav",
            "category": "browse",
            "url_route": "simple-react-app",
        }
    ]
