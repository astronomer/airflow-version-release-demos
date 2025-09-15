from typing import Callable
from airflow.plugins_manager import AirflowPlugin
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class HelloWorldLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        print(f"🌐 Hello from middleware! Request: {request.method} {request.url}")
        response = await call_next(request)
        response.headers["X-Hello-Middleware"] = "Hello from Airflow middleware!"
       
        return response


class HelloWorldMiddlewarePlugin(AirflowPlugin):
    name = "hello_middleware"
   
    fastapi_root_middlewares = [
        {
            "middleware": HelloWorldLoggingMiddleware,
            "args": [],
            "kwargs": {},
            "name": "Hello World Logging Middleware"
        }
    ]
