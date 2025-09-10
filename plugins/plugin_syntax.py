from airflow.plugins_manager import AirflowPlugin
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime


# DAG Management FastAPI app - bulk pause/unpause operations!
app = FastAPI(title="DAG Manager Plugin", version="1.0.0")


@app.get("/")
async def root():
    return {
        "message": "⚙️ DAG Manager Plugin - Bulk pause/unpause operations",
        "timestamp": datetime.now().isoformat(),
        "status": "running",
        "endpoints": {
            "dashboard": "/simple-plugin/dashboard",
            "dags": "/simple-plugin/dags",
            "pause_all": "/simple-plugin/pause-all",
            "unpause_all": "/simple-plugin/unpause-all"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "airflow-plugin"}


@app.get("/dags")
async def list_dags():
    """Get DAG information with pause/unpause status"""
    try:
        from airflow.models import DagBag, DagModel
        from airflow.utils.db import provide_session
        
        @provide_session
        def get_dag_info(session=None):
            dagbag = DagBag()
            dags_info = []
            
            for dag_id, dag in dagbag.dags.items():
                # Get the DagModel to check is_paused status
                dag_model = session.query(DagModel).filter(DagModel.dag_id == dag_id).first()
                is_paused = dag_model.is_paused if dag_model else False
                
                dags_info.append({
                    "dag_id": dag_id,
                    "is_paused": is_paused,
                    "description": dag.description or "No description"
                })
            
            return dags_info
        
        dags_info = get_dag_info()
        total_dags = len(dags_info)
        paused_dags = len([d for d in dags_info if d["is_paused"]])
        active_dags = total_dags - paused_dags
        
        return {
            "total_dags": total_dags,
            "active_dags": active_dags,
            "paused_dags": paused_dags,
            "dags": dags_info
        }
    except Exception as e:
        return {"error": f"Could not fetch DAGs: {str(e)}"}


@app.post("/pause-all")
async def pause_all_dags():
    """Pause all DAGs in the environment"""
    try:
        from airflow.models import DagBag, DagModel
        from airflow.utils.db import provide_session
        
        @provide_session
        def pause_dags(session=None):
            dagbag = DagBag()
            paused_count = 0
            
            for dag_id in dagbag.dags.keys():
                dag_model = session.query(DagModel).filter(DagModel.dag_id == dag_id).first()
                if dag_model and not dag_model.is_paused:
                    dag_model.is_paused = True
                    paused_count += 1
            
            session.commit()
            return paused_count
        
        paused_count = pause_dags()
        return {
            "message": f"Successfully paused {paused_count} DAGs",
            "paused_count": paused_count,
            "status": "success"
        }
    except Exception as e:
        return {"error": f"Failed to pause DAGs: {str(e)}", "status": "error"}


@app.post("/unpause-all")
async def unpause_all_dags():
    """Unpause all DAGs in the environment"""
    try:
        from airflow.models import DagBag, DagModel
        from airflow.utils.db import provide_session
        
        @provide_session
        def unpause_dags(session=None):
            dagbag = DagBag()
            unpaused_count = 0
            
            for dag_id in dagbag.dags.keys():
                dag_model = session.query(DagModel).filter(DagModel.dag_id == dag_id).first()
                if dag_model and dag_model.is_paused:
                    dag_model.is_paused = False
                    unpaused_count += 1
            
            session.commit()
            return unpaused_count
        
        unpaused_count = unpause_dags()
        return {
            "message": f"Successfully unpaused {unpaused_count} DAGs",
            "unpaused_count": unpaused_count,
            "status": "success"
        }
    except Exception as e:
        return {"error": f"Failed to unpause DAGs: {str(e)}", "status": "error"}


@app.get("/dashboard")
async def dashboard():
    """Interactive DAG Management Dashboard"""
    try:
        from airflow.models import DagBag, DagModel
        from airflow.utils.db import provide_session
        
        @provide_session
        def get_dag_stats(session=None):
            dagbag = DagBag()
            total_dags = len(dagbag.dags)
            paused_count = 0
            
            for dag_id in dagbag.dags.keys():
                dag_model = session.query(DagModel).filter(DagModel.dag_id == dag_id).first()
                if dag_model and dag_model.is_paused:
                    paused_count += 1
            
            return total_dags, paused_count
        
        # Get DAG statistics
        total_dags, paused_dags = get_dag_stats()
        active_dags = total_dags - paused_dags
        
        # Interactive HTML dashboard with buttons
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>DAG Management Console</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .card {{ background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .metric {{ display: inline-block; margin: 10px 20px; text-align: center; }}
                .metric-value {{ font-size: 2em; font-weight: bold; color: #1976d2; }}
                .metric-label {{ color: #666; }}
                .header {{ color: #333; border-bottom: 2px solid #1976d2; padding-bottom: 10px; }}
                .btn {{ padding: 12px 24px; margin: 10px; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; font-weight: bold; }}
                .btn-pause {{ background: #ff9800; color: white; }}
                .btn-unpause {{ background: #4caf50; color: white; }}
                .btn-refresh {{ background: #2196f3; color: white; }}
                .btn:hover {{ opacity: 0.8; }}
                .btn:disabled {{ background: #ccc; cursor: not-allowed; }}
                .status-message {{ padding: 15px; margin: 10px 0; border-radius: 6px; display: none; }}
                .success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
                .error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
                .dag-list {{ max-height: 300px; overflow-y: auto; }}
                .dag-item {{ margin: 5px 0; padding: 5px; }}
                .dag-active {{ color: #4caf50; }}
                .dag-paused {{ color: #ff9800; }}
                .loading {{ text-align: center; color: #666; }}
            </style>
        </head>
        <body>
            <h1 class="header">⚙️ DAG Management Console</h1>
            
            <div id="statusMessage" class="status-message"></div>
            
            <div class="card">
                <h2>📊 DAG Statistics</h2>
                <div class="metric">
                    <div class="metric-value" id="totalDags">{total_dags}</div>
                    <div class="metric-label">Total DAGs</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="activeDags">{active_dags}</div>
                    <div class="metric-label">🟢 Active DAGs</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="pausedDags">{paused_dags}</div>
                    <div class="metric-label">⏸️ Paused DAGs</div>
                </div>
            </div>
            
            <div class="card">
                <h2>🎛️ Bulk DAG Operations</h2>
                <p><strong>Warning:</strong> These operations affect ALL DAGs in your environment!</p>
                <button class="btn btn-pause" onclick="pauseAllDags()" id="pauseBtn">⏸️ Pause All DAGs</button>
                <button class="btn btn-unpause" onclick="unpauseAllDags()" id="unpauseBtn">▶️ Unpause All DAGs</button>
                <button class="btn btn-refresh" onclick="refreshData()" id="refreshBtn">🔄 Refresh Data</button>
            </div>
            
            <div class="card">
                <h2>📋 DAG Status</h2>
                <div id="dagList" class="dag-list">
                    <div class="loading">Loading DAG list...</div>
                </div>
            </div>
            
            <script>
                async function showMessage(message, type) {{
                    const msgEl = document.getElementById('statusMessage');
                    msgEl.textContent = message;
                    msgEl.className = `status-message ${{type}}`;
                    msgEl.style.display = 'block';
                    setTimeout(() => msgEl.style.display = 'none', 5000);
                }}
                
                async function pauseAllDags() {{
                    const btn = document.getElementById('pauseBtn');
                    btn.disabled = true;
                    btn.textContent = '⏳ Pausing...';
                    
                    try {{
                        const response = await fetch('/simple-plugin/pause-all', {{ method: 'POST' }});
                        const data = await response.json();
                        
                        if (data.status === 'success') {{
                            showMessage(`✅ ${{data.message}}`, 'success');
                            refreshData();
                        }} else {{
                            showMessage(`❌ ${{data.error}}`, 'error');
                        }}
                    }} catch (error) {{
                        showMessage(`❌ Network error: ${{error.message}}`, 'error');
                    }} finally {{
                        btn.disabled = false;
                        btn.textContent = '⏸️ Pause All DAGs';
                    }}
                }}
                
                async function unpauseAllDags() {{
                    const btn = document.getElementById('unpauseBtn');
                    btn.disabled = true;
                    btn.textContent = '⏳ Unpausing...';
                    
                    try {{
                        const response = await fetch('/simple-plugin/unpause-all', {{ method: 'POST' }});
                        const data = await response.json();
                        
                        if (data.status === 'success') {{
                            showMessage(`✅ ${{data.message}}`, 'success');
                            refreshData();
                        }} else {{
                            showMessage(`❌ ${{data.error}}`, 'error');
                        }}
                    }} catch (error) {{
                        showMessage(`❌ Network error: ${{error.message}}`, 'error');
                    }} finally {{
                        btn.disabled = false;
                        btn.textContent = '▶️ Unpause All DAGs';
                    }}
                }}
                
                async function refreshData() {{
                    const btn = document.getElementById('refreshBtn');
                    btn.disabled = true;
                    btn.textContent = '🔄 Refreshing...';
                    
                    try {{
                        const response = await fetch('/simple-plugin/dags');
                        const data = await response.json();
                        
                        if (data.error) {{
                            showMessage(`❌ ${{data.error}}`, 'error');
                            return;
                        }}
                        
                        // Update metrics
                        document.getElementById('totalDags').textContent = data.total_dags;
                        document.getElementById('activeDags').textContent = data.active_dags;
                        document.getElementById('pausedDags').textContent = data.paused_dags;
                        
                        // Update DAG list
                        const dagListEl = document.getElementById('dagList');
                        if (data.dags && data.dags.length > 0) {{
                            dagListEl.innerHTML = data.dags.map(dag => 
                                `<div class="dag-item">
                                    <span class="${{dag.is_paused ? 'dag-paused' : 'dag-active'}}">
                                        ${{dag.is_paused ? '⏸️' : '🟢'}}
                                    </span>
                                    <strong>${{dag.dag_id}}</strong>
                                    <span style="color: #666;"> - ${{dag.description}}</span>
                                </div>`
                            ).join('');
                        }} else {{
                            dagListEl.innerHTML = '<div class="loading">No DAGs found</div>';
                        }}
                        
                        showMessage('✅ Data refreshed successfully', 'success');
                    }} catch (error) {{
                        showMessage(`❌ Failed to refresh: ${{error.message}}`, 'error');
                    }} finally {{
                        btn.disabled = false;
                        btn.textContent = '🔄 Refresh Data';
                    }}
                }}
                
                // Load initial data
                refreshData();
            </script>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        error_html = f"""
        <html><body>
        <h1>⚠️ Dashboard Error</h1>
        <p>Could not load dashboard: {str(e)}</p>
        <p><a href="javascript:location.reload()">🔄 Reload Page</a></p>
        </body></html>
        """
        return HTMLResponse(content=error_html)


@app.get("/widget")
async def dashboard_widget():
    """Compact DAG management widget for embedding in the main dashboard"""
    try:
        from airflow.models import DagBag, DagModel
        from airflow.utils.db import provide_session
        
        @provide_session
        def get_dag_stats(session=None):
            dagbag = DagBag()
            total_dags = len(dagbag.dags)
            paused_count = 0
            
            for dag_id in dagbag.dags.keys():
                dag_model = session.query(DagModel).filter(DagModel.dag_id == dag_id).first()
                if dag_model and dag_model.is_paused:
                    paused_count += 1
            
            return total_dags, paused_count
        
        # Get DAG statistics
        total_dags, paused_dags = get_dag_stats()
        active_dags = total_dags - paused_dags
        
        # Compact widget HTML optimized for dashboard embedding
        widget_html = f"""
        <div style="background: white; border-radius: 8px; padding: 15px; margin: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); min-width: 300px;">
            <h3 style="margin: 0 0 10px 0; color: #333; font-size: 16px;">⚙️ DAG Bulk Operations</h3>
            
            <div style="display: flex; gap: 15px; margin-bottom: 15px; font-size: 14px;">
                <div style="text-align: center;">
                    <div style="font-weight: bold; color: #1976d2; font-size: 18px;">{total_dags}</div>
                    <div style="color: #666;">Total</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-weight: bold; color: #4caf50; font-size: 18px;">{active_dags}</div>
                    <div style="color: #666;">Active</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-weight: bold; color: #ff9800; font-size: 18px;">{paused_dags}</div>
                    <div style="color: #666;">Paused</div>
                </div>
            </div>
            
            <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                <button onclick="bulkPause()" style="flex: 1; padding: 8px; background: #ff9800; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px;">
                    ⏸️ Pause All
                </button>
                <button onclick="bulkUnpause()" style="flex: 1; padding: 8px; background: #4caf50; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px;">
                    ▶️ Unpause All
                </button>
            </div>
            
            <div id="widgetStatus" style="padding: 5px; border-radius: 4px; font-size: 12px; text-align: center; display: none;"></div>
            
            <div style="text-align: center; margin-top: 10px;">
                <a href="/simple-plugin/dashboard" target="_blank" style="color: #1976d2; text-decoration: none; font-size: 12px;">
                    🔗 Open Full Manager
                </a>
            </div>
        </div>
        
        <script>
            function showWidgetMessage(message, type) {{
                const statusEl = document.getElementById('widgetStatus');
                statusEl.textContent = message;
                statusEl.style.display = 'block';
                statusEl.style.background = type === 'success' ? '#d4edda' : '#f8d7da';
                statusEl.style.color = type === 'success' ? '#155724' : '#721c24';
                setTimeout(() => statusEl.style.display = 'none', 3000);
            }}
            
            async function bulkPause() {{
                try {{
                    const response = await fetch('/simple-plugin/pause-all', {{ method: 'POST' }});
                    const data = await response.json();
                    if (data.status === 'success') {{
                        showWidgetMessage(`✅ Paused ${{data.paused_count}} DAGs`, 'success');
                        setTimeout(() => window.location.reload(), 1500);
                    }} else {{
                        showWidgetMessage(`❌ ${{data.error}}`, 'error');
                    }}
                }} catch (error) {{
                    showWidgetMessage(`❌ Error: ${{error.message}}`, 'error');
                }}
            }}
            
            async function bulkUnpause() {{
                try {{
                    const response = await fetch('/simple-plugin/unpause-all', {{ method: 'POST' }});
                    const data = await response.json();
                    if (data.status === 'success') {{
                        showWidgetMessage(`✅ Unpaused ${{data.unpaused_count}} DAGs`, 'success');
                        setTimeout(() => window.location.reload(), 1500);
                    }} else {{
                        showWidgetMessage(`❌ ${{data.error}}`, 'error');
                    }}
                }} catch (error) {{
                    showWidgetMessage(`❌ Error: ${{error.message}}`, 'error');
                }}
            }}
        </script>
        """
        
        return HTMLResponse(content=widget_html)
        
    except Exception as e:
        error_widget = f"""
        <div style="background: #f8d7da; color: #721c24; padding: 10px; border-radius: 4px; margin: 10px;">
            <strong>Widget Error:</strong> {str(e)}
        </div>
        """
        return HTMLResponse(content=error_widget)


@app.get("/hello.js")
async def hello_world_component():
    """Simple React component for dashboard embedding"""
    js_content = """
// DAG Management Dashboard Widget for Airflow
console.log('Setting up DAG Management Widget for Airflow...');

function DAGManagerWidget(props) {
    console.log('DAGManagerWidget called with props:', props);
    
    const [dagStats, setDagStats] = React.useState({ total: 0, active: 0, paused: 0 });
    const [loading, setLoading] = React.useState({ pause: false, unpause: false });
    const [message, setMessage] = React.useState({ text: '', type: '' });
    
    // Load DAG statistics
    React.useEffect(() => {
        fetch('/simple-plugin/dags')
            .then(response => response.json())
            .then(data => {
                if (!data.error) {
                    setDagStats({
                        total: data.total_dags || 0,
                        active: data.active_dags || 0,
                        paused: data.paused_dags || 0
                    });
                }
            })
            .catch(error => console.error('Error loading DAG stats:', error));
    }, []);
    
    const showMessage = (text, type) => {
        setMessage({ text, type });
        setTimeout(() => setMessage({ text: '', type: '' }), 3000);
    };
    
    const pauseAllDAGs = async () => {
        setLoading({ ...loading, pause: true });
        try {
            const response = await fetch('/simple-plugin/pause-all', { method: 'POST' });
            const data = await response.json();
            if (data.status === 'success') {
                showMessage(`✅ Paused ${data.paused_count} DAGs`, 'success');
                setDagStats(prev => ({ ...prev, paused: prev.total, active: 0 }));
            } else {
                showMessage(`❌ ${data.error}`, 'error');
            }
        } catch (error) {
            showMessage(`❌ Error: ${error.message}`, 'error');
        } finally {
            setLoading({ ...loading, pause: false });
        }
    };
    
    const unpauseAllDAGs = async () => {
        setLoading({ ...loading, unpause: true });
        try {
            const response = await fetch('/simple-plugin/unpause-all', { method: 'POST' });
            const data = await response.json();
            if (data.status === 'success') {
                showMessage(`✅ Unpaused ${data.unpaused_count} DAGs`, 'success');
                setDagStats(prev => ({ ...prev, active: prev.total, paused: 0 }));
            } else {
                showMessage(`❌ ${data.error}`, 'error');
            }
        } catch (error) {
            showMessage(`❌ Error: ${error.message}`, 'error');
        } finally {
            setLoading({ ...loading, unpause: false });
        }
    };
    
    return React.createElement('div', {
        style: {
            background: 'white',
            border: '1px solid #d1d5db',
            borderRadius: '8px',
            padding: '15px',
            margin: '10px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            fontFamily: 'system-ui, -apple-system, sans-serif'
        }
    }, [
        // Header
        React.createElement('h3', {
            key: 'header',
            style: {
                margin: '0 0 15px 0',
                color: '#374151',
                fontSize: '16px',
                fontWeight: '600'
            }
        }, '⚙️ DAG Bulk Operations'),
        
        // Statistics
        React.createElement('div', {
            key: 'stats',
            style: {
                display: 'flex',
                gap: '20px',
                marginBottom: '15px',
                fontSize: '14px'
            }
        }, [
            React.createElement('div', {
                key: 'total',
                style: { textAlign: 'center' }
            }, [
                React.createElement('div', {
                    key: 'total-value',
                    style: { fontWeight: 'bold', color: '#1976d2', fontSize: '18px' }
                }, dagStats.total),
                React.createElement('div', {
                    key: 'total-label',
                    style: { color: '#6b7280' }
                }, 'Total')
            ]),
            React.createElement('div', {
                key: 'active',
                style: { textAlign: 'center' }
            }, [
                React.createElement('div', {
                    key: 'active-value',
                    style: { fontWeight: 'bold', color: '#4caf50', fontSize: '18px' }
                }, dagStats.active),
                React.createElement('div', {
                    key: 'active-label',
                    style: { color: '#6b7280' }
                }, 'Active')
            ]),
            React.createElement('div', {
                key: 'paused',
                style: { textAlign: 'center' }
            }, [
                React.createElement('div', {
                    key: 'paused-value',
                    style: { fontWeight: 'bold', color: '#ff9800', fontSize: '18px' }
                }, dagStats.paused),
                React.createElement('div', {
                    key: 'paused-label',
                    style: { color: '#6b7280' }
                }, 'Paused')
            ])
        ]),
        
        // Buttons
        React.createElement('div', {
            key: 'buttons',
            style: {
                display: 'flex',
                gap: '10px',
                marginBottom: message.text ? '10px' : '0'
            }
        }, [
            React.createElement('button', {
                key: 'pause-btn',
                onClick: pauseAllDAGs,
                disabled: loading.pause,
                style: {
                    flex: 1,
                    padding: '8px 12px',
                    background: loading.pause ? '#ccc' : '#ff9800',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: loading.pause ? 'not-allowed' : 'pointer',
                    fontSize: '14px',
                    fontWeight: '500'
                }
            }, loading.pause ? '⏳ Pausing...' : '⏸️ Pause All'),
            React.createElement('button', {
                key: 'unpause-btn',
                onClick: unpauseAllDAGs,
                disabled: loading.unpause,
                style: {
                    flex: 1,
                    padding: '8px 12px',
                    background: loading.unpause ? '#ccc' : '#4caf50',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: loading.unpause ? 'not-allowed' : 'pointer',
                    fontSize: '14px',
                    fontWeight: '500'
                }
            }, loading.unpause ? '⏳ Unpausing...' : '▶️ Unpause All')
        ]),
        
        // Status Message
        message.text ? React.createElement('div', {
            key: 'message',
            style: {
                padding: '8px',
                borderRadius: '4px',
                fontSize: '12px',
                textAlign: 'center',
                background: message.type === 'success' ? '#d4edda' : '#f8d7da',
                color: message.type === 'success' ? '#155724' : '#721c24',
                border: `1px solid ${message.type === 'success' ? '#c3e6cb' : '#f5c6cb'}`
            }
        }, message.text) : null
    ]);
}

// CRITICAL: Set the global variable that matches our plugin name
globalThis['Hello Dashboard'] = DAGManagerWidget;

// Also set the fallback that Airflow looks for
globalThis.AirflowPlugin = DAGManagerWidget;

console.log('DAG Manager Widget globals set:', {
    'Hello Dashboard': typeof globalThis['Hello Dashboard'],
    'AirflowPlugin': typeof globalThis.AirflowPlugin
});
    """
    
    from fastapi.responses import Response
    return Response(content=js_content, media_type="text/javascript")


# Plugin configuration - self-contained, no external URLs
app_config = {
    "app": app,
    "url_prefix": "/simple-plugin",
    "name": "Simple Plugin"
}

# External view configurations
dag_management_view = {
    "name": "DAG Manager",
    "href": "/simple-plugin/dashboard",
    "destination": "nav",
    "category": "admin"
}

# Simple React app for dashboard
hello_world_app = {
    "name": "Hello Dashboard",
    "bundle_url": "/simple-plugin/hello.js",
    "destination": "dashboard",
    "url_route": "hello-world"
}


class DAGManagerPlugin(AirflowPlugin):
    name = "dag_manager"
    fastapi_apps = [app_config]
    external_views = [dag_management_view]
    react_apps = [hello_world_app]