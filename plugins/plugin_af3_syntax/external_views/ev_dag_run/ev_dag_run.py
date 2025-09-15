from pathlib import Path
from airflow.plugins_manager import AirflowPlugin
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse

PLUGIN_DIR = Path(__file__).parent 
TEMPLATES_DIR = PLUGIN_DIR / "templates"
STATIC_DIR = PLUGIN_DIR / "static"

app = FastAPI(title="DAG Run Hello World", version="1.0.0")


def load_template(template_name: str) -> str:
    """Load HTML template from file"""
    template_path = TEMPLATES_DIR / template_name
    if template_path.exists():
        return template_path.read_text(encoding='utf-8')
    return "<html><body><h1>Template not found</h1></body></html>"


@app.get("/hello/{dag_id}/{run_id}")
async def hello_dag_run(dag_id: str, run_id: str):
    """DAG Run specific Hello World page using separate HTML template"""
    html_content = load_template("hello.html")
    # Replace template variables
    html_content = html_content.replace("{{DAG_ID}}", dag_id)
    html_content = html_content.replace("{{RUN_ID}}", run_id)
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


# class DAGRunExternalViewPlugin(AirflowPlugin):
#     name = "dag_run_hello_world"
    
#     fastapi_apps = [{
#         "app": app,
#         "url_prefix": "/ev-dag-run-plugin",
#         "name": "External View - DAG Run"
#     }]

#     external_views = [{
#         "name": "Plugin Example - DAG Run",
#         "href": "/ev-dag-run-plugin/hello/{{DAG_ID}}/{{RUN_ID}}",
#         "destination": "dag_run",     
#         "url_route": "dag_run_plugin"  
#     }]
