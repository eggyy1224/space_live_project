import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import init_app
from api.endpoints import health, speech, websocket
from core.config import settings
from utils.logger import setup_logging, logger
from fastapi.staticfiles import StaticFiles
import os

# 設定日誌
logger = setup_logging()
logger.info("啟動虛擬太空人後端服務")

# 建立應用
app = init_app()

# --- 添加 CORS 中介軟體 ---
# 允許所有來源 (*)，可以根據需要替換為具體的前端 URL
# 例如 origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # 允許的來源列表
    allow_credentials=True, # 允許 cookies
    allow_methods=["*"], # 允許所有 HTTP 方法
    allow_headers=["*"], # 允許所有 HTTP 標頭
)
# --- CORS 配置結束 ---

# 包含 API 路由
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(speech.router, prefix="/api", tags=["Speech"])

# ... (Static files and startup event) ...

if __name__ == "__main__":
    # 啟動服務器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )