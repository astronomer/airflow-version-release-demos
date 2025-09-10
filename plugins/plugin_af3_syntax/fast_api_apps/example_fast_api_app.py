"""
FastAPI App Plugin - Syntax Example

This plugin demonstrates how to create a standalone FastAPI application within Airflow 3.
Unlike external views, FastAPI apps are accessed directly via their URL prefix.

Key Features:
- Standalone REST API endpoints
- Auto-generated API documentation
- Static file serving
- Template rendering
- Direct URL access (no UI integration needed)
"""

from pathlib import Path
from typing import Dict, List
from airflow.plugins_manager import AirflowPlugin
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel


# ============================================================================
# 📁 File Structure Setup
# ============================================================================
PLUGIN_DIR = Path(__file__).parent 
TEMPLATES_DIR = PLUGIN_DIR / "templates"
STATIC_DIR = PLUGIN_DIR / "static"


# ============================================================================
# 🔧 FastAPI App Configuration
# ============================================================================
app = FastAPI(
    title="Airflow FastAPI App Example",
    description="A comprehensive example of FastAPI app integration in Airflow 3",
    version="1.0.0",
    docs_url="/docs",      # Auto-generated API docs at /your-prefix/docs
    redoc_url="/redoc"     # Alternative docs at /your-prefix/redoc
)


# ============================================================================
# 📊 Data Models (Pydantic)
# ============================================================================
class PluginInfo(BaseModel):
    name: str
    type: str
    status: str
    endpoints: List[str]

class UserMessage(BaseModel):
    message: str
    user_name: str = "Anonymous"


# ============================================================================
# 🛠️ Utility Functions
# ============================================================================
def load_template(template_name: str) -> str:
    """Load HTML template from file"""
    template_path = TEMPLATES_DIR / template_name
    if template_path.exists():
        return template_path.read_text(encoding='utf-8')
    return "<html><body><h1>Template not found</h1></body></html>"


# ============================================================================
# 🌐 API Endpoints
# ============================================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """
    Root endpoint - API information
    """
    return {
        "message": "🚀 Hello from FastAPI App Plugin!",
        "type": "standalone_fastapi_app",
        "documentation": "Visit /fastapi-app/docs for API documentation",
        "access": "Direct URL access (no UI integration required)"
    }


@app.get("/info", response_model=PluginInfo)
async def get_plugin_info():
    """
    Get detailed plugin information
    """
    return PluginInfo(
        name="FastAPI App Example",
        type="fastapi_app",
        status="active",
        endpoints=[
            "/",
            "/info", 
            "/hello",
            "/api/message",
            "/health",
            "/static/{file_name}",
            "/docs",
            "/redoc"
        ]
    )


@app.get("/hello")
async def hello_page():
    """
    Serve HTML page using template
    """
    html_content = load_template("hello.html")
    return HTMLResponse(content=html_content)


@app.post("/api/message", response_model=Dict[str, str])
async def post_message(user_message: UserMessage):
    """
    POST endpoint - Accept user messages
    """
    return {
        "status": "received",
        "message": f"Hello {user_message.user_name}! Your message: '{user_message.message}' was received.",
        "timestamp": "2024-01-01T12:00:00Z"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "fastapi-app-plugin"}


@app.get("/airflow-integration")
async def airflow_integration():
    """
    Example of Airflow integration - Get DAG count
    """
    try:
        from airflow.models import DagBag
        dagbag = DagBag()
        dag_count = len(dagbag.dags)
        
        return {
            "airflow_integration": "success",
            "total_dags": dag_count,
            "message": f"Found {dag_count} DAGs in this Airflow instance"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Airflow integration error: {str(e)}")


# ============================================================================
# 📁 Static File Serving
# ============================================================================
@app.get("/static/{file_name}")
async def serve_static_files(file_name: str):
    """
    Serve static CSS, JS, and other files
    """
    file_path = STATIC_DIR / file_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type
    if file_name.endswith('.css'):
        media_type = 'text/css'
    elif file_name.endswith('.js'):
        media_type = 'application/javascript'
    elif file_name.endswith('.png'):
        media_type = 'image/png'
    elif file_name.endswith('.jpg') or file_name.endswith('.jpeg'):
        media_type = 'image/jpeg'
    else:
        media_type = 'text/plain'
    
    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=file_name
    )


# ============================================================================
# 🔌 Plugin Registration
# ============================================================================
class FastAPIAppPlugin(AirflowPlugin):
    """
    Plugin that registers a standalone FastAPI application
    
    Key differences from External Views:
    - No 'external_views' - this is a standalone app
    - No 'url_route' - accessed directly via URL prefix
    - Full REST API capabilities (GET, POST, PUT, DELETE, etc.)
    - Auto-generated API documentation
    - Direct URL access: http://localhost:8080/fastapi-app/
    """
    
    name = "fastapi_app_example"
    
    # Register the FastAPI app
    fastapi_apps = [{
        "app": app,                           # The FastAPI application instance
        "url_prefix": "/fastapi-app",         # URL prefix for all endpoints
        "name": "FastAPI App Example"        # Display name
    }]
    
    # Note: No external_views needed - this is a standalone app!