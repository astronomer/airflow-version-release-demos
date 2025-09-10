# from airflow.plugins_manager import AirflowPlugin
# from fastapi import FastAPI
# from fastapi.responses import HTMLResponse
# from datetime import datetime


# # DAG Management FastAPI app - bulk pause/unpause operations!
# app = FastAPI(title="DAG Manager Plugin", version="1.0.0")


# @app.get("/")
# async def root():
#     return {
#         "message": "⚙️ DAG Manager Plugin - Bulk pause/unpause operations",
#         "timestamp": datetime.now().isoformat(),
#         "status": "running",
#         "endpoints": {
#             "dashboard": "/simple-plugin/dashboard",
#             "dags": "/simple-plugin/dags",
#             "pause_all": "/simple-plugin/pause-all",
#             "unpause_all": "/simple-plugin/unpause-all"
#         }
#     }


# @app.get("/health")
# async def health_check():
#     return {"status": "healthy", "service": "airflow-plugin"}


# @app.get("/dags")
# async def list_dags():
#     """Get DAG information with pause/unpause status"""
#     try:
#         from airflow.models import DagBag, DagModel
#         from airflow.utils.db import provide_session
        
#         @provide_session
#         def get_dag_info(session=None):
#             dagbag = DagBag()
#             dags_info = []
            
#             for dag_id, dag in dagbag.dags.items():
#                 # Get the DagModel to check is_paused status
#                 dag_model = session.query(DagModel).filter(DagModel.dag_id == dag_id).first()
#                 is_paused = dag_model.is_paused if dag_model else False
                
#                 dags_info.append({
#                     "dag_id": dag_id,
#                     "is_paused": is_paused,
#                     "description": dag.description or "No description"
#                 })
            
#             return dags_info
        
#         dags_info = get_dag_info()
#         total_dags = len(dags_info)
#         paused_dags = len([d for d in dags_info if d["is_paused"]])
#         active_dags = total_dags - paused_dags
        
#         return {
#             "total_dags": total_dags,
#             "active_dags": active_dags,
#             "paused_dags": paused_dags,
#             "dags": dags_info
#         }
#     except Exception as e:
#         return {"error": f"Could not fetch DAGs: {str(e)}"}


# @app.post("/pause-all")
# async def pause_all_dags():
#     """Pause all DAGs in the environment"""
#     try:
#         from airflow.models import DagBag, DagModel
#         from airflow.utils.db import provide_session
        
#         @provide_session
#         def pause_dags(session=None):
#             dagbag = DagBag()
#             paused_count = 0
            
#             for dag_id in dagbag.dags.keys():
#                 dag_model = session.query(DagModel).filter(DagModel.dag_id == dag_id).first()
#                 if dag_model and not dag_model.is_paused:
#                     dag_model.is_paused = True
#                     paused_count += 1
            
#             session.commit()
#             return paused_count
        
#         paused_count = pause_dags()
#         return {
#             "message": f"Successfully paused {paused_count} DAGs",
#             "paused_count": paused_count,
#             "status": "success"
#         }
#     except Exception as e:
#         return {"error": f"Failed to pause DAGs: {str(e)}", "status": "error"}


# @app.post("/unpause-all")
# async def unpause_all_dags():
#     """Unpause all DAGs in the environment"""
#     try:
#         from airflow.models import DagBag, DagModel
#         from airflow.utils.db import provide_session
        
#         @provide_session
#         def unpause_dags(session=None):
#             dagbag = DagBag()
#             unpaused_count = 0
            
#             for dag_id in dagbag.dags.keys():
#                 dag_model = session.query(DagModel).filter(DagModel.dag_id == dag_id).first()
#                 if dag_model and dag_model.is_paused:
#                     dag_model.is_paused = False
#                     unpaused_count += 1
            
#             session.commit()
#             return unpaused_count
        
#         unpaused_count = unpause_dags()
#         return {
#             "message": f"Successfully unpaused {unpaused_count} DAGs",
#             "unpaused_count": unpaused_count,
#             "status": "success"
#         }
#     except Exception as e:
#         return {"error": f"Failed to unpause DAGs: {str(e)}", "status": "error"}


# @app.get("/dashboard")
# async def dashboard():
#     """Interactive DAG Management Dashboard"""
#     try:
#         from airflow.models import DagBag, DagModel
#         from airflow.utils.db import provide_session
        
#         @provide_session
#         def get_dag_stats(session=None):
#             dagbag = DagBag()
#             total_dags = len(dagbag.dags)
#             paused_count = 0
            
#             for dag_id in dagbag.dags.keys():
#                 dag_model = session.query(DagModel).filter(DagModel.dag_id == dag_id).first()
#                 if dag_model and dag_model.is_paused:
#                     paused_count += 1
            
#             return total_dags, paused_count
        
#         # Get DAG statistics
#         total_dags, paused_dags = get_dag_stats()
#         active_dags = total_dags - paused_dags
        
#         # Interactive HTML dashboard with buttons
#         html_content = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <title>DAG Management Console</title>
#             <style>
#                 body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
#                 .card {{ background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
#                 .metric {{ display: inline-block; margin: 10px 20px; text-align: center; }}
#                 .metric-value {{ font-size: 2em; font-weight: bold; color: #1976d2; }}
#                 .metric-label {{ color: #666; }}
#                 .header {{ color: #333; border-bottom: 2px solid #1976d2; padding-bottom: 10px; }}
#                 .btn {{ padding: 12px 24px; margin: 10px; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; font-weight: bold; }}
#                 .btn-pause {{ background: #ff9800; color: white; }}
#                 .btn-unpause {{ background: #4caf50; color: white; }}
#                 .btn-refresh {{ background: #2196f3; color: white; }}
#                 .btn:hover {{ opacity: 0.8; }}
#                 .btn:disabled {{ background: #ccc; cursor: not-allowed; }}
#                 .status-message {{ padding: 15px; margin: 10px 0; border-radius: 6px; display: none; }}
#                 .success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
#                 .error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
#                 .dag-list {{ max-height: 300px; overflow-y: auto; }}
#                 .dag-item {{ margin: 5px 0; padding: 5px; }}
#                 .dag-active {{ color: #4caf50; }}
#                 .dag-paused {{ color: #ff9800; }}
#                 .loading {{ text-align: center; color: #666; }}
#             </style>
#         </head>
#         <body>
#             <h1 class="header">⚙️ DAG Management Console</h1>
            
#             <div id="statusMessage" class="status-message"></div>
            
#             <div class="card">
#                 <h2>📊 DAG Statistics</h2>
#                 <div class="metric">
#                     <div class="metric-value" id="totalDags">{total_dags}</div>
#                     <div class="metric-label">Total DAGs</div>
#                 </div>
#                 <div class="metric">
#                     <div class="metric-value" id="activeDags">{active_dags}</div>
#                     <div class="metric-label">🟢 Active DAGs</div>
#                 </div>
#                 <div class="metric">
#                     <div class="metric-value" id="pausedDags">{paused_dags}</div>
#                     <div class="metric-label">⏸️ Paused DAGs</div>
#                 </div>
#             </div>
            
#             <div class="card">
#                 <h2>🎛️ Bulk DAG Operations</h2>
#                 <p><strong>Warning:</strong> These operations affect ALL DAGs in your environment!</p>
#                 <button class="btn btn-pause" onclick="pauseAllDags()" id="pauseBtn">⏸️ Pause All DAGs</button>
#                 <button class="btn btn-unpause" onclick="unpauseAllDags()" id="unpauseBtn">▶️ Unpause All DAGs</button>
#                 <button class="btn btn-refresh" onclick="refreshData()" id="refreshBtn">🔄 Refresh Data</button>
#             </div>
            
#             <div class="card">
#                 <h2>📋 DAG Status</h2>
#                 <div id="dagList" class="dag-list">
#                     <div class="loading">Loading DAG list...</div>
#                 </div>
#             </div>
            
#             <script>
#                 async function showMessage(message, type) {{
#                     const msgEl = document.getElementById('statusMessage');
#                     msgEl.textContent = message;
#                     msgEl.className = `status-message ${{type}}`;
#                     msgEl.style.display = 'block';
#                     setTimeout(() => msgEl.style.display = 'none', 5000);
#                 }}
                
#                 async function pauseAllDags() {{
#                     const btn = document.getElementById('pauseBtn');
#                     btn.disabled = true;
#                     btn.textContent = '⏳ Pausing...';
                    
#                     try {{
#                         const response = await fetch('/simple-plugin/pause-all', {{ method: 'POST' }});
#                         const data = await response.json();
                        
#                         if (data.status === 'success') {{
#                             showMessage(`✅ ${{data.message}}`, 'success');
#                             refreshData();
#                         }} else {{
#                             showMessage(`❌ ${{data.error}}`, 'error');
#                         }}
#                     }} catch (error) {{
#                         showMessage(`❌ Network error: ${{error.message}}`, 'error');
#                     }} finally {{
#                         btn.disabled = false;
#                         btn.textContent = '⏸️ Pause All DAGs';
#                     }}
#                 }}
                
#                 async function unpauseAllDags() {{
#                     const btn = document.getElementById('unpauseBtn');
#                     btn.disabled = true;
#                     btn.textContent = '⏳ Unpausing...';
                    
#                     try {{
#                         const response = await fetch('/simple-plugin/unpause-all', {{ method: 'POST' }});
#                         const data = await response.json();
                        
#                         if (data.status === 'success') {{
#                             showMessage(`✅ ${{data.message}}`, 'success');
#                             refreshData();
#                         }} else {{
#                             showMessage(`❌ ${{data.error}}`, 'error');
#                         }}
#                     }} catch (error) {{
#                         showMessage(`❌ Network error: ${{error.message}}`, 'error');
#                     }} finally {{
#                         btn.disabled = false;
#                         btn.textContent = '▶️ Unpause All DAGs';
#                     }}
#                 }}
                
#                 async function refreshData() {{
#                     const btn = document.getElementById('refreshBtn');
#                     btn.disabled = true;
#                     btn.textContent = '🔄 Refreshing...';
                    
#                     try {{
#                         const response = await fetch('/simple-plugin/dags');
#                         const data = await response.json();
                        
#                         if (data.error) {{
#                             showMessage(`❌ ${{data.error}}`, 'error');
#                             return;
#                         }}
                        
#                         // Update metrics
#                         document.getElementById('totalDags').textContent = data.total_dags;
#                         document.getElementById('activeDags').textContent = data.active_dags;
#                         document.getElementById('pausedDags').textContent = data.paused_dags;
                        
#                         // Update DAG list
#                         const dagListEl = document.getElementById('dagList');
#                         if (data.dags && data.dags.length > 0) {{
#                             dagListEl.innerHTML = data.dags.map(dag => 
#                                 `<div class="dag-item">
#                                     <span class="${{dag.is_paused ? 'dag-paused' : 'dag-active'}}">
#                                         ${{dag.is_paused ? '⏸️' : '🟢'}}
#                                     </span>
#                                     <strong>${{dag.dag_id}}</strong>
#                                     <span style="color: #666;"> - ${{dag.description}}</span>
#                                 </div>`
#                             ).join('');
#                         }} else {{
#                             dagListEl.innerHTML = '<div class="loading">No DAGs found</div>';
#                         }}
                        
#                         showMessage('✅ Data refreshed successfully', 'success');
#                     }} catch (error) {{
#                         showMessage(`❌ Failed to refresh: ${{error.message}}`, 'error');
#                     }} finally {{
#                         btn.disabled = false;
#                         btn.textContent = '🔄 Refresh Data';
#                     }}
#                 }}
                
#                 // Load initial data
#                 refreshData();
#             </script>
#         </body>
#         </html>
#         """
        
#         return HTMLResponse(content=html_content)
        
#     except Exception as e:
#         error_html = f"""
#         <html><body>
#         <h1>⚠️ Dashboard Error</h1>
#         <p>Could not load dashboard: {str(e)}</p>
#         <p><a href="javascript:location.reload()">🔄 Reload Page</a></p>
#         </body></html>
#         """
#         return HTMLResponse(content=error_html)


# # Plugin configuration - self-contained, no external URLs
# app_config = {
#     "app": app,
#     "url_prefix": "/simple-plugin",
#     "name": "Simple Plugin"
# }

# # External view to show DAG management console in Airflow UI
# dag_management_view = {
#     "name": "DAG Manager",
#     "href": "/simple-plugin/dashboard",
#     "destination": "nav",  # Shows in navigation menu
#     "category": "admin",   # Put it in admin section since it's for management
#     "url_route": "dag-manager",  # Renders inside Airflow UI
# }


# class DAGManagerPlugin(AirflowPlugin):
#     name = "dag_manager"
#     fastapi_apps = [app_config]
#     external_views = [dag_management_view]