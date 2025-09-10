"""
FastAPI Middleware Plugin - Simple Syntax Example

This plugin demonstrates how to create FastAPI middleware in Airflow 3.
Middleware intercepts ALL HTTP requests to your Airflow instance.

Key Features:
- Processes EVERY request to http://localhost:8080/*
- Can modify requests and responses globally
- Useful for logging, security, headers, monitoring
- Runs before any other Airflow processing

⚠️  WARNING: Middleware affects ALL Airflow traffic!
"""

import time
from typing import Callable
from airflow.plugins_manager import AirflowPlugin
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


# ============================================================================
# 🛡️ Simple Logging Middleware
# ============================================================================
class SimpleLoggingMiddleware(BaseHTTPMiddleware):
    """
    Simple middleware that logs all requests with timing information.
    This will log EVERY request to your Airflow instance!
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 📥 BEFORE request processing
        start_time = time.time()
        method = request.method
        url = str(request.url)
        client_ip = request.client.host if request.client else "unknown"
        
        # Log incoming request
        print(f"🌐 [{method}] {url} from {client_ip}")
        
        # ⚡ Process the request (call the next middleware/endpoint)
        response = await call_next(request)
        
        # 📤 AFTER request processing
        process_time = time.time() - start_time
        status_code = response.status_code
        
        # Log response with timing
        print(f"✅ [{method}] {url} → {status_code} ({process_time:.3f}s)")
        
        # Add custom header to ALL responses
        response.headers["X-Airflow-Plugin"] = "SimpleLoggingMiddleware"
        response.headers["X-Response-Time"] = f"{process_time:.3f}s"
        
        return response


# ============================================================================
# 🔒 Simple Security Headers Middleware  
# ============================================================================
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Simple middleware that adds security headers to all responses.
    Enhances security for your entire Airflow instance!
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Process the request normally
        response = await call_next(request)
        
        # Add security headers to ALL responses
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Custom header showing this middleware ran
        response.headers["X-Security-Enhanced"] = "true"
        
        return response


# ============================================================================
# 📊 Simple Request Counter Middleware
# ============================================================================
class RequestCounterMiddleware(BaseHTTPMiddleware):
    """
    Simple middleware that counts all requests.
    Demonstrates stateful middleware.
    """
    
    def __init__(self, app, **kwargs):
        super().__init__(app)
        self.request_count = 0
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Increment counter for every request
        self.request_count += 1
        
        # Process the request
        response = await call_next(request)
        
        # Add counter to response headers
        response.headers["X-Request-Count"] = str(self.request_count)
        
        # Log milestone requests
        if self.request_count % 10 == 0:
            print(f"🎉 Milestone: {self.request_count} requests processed!")
        
        return response


# ============================================================================
# 🔌 Plugin Registration
# ============================================================================
class FastAPIMiddlewarePlugin(AirflowPlugin):
    """
    Plugin that registers FastAPI middlewares for global request processing.
    
    Key Concepts:
    - fastapi_root_middlewares: List of middleware configurations
    - Each middleware processes ALL requests to Airflow
    - Middleware stack executes in the order defined
    - Can be used for logging, security, monitoring, etc.
    
    URLs affected: ALL http://localhost:8080/* requests!
    """
    
    name = "fastapi_middleware_example"
    
    # Register multiple middlewares (executed in order)
    fastapi_root_middlewares = [
        {
            "middleware": SimpleLoggingMiddleware,     # Middleware class
            "args": [],                               # Positional arguments
            "kwargs": {},                             # Keyword arguments  
            "name": "Simple Logging Middleware"       # Display name
        },
        {
            "middleware": SecurityHeadersMiddleware,
            "args": [],
            "kwargs": {},
            "name": "Security Headers Middleware"
        },
        {
            "middleware": RequestCounterMiddleware,
            "args": [],
            "kwargs": {},
            "name": "Request Counter Middleware"
        }
    ]
    
    # Note: No fastapi_apps or external_views needed!
    # Middleware works at the global HTTP level


# ============================================================================
# 📝 Usage Instructions
# ============================================================================
"""
🚀 How to Test This Middleware:

1. Restart Airflow to load the plugin

2. Visit ANY Airflow URL:
   - http://localhost:8080/
   - http://localhost:8080/dags
   - http://localhost:8080/admin/
   - http://localhost:8080/fastapi-app/
   
3. Check your Airflow logs - you should see:
   🌐 [GET] http://localhost:8080/ from 127.0.0.1
   ✅ [GET] http://localhost:8080/ → 200 (0.045s)

4. Check response headers in browser dev tools:
   - X-Airflow-Plugin: SimpleLoggingMiddleware
   - X-Response-Time: 0.045s
   - X-Security-Enhanced: true
   - X-Request-Count: 1

5. Every 10th request will log:
   🎉 Milestone: 10 requests processed!

⚠️  Remember: This affects ALL Airflow traffic!
"""
