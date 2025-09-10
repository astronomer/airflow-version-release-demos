"""
External View Plugin - Task Instance

This plugin adds a link to individual task instance pages. 
It opens a separate page with task instance specific information.
"""

from pathlib import Path
from airflow.plugins_manager import AirflowPlugin
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse

PLUGIN_DIR = Path(__file__).parent 
TEMPLATES_DIR = PLUGIN_DIR / "templates"
STATIC_DIR = PLUGIN_DIR / "static"

app = FastAPI(title="Task Instance Hello World", version="1.0.0")


def load_template(template_name: str) -> str:
    """Load HTML template from file"""
    template_path = TEMPLATES_DIR / template_name
    if template_path.exists():
        return template_path.read_text(encoding='utf-8')
    return "<html><body><h1>Template not found</h1></body></html>"


@app.get("/hello/{dag_id}/{run_id}/{task_id}/{map_index}")
async def hello_task_instance(dag_id: str, run_id: str, task_id: str, map_index: str):
    """Task Instance specific Hello World page using separate HTML template"""
    html_content = load_template("hello.html")
    # Replace template variables
    html_content = html_content.replace("{{DAG_ID}}", dag_id)
    html_content = html_content.replace("{{RUN_ID}}", run_id)
    html_content = html_content.replace("{{TASK_ID}}", task_id)
    html_content = html_content.replace("{{MAP_INDEX}}", map_index)
    return HTMLResponse(content=html_content)


@app.get("/static/{file_name}")
async def serve_static_files(file_name: str):
    """Serve static CSS and JS files"""
    file_path = STATIC_DIR / file_name
    if file_path.exists():
        # Determine media type based on file extension
        if file_name.endswith('.css'):
            media_type = 'text/css'
        elif file_name.endswith('.js'):
            media_type = 'application/javascript'
        else:
            media_type = 'text/plain'
        
        return FileResponse(
            path=str(file_path),
            media_type=media_type,
            filename=file_name
        )
    return HTMLResponse(content="File not found", status_code=404)


class TaskInstanceExternalViewPlugin(AirflowPlugin):
    name = "task_instance_hello_world"
    
    fastapi_apps = [{
        "app": app,
        "url_prefix": "/ev-task-instance-plugin",
        "name": "External View - Task Instance"
    }]

    external_views = [{
        "name": "Plugin Example - Task Instance",
        "href": "/ev-task-instance-plugin/hello/{{DAG_ID}}/{{RUN_ID}}/{{TASK_ID}}/{{MAP_INDEX}}",
        "destination": "task_instance",     # This puts it on individual task instance pages
        "url_route": "task_instance_plugin"  # Makes it appear in UI
    }]
