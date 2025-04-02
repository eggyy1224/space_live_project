from fastapi import FastAPI
from .base import create_app
from .endpoints import websocket
from .endpoints import speech
from .endpoints import expressions
from .endpoints import health
from .middleware.cors import setup_cors

def init_app() -> FastAPI:
    """初始化應用並註冊所有路由"""
    app = create_app()
    
    # 設置中間件
    setup_cors(app)
    
    # 註冊WebSocket路由
    app.add_websocket_route("/ws", websocket.websocket_endpoint)
    
    # 註冊常規API路由
    app.include_router(speech.router, prefix="/api", tags=["speech"])
    app.include_router(expressions.router, prefix="/api", tags=["expressions"])
    app.include_router(health.router, prefix="/api", tags=["system"])
    
    return app 