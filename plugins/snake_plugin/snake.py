from airflow.plugins_manager import AirflowPlugin
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from datetime import datetime


app = FastAPI(title="Snake Game Plugin", version="1.0.0")

PLUGIN_DIR = Path(__file__).parent / "snake_game"

app.mount("/static", StaticFiles(directory=str(PLUGIN_DIR / "static")), name="static")


@app.get("/")
async def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/snake-game/game")


@app.get("/game")
async def snake_game_page():
    try:
        template_path = PLUGIN_DIR / "templates" / "snake_game.html"
        with open(template_path, "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        error_html = f"""
        <html><body>
        <h1>🐍 Game Error</h1>
        <p>Could not load Snake game: {str(e)}</p>
        <p><a href="javascript:location.reload()">🔄 Reload Page</a></p>
        </body></html>
        """
        return HTMLResponse(content=error_html)



@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "snake-game-plugin", "high_score": "∞"}


class SnakeGamePlugin(AirflowPlugin):
    name = "snake_game"
    
    fastapi_apps = [{
        "app": app,
        "url_prefix": "/snake-game",
        "name": "Snake Game Plugin"
    }]
    
    external_views = [{
        "name": "Snake",
        "icon": "/snake-game/static/snake-icon.svg",
        "href": "/snake-game/game",
        "destination": "nav",
        "url_route": "snake_game",
        "nav_top_level": True,
    }]
    