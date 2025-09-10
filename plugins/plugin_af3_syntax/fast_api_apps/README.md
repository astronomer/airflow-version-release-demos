# FastAPI App Plugin - Comprehensive Syntax Example

This is a **complete FastAPI application plugin** for Airflow 3, demonstrating all the key concepts and capabilities.

## 📁 File Structure

```
fast_api_apps/
├── example_fast_api_app.py    # 🐍 Main FastAPI app plugin
├── templates/
│   └── hello.html             # 📄 HTML template with API docs
├── static/
│   ├── style.css              # 🎨 Professional styling
│   └── script.js              # ⚡ Interactive API testing
└── README.md                  # 📚 This documentation
```

## 🚀 Key Differences from External Views

| Feature | External Views | FastAPI Apps |
|---------|---------------|--------------|
| **Purpose** | UI integration | Standalone API |
| **Access** | Via Airflow UI links | Direct URL access |
| **Registration** | `external_views = []` | `fastapi_apps = []` |
| **UI Integration** | Automatic with `url_route` | Manual/none |
| **API Capabilities** | Limited | Full REST API |
| **Documentation** | Manual | Auto-generated |

## 🔧 Technical Features

### **🌐 Full REST API**
```python
@app.get("/")                    # GET endpoints
@app.post("/api/message")        # POST endpoints  
@app.get("/health")              # Health checks
@app.get("/airflow-integration") # Airflow data access
```

### **📊 Pydantic Models**
```python
class UserMessage(BaseModel):
    message: str
    user_name: str = "Anonymous"
```

### **📚 Auto-Generated Documentation**
- **Swagger UI**: `/fastapi-app/docs`
- **ReDoc**: `/fastapi-app/redoc`

### **🎨 Static File Serving**
- CSS, JavaScript, images
- Proper MIME type detection
- Error handling

### **🔌 Airflow Integration**
```python
@app.get("/airflow-integration")
async def airflow_integration():
    from airflow.models import DagBag
    dagbag = DagBag()
    return {"total_dags": len(dagbag.dags)}
```

## 🌍 Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| **GET** | `/fastapi-app/` | Root API info |
| **GET** | `/fastapi-app/info` | Plugin details |
| **GET** | `/fastapi-app/hello` | HTML page |
| **POST** | `/fastapi-app/api/message` | Send messages |
| **GET** | `/fastapi-app/health` | Health check |
| **GET** | `/fastapi-app/airflow-integration` | DAG count |
| **GET** | `/fastapi-app/docs` | API documentation |
| **GET** | `/fastapi-app/static/{file}` | Static files |

## 🎯 Usage Examples

### **1. Basic API Call**
```bash
curl http://localhost:8080/fastapi-app/
```

### **2. POST Request**
```bash
curl -X POST http://localhost:8080/fastapi-app/api/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "user_name": "Test"}'
```

### **3. View Documentation**
Visit: `http://localhost:8080/fastapi-app/docs`

### **4. Interactive Testing**
Visit: `http://localhost:8080/fastapi-app/hello`

## 🔒 Plugin Registration

```python
class FastAPIAppPlugin(AirflowPlugin):
    name = "fastapi_app_example"
    
    fastapi_apps = [{
        "app": app,                    # FastAPI instance
        "url_prefix": "/fastapi-app",  # URL prefix
        "name": "FastAPI App Example" # Display name
    }]
    
    # Note: No external_views needed!
```

## ✨ Interactive Features

- **🧪 API Testing**: Built-in test runner
- **📊 Real-time Results**: Live API response display
- **🎨 Professional UI**: Modern, responsive design
- **♿ Accessibility**: Full keyboard and screen reader support

## 🎨 Professional Design

- **🎨 Brand colors**: Moonshot palette integration
- **🌈 FastAPI green**: Distinctive theme
- **📱 Responsive**: Mobile-friendly design
- **✨ Animations**: Smooth transitions and feedback

## 🔄 Next Steps

This FastAPI app serves as a **complete template** for building:

- **REST APIs** for Airflow data
- **Webhook endpoints** for external integrations
- **Admin tools** with custom interfaces
- **Data visualization** dashboards
- **Integration services** with external systems

Perfect foundation for real-world Airflow 3 FastAPI applications! 🚀
