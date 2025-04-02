from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings

def setup_cors(app: FastAPI) -> None:
    """
    設置CORS中間件
    
    Args:
        app: FastAPI應用實例
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_CREDENTIALS,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    ) 