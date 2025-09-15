from airflow.plugins_manager import AirflowPlugin
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from datetime import datetime
import json


# 📦 XCom Viewer Plugin - Display task XCom data in a beautiful interface
app = FastAPI(title="XCom Viewer Plugin", version="1.0.0")

# Get the plugin directory
PLUGIN_DIR = Path(__file__).parent / "xcom_viewer"

# Mount static files
app.mount("/static", StaticFiles(directory=str(PLUGIN_DIR / "static")), name="static")


@app.get("/")
async def root():
    """API info endpoint"""
    return {
        "plugin": "XCom Viewer",
        "description": "View XCom data for Airflow task instances",
        "version": "1.0.0",
        "endpoints": {
            "viewer": "/xcom-viewer/view/{dag_id}/{run_id}/{task_id}/{map_index}",
            "api": "/xcom-viewer/api/xcom/{dag_id}/{run_id}/{task_id}/{map_index}"
        }
    }


@app.get("/view/{dag_id}/{run_id}/{task_id}/{map_index}")
async def xcom_viewer_page(dag_id: str, run_id: str, task_id: str, map_index: str):
    """XCom Viewer Interface for specific task instance"""
    try:
        template_path = PLUGIN_DIR / "templates" / "xcom_viewer.html"
        with open(template_path, "r") as f:
            html_content = f.read()
        
        # Replace template variables
        html_content = html_content.replace("{{DAG_ID}}", dag_id)
        html_content = html_content.replace("{{RUN_ID}}", run_id)
        html_content = html_content.replace("{{TASK_ID}}", task_id)
        html_content = html_content.replace("{{MAP_INDEX}}", map_index)
        
        return HTMLResponse(content=html_content)
    except Exception as e:
        error_html = f"""
        <html><body>
        <h1>📦 XCom Viewer Error</h1>
        <p>Could not load XCom viewer: {str(e)}</p>
        <p><a href="javascript:location.reload()">🔄 Reload Page</a></p>
        </body></html>
        """
        return HTMLResponse(content=error_html)


@app.get("/api/xcom/{dag_id}/{run_id}/{task_id}/{map_index}")
async def get_xcom_data(dag_id: str, run_id: str, task_id: str, map_index: str):
    """Get XCom data for specific task instance using Airflow REST API"""
    try:
        import requests
        
        # Airflow API configuration
        _USERNAME = "admin"
        _PASSWORD = "admin" 
        _HOST = "http://localhost:8080"
        
        def get_jwt_token():
            token_url = f"{_HOST}/auth/token"
            payload = {"username": _USERNAME, "password": _PASSWORD}
            headers = {"Content-Type": "application/json"}
            response = requests.post(token_url, json=payload, headers=headers)
            return response.json().get("access_token")
        
        # Get JWT token
        token = get_jwt_token()
        auth_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Get XCom entries for this task instance
        xcom_url = f"{_HOST}/api/v1/dags/{dag_id}/dagRuns/{run_id}/taskInstances/{task_id}/xcomEntries"
        
        # Add map_index as query parameter only for mapped tasks (map_index >= 0)
        params = {}
        if map_index != "-1" and map_index.isdigit() and int(map_index) >= 0:
            params["map_index"] = int(map_index)
        
        # Debug logging
        print(f"XCom API URL: {xcom_url}")
        print(f"XCom API Params: {params}")
        
        xcom_response = requests.get(xcom_url, headers=auth_headers, params=params)
        
        if not xcom_response.ok:
            return JSONResponse(
                status_code=xcom_response.status_code,
                content={
                    "error": f"Failed to fetch XCom data: {xcom_response.status_code}",
                    "message": xcom_response.text,
                    "debug_info": {
                        "url": xcom_url,
                        "params": params,
                        "response_text": xcom_response.text
                    },
                    "task_info": {
                        "dag_id": dag_id,
                        "run_id": run_id,
                        "task_id": task_id,
                        "map_index": map_index
                    }
                }
            )
        
        xcom_data = xcom_response.json()
        
        # Process XCom entries for better display
        processed_xcoms = []
        xcom_entries = xcom_data.get("xcom_entries", [])
        
        for xcom in xcom_entries:
            # Get the actual XCom value
            xcom_key = xcom.get("key", "return_value")
            
            # Get the XCom value using the specific key endpoint
            value_url = f"{_HOST}/api/v1/dags/{dag_id}/dagRuns/{run_id}/taskInstances/{task_id}/xcomEntries/{xcom_key}"
            
            value_params = {}
            if map_index != "-1" and map_index.isdigit() and int(map_index) >= 0:
                value_params["map_index"] = int(map_index)
            
            value_response = requests.get(value_url, headers=auth_headers, params=value_params)
            
            xcom_value = None
            value_type = "unknown"
            value_size = 0
            
            if value_response.ok:
                try:
                    value_data = value_response.json()
                    xcom_value = value_data.get("value")
                    
                    # Determine value type and size
                    if xcom_value is not None:
                        if isinstance(xcom_value, dict):
                            value_type = "dict"
                            value_size = len(json.dumps(xcom_value))
                        elif isinstance(xcom_value, list):
                            value_type = "list"
                            value_size = len(json.dumps(xcom_value))
                        elif isinstance(xcom_value, str):
                            value_type = "string"
                            value_size = len(xcom_value)
                        elif isinstance(xcom_value, (int, float)):
                            value_type = "number"
                            value_size = len(str(xcom_value))
                        elif isinstance(xcom_value, bool):
                            value_type = "boolean"
                            value_size = len(str(xcom_value))
                        else:
                            value_type = type(xcom_value).__name__
                            value_size = len(str(xcom_value))
                
                except Exception as e:
                    xcom_value = f"Error parsing value: {str(e)}"
                    value_type = "error"
            
            processed_xcoms.append({
                "key": xcom_key,
                "value": xcom_value,
                "value_type": value_type,
                "value_size": value_size,
                "timestamp": xcom.get("timestamp"),
                "execution_date": xcom.get("execution_date"),
                "map_index": xcom.get("map_index", -1)
            })
        
        # Get task instance info for context
        task_info_url = f"{_HOST}/api/v1/dags/{dag_id}/dagRuns/{run_id}/taskInstances/{task_id}"
        task_info_response = requests.get(task_info_url, headers=auth_headers)
        
        task_info = {}
        if task_info_response.ok:
            task_info = task_info_response.json()
        
        result = {
            "task_info": {
                "dag_id": dag_id,
                "run_id": run_id,
                "task_id": task_id,
                "map_index": map_index,
                "state": task_info.get("state"),
                "start_date": task_info.get("start_date"),
                "end_date": task_info.get("end_date"),
                "operator": task_info.get("operator")
            },
            "xcom_entries": processed_xcoms,
            "total_entries": len(processed_xcoms),
            "timestamp": datetime.now().isoformat()
        }
        
        return result
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to retrieve XCom data: {str(e)}",
                "task_info": {
                    "dag_id": dag_id,
                    "run_id": run_id,
                    "task_id": task_id,
                    "map_index": map_index
                }
            }
        )


@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "xcom-viewer-plugin", 
        "capabilities": "📦 XCom data visualization"
    }


# # Plugin configuration - XCom Viewer
# class XComViewerPlugin(AirflowPlugin):
#     name = "xcom_viewer"
    
#     # FastAPI app for XCom viewing
#     fastapi_apps = [{
#         "app": app,
#         "url_prefix": "/xcom-viewer",
#         "name": "XCom Viewer Plugin"
#     }]
    
#     # External view - accessible from task instance pages
#     external_views = [{
#         "name": "📦 View XComs",
#         "href": "/xcom-viewer/view/{{DAG_ID}}/{{RUN_ID}}/{{TASK_ID}}/{{MAP_INDEX}}",
#         "destination": "task_instance",
#         "url_route": "xcom_viewer"
#     }]
