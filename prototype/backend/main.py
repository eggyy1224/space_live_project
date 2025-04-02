import uvicorn
from api import init_app
from utils.logger import setup_logging

# 設定日誌
logger = setup_logging()
logger.info("啟動虛擬太空人後端服務")

# 建立應用
app = init_app()

if __name__ == "__main__":
    # 啟動服務器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )