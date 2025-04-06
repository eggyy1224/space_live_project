from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from .base import create_app
from .endpoints import websocket
from .endpoints import speech
from .endpoints import expressions
from .endpoints import health
from .middleware.cors import setup_cors
import os
import logging

# 設置日誌
logger = logging.getLogger(__name__)

def init_app() -> FastAPI:
    """初始化應用並註冊所有路由"""
    app = create_app()
    
    # 設置中間件 
    # setup_cors(app)  # 注釋掉，避免與下面的重複
    
    # 添加 CORS 中間件（確保適用於所有路由）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允許所有來源訪問
        allow_credentials=True,
        allow_methods=["*"],  # 允許所有方法
        allow_headers=["*"],  # 允許所有頭
    )
    
    # 註冊WebSocket路由
    app.add_websocket_route("/ws", websocket.websocket_endpoint)
    
    # 註冊常規API路由
    app.include_router(speech.router, prefix="/api", tags=["speech"])
    app.include_router(expressions.router, prefix="/api", tags=["expressions"])
    app.include_router(health.router, prefix="/api", tags=["system"])
    
    # 創建音頻目錄（如果不存在）
    audio_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "audio")
    os.makedirs(audio_dir, exist_ok=True)
    
    # 確保音頻目錄有正確的權限
    try:
        # 嘗試添加讀取權限
        os.chmod(audio_dir, 0o755)
        logger.info(f"設置音頻目錄權限: {audio_dir}")
    except Exception as e:
        logger.warning(f"無法設置音頻目錄權限: {e}")
    
    # 掛載靜態文件，設置HTML=True以支持瀏覽器訪問
    app.mount("/audio", StaticFiles(directory=audio_dir, html=True, check_dir=True), name="audio")
    
    # 添加簡單的音頻文件訪問路由，作為備選方案
    @app.get("/audio-file/{filename}")
    async def get_audio_file(filename: str):
        filepath = os.path.join(audio_dir, filename)
        if os.path.exists(filepath):
            logger.info(f"提供音頻文件: {filepath}")
            # 擴展 CORS 標頭
            cors_headers = {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Access-Control-Max-Age": "86400", # 24小時缓存預檢請求
                "Cache-Control": "no-cache", # 避免瀏覽器緩存，確保始終從伺服器獲取最新音頻
            }
            return FileResponse(
                filepath, 
                media_type="audio/mpeg",
                headers=cors_headers
            )
        else:
            logger.error(f"音頻文件不存在: {filepath}")
            return {"error": "音頻文件不存在"}
    
    return app 