"""
Simple DAG External View Plugin - Hello World
This demonstrates adding a basic link to individual DAG pages.
"""

from airflow.plugins_manager import AirflowPlugin
from fastapi import FastAPI
from fastapi.responses import HTMLResponse


# Simple FastAPI app
app = FastAPI(title="DAG Hello World", version="1.0.0")


@app.get("/hello/{dag_id}")
async def hello_dag(dag_id: str):
    """Simple Hello World page for DAG-level demonstration"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hello World - DAG Level</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                margin: 40px; 
                background: #f5f5f5; 
                text-align: center;
            }}
            .container {{ 
                max-width: 600px; 
                margin: 0 auto; 
                background: white; 
                padding: 40px; 
                border-radius: 8px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .btn {{
                background: #28a745;
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 5px;
                font-size: 18px;
                cursor: pointer;
                margin: 20px;
            }}
            .btn:hover {{ background: #1e7e34; }}
            .dag-id {{
                background: #e9ecef;
                padding: 10px;
                border-radius: 5px;
                font-family: monospace;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚁 Hello World from DAG Page!</h1>
            <p>This external view is specific to the DAG you're viewing.</p>
            <div class="dag-id">DAG ID: <strong>{dag_id}</strong></div>
            <button class="btn" onclick="alert('Hello from DAG: {dag_id}!')">
                👋 Hello from {dag_id}!
            </button>
            <p><small>Location: <strong>Individual DAG Page</strong></small></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


class DAGExternalViewPlugin(AirflowPlugin):
    """Simple plugin that adds a Hello World link to DAG pages."""
    
    name = "dag_hello_world"
    
    # FastAPI app configuration
    fastapi_apps = [{
        "app": app,
        "url_prefix": "/dag-plugin",
        "name": "DAG Hello World"
    }]
    
    # External view that appears on DAG pages
    external_views = [{
        "name": "Hello World (DAG)",
        "href": "/dag-plugin/hello/{{DAG_ID}}",  # Template uses DAG_ID
        "destination": "dag"  # This puts it on individual DAG pages
    }]
