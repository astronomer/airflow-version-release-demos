"""
React App Plugin - Simple Syntax Example

This plugin demonstrates how to create a React component that embeds in Airflow 3 UI.
React apps provide native UI integration with React components.

Key Features:
- Native React components in Airflow UI
- Direct embedding in specific UI locations  
- Access to React hooks and state management
- Professional UI integration (not iframes)

Key Differences from External Views:
- External Views: HTML pages (often in iframes)
- React Apps: Native React components embedded directly
"""

from pathlib import Path
from airflow.plugins_manager import AirflowPlugin
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse


# ============================================================================
# 📁 File Structure Setup  
# ============================================================================
PLUGIN_DIR = Path(__file__).parent


# ============================================================================
# 🌐 FastAPI App for Serving React Component
# ============================================================================
app = FastAPI(title="Simple React App", version="1.0.0")


@app.get("/hello-world.js")
async def serve_react_component():
    """
    Serve the React component JavaScript file.
    This file contains the actual React component code.
    """
    js_file_path = PLUGIN_DIR / "hello-world.js"
    if js_file_path.exists():
        return FileResponse(
            path=str(js_file_path),
            media_type="application/javascript",
            filename="hello-world.js"
        )
    return HTMLResponse(content="// React component not found", status_code=404)


@app.get("/")
async def root():
    """Basic info about this React app plugin"""
    return {
        "message": "🌟 Simple React App Plugin",
        "type": "react_app",
        "component_url": "/simple-react/hello-world.js",
        "description": "Embeds a React component directly in Airflow UI"
    }


# ============================================================================
# 🔌 Plugin Registration
# ============================================================================
class SimpleReactAppPlugin(AirflowPlugin):
    """
    Plugin that registers a React component for UI embedding.
    
    Key Concepts:
    - react_apps: List of React app configurations
    - bundle_url: URL to the JavaScript file containing React component
    - destination: Where to embed (nav, dashboard, dag, dag_run, task, task_instance)
    - Native UI integration (not iframes like external views)
    """
    
    name = "simple_react_app"
    
    # FastAPI app to serve the React component file
    fastapi_apps = [{
        "app": app,
        "url_prefix": "/simple-react",
        "name": "Simple React App"
    }]
    
    # React app configuration
    react_apps = [{
        "name": "React Example Plugin",           # Component name (becomes global variable)
        "bundle_url": "/simple-react/hello-world.js",  # URL to React component file
        "destination": "nav",                      # Navigation menu link
        "category": "browse",                      # Groups under Browse section
        "url_route": "simple-react-app"           # Creates dedicated page route
    }]
    
    # Note: The component will appear as a link in the Browse menu!


# ============================================================================
# 📝 Usage Instructions
# ============================================================================
"""
🚀 How This Works:

1. The fastapi_apps serves the React component JavaScript file
2. The react_apps tells Airflow to load that component
3. Airflow loads /simple-react/hello-world.js in the browser
4. The JavaScript file must create a global variable named "React Example Plugin"
5. Airflow finds that global variable and renders it as a React component

🌍 Where to See It:
- Look in the Browse menu for "React Example Plugin" link
- Click it to open a dedicated page with the React component
- It will appear as a native React app on its own page

🔧 Component Requirements:
- Must use React.createElement (no JSX compilation)
- Must set global variable: globalThis['React Example Plugin'] = YourComponent
- Can use React hooks (useState, useEffect, etc.)
- Has access to props passed by Airflow (dagId, runId, etc.)
"""
