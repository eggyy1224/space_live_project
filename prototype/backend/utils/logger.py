import sys
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logging(log_level=logging.DEBUG, log_to_console=True, log_to_file=True, log_file_path=None):
    """
    設置應用日誌
    
    Args:
        log_level: 日誌級別
        log_to_console: 是否輸出到控制台
        log_to_file: 是否輸出到文件
        log_file_path: 日誌文件路徑
    """
    # 獲取根日誌記錄器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 清除現有處理器
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)
    
    # 日誌格式
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(module)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 控制台日誌
    if log_to_console:
        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # 文件日誌
    if log_to_file:
        if log_file_path is None:
            # 默認日誌路徑
            log_dir = Path(__file__).resolve().parent.parent / "logs"
            log_dir.mkdir(exist_ok=True)
            log_file_path = log_dir / "app.log"
        
        # 旋轉日誌處理器，每個文件1MB，保留10個備份
        file_handler = RotatingFileHandler(
            log_file_path, maxBytes=1024*1024, backupCount=10, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # 設置特定庫的日誌級別
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    
    # 返回根記錄器
    return root_logger

# 創建默認記錄器
logger = logging.getLogger(__name__) 