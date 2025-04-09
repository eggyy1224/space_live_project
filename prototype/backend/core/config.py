import os
from dotenv import load_dotenv
from typing import Optional

# 載入環境變數
load_dotenv()

class Settings:
    """應用配置類"""
    # API配置
    API_PREFIX = "/api"
    
    # CORS配置
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174"
    ]  # 明確指定允許的來源，提高安全性
    CORS_CREDENTIALS = True
    CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS = ["Content-Type", "Authorization", "X-Requested-With"]
    
    # Google API配置
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # AI模型配置
    AI_MODEL_NAME = "gemini-2.0-flash"
    
    # 生成配置
    GENERATION_TEMPERATURE = 0.7
    GENERATION_TOP_P = 0.8
    GENERATION_TOP_K = 40
    GENERATION_MAX_TOKENS = 1024
    
    # LangChain配置
    MEMORY_MAX_HISTORY = 10  # 對話歷史的最大存儲條數
    VECTOR_MEMORY_K = 3  # 向量記憶檢索數量
    
    # ChromaDB配置
    VECTOR_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chroma_db")
    
    # 動畫配置
    TRANSITION_STEPS = 8
    TRANSITION_DELAY = 0.08
    TRANSITION_SPEED = 0.3

settings = Settings() 