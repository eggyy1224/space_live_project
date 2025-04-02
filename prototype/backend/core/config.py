import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

class Settings:
    """應用配置類"""
    # API配置
    API_PREFIX = "/api"
    
    # CORS配置
    CORS_ORIGINS = ["*"]  # 在生產環境中應該設置為特定域名
    CORS_CREDENTIALS = True
    CORS_METHODS = ["*"]
    CORS_HEADERS = ["*"]
    
    # Google API配置
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    # AI模型配置
    AI_MODEL_NAME = "gemini-2.0-flash"
    
    # 生成配置
    GENERATION_TEMPERATURE = 0.7
    GENERATION_TOP_P = 0.8
    GENERATION_TOP_K = 40
    GENERATION_MAX_TOKENS = 1024
    
    # 動畫配置
    TRANSITION_STEPS = 8
    TRANSITION_DELAY = 0.08
    TRANSITION_SPEED = 0.3

settings = Settings() 