from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings

def create_app() -> FastAPI:
    """
    創建並配置FastAPI應用
    
    Returns:
        已配置的FastAPI應用
    """
    app = FastAPI(title="太空人虛擬人物API")
    
    # 設置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_CREDENTIALS,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    )
    
    return app 