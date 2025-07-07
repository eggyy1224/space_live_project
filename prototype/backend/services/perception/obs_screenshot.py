"""
OBS 截圖服務

使用 OBS WebSocket API 來截取 OBS 畫面影像
"""

import asyncio
import base64
import datetime
import os
from pathlib import Path
from typing import Optional, Dict, Any
import obsws_python as obs
from utils.logger import logger


class OBSScreenshotService:
    """
    OBS 截圖服務類別
    
    負責連接 OBS WebSocket 並執行截圖操作
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 4455,
        password: str = "",
        timeout: int = 10
    ):
        """
        初始化 OBS 截圖服務
        
        Args:
            host: OBS WebSocket 主機位址
            port: OBS WebSocket 連接埠
            password: OBS WebSocket 密碼
            timeout: 連接逾時時間（秒）
        """
        self.host = host
        self.port = port
        self.password = password
        self.timeout = timeout
        self.client = None
        self.screenshots_dir = Path("screenshots")  # 修正：使用相對路徑
        
        # 確保截圖目錄存在
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_client(self) -> obs.ReqClient:
        """
        取得 OBS WebSocket 客戶端
        
        Returns:
            obs.ReqClient: OBS 請求客戶端
            
        Raises:
            ConnectionError: 當無法連接到 OBS 時
        """
        try:
            if not self.client:
                self.client = obs.ReqClient(
                    host=self.host,
                    port=self.port,
                    password=self.password,
                    timeout=self.timeout
                )
            return self.client
        except Exception as e:
            logger.error(f"無法連接到 OBS WebSocket: {e}")
            raise ConnectionError(f"無法連接到 OBS WebSocket: {e}")
    
    def disconnect(self):
        """
        斷開 OBS WebSocket 連接
        """
        if self.client:
            try:
                self.client.disconnect()
                self.client = None
                logger.info("已斷開 OBS WebSocket 連接")
            except Exception as e:
                logger.warning(f"斷開 OBS 連接時發生錯誤: {e}")
    
    def get_obs_status(self) -> Dict[str, Any]:
        """
        取得 OBS 狀態資訊
        
        Returns:
            Dict[str, Any]: OBS 狀態資訊
        """
        try:
            client = self._get_client()
            
            # 取得 OBS 版本資訊
            version_info = client.get_version()
            
            # 取得當前場景
            current_scene = client.get_current_program_scene()
            
            # 取得串流狀態
            stream_status = client.get_stream_status()
            
            # 取得錄影狀態
            record_status = client.get_record_status()
            
            return {
                "obs_version": version_info.obs_version,
                "websocket_version": version_info.obs_web_socket_version,
                "current_scene": current_scene.current_program_scene_name,
                "streaming": stream_status.output_active,
                "recording": record_status.output_active,
                "connected": True
            }
            
        except Exception as e:
            logger.error(f"取得 OBS 狀態失敗: {e}")
            return {
                "connected": False,
                "error": str(e)
            }
    
    def take_screenshot(
        self,
        source_name: Optional[str] = None,
        scene_name: Optional[str] = None,
        width: int = 1920,
        height: int = 1080,
        image_format: str = "png"
    ) -> Dict[str, Any]:
        """
        擷取 OBS 畫面截圖
        
        Args:
            source_name: 來源名稱（如果指定，則截取特定來源）
            scene_name: 場景名稱（如果指定，則截取特定場景）
            width: 截圖寬度
            height: 截圖高度
            image_format: 圖片格式 (png, jpg)
            
        Returns:
            Dict[str, Any]: 截圖結果，包含檔案路徑和基本資訊
        """
        try:
            client = self._get_client()
            
            # 產生時間戳記作為檔案名稱
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            
            if source_name:
                # 截取特定來源
                logger.info(f"正在截取來源 '{source_name}' 的畫面...")
                screenshot_data = client.get_source_screenshot(
                    name=source_name,
                    img_format=image_format,
                    width=width,
                    height=height,
                    quality=90  # 高品質截圖
                )
                filename = f"source_{source_name}_{timestamp}.{image_format}"
            elif scene_name:
                # 截取特定場景
                logger.info(f"正在截取場景 '{scene_name}' 的畫面...")
                # OBS WebSocket v5 沒有直接的場景截圖功能，需要透過程式輸出
                # 這裡我們使用當前程式場景的截圖
                screenshot_data = client.get_source_screenshot(
                    name=scene_name,
                    img_format=image_format,
                    width=width,
                    height=height,
                    quality=90  # 高品質截圖
                )
                filename = f"scene_{scene_name}_{timestamp}.{image_format}"
            else:
                # 截取目前的程式輸出（整個 OBS 畫面）
                logger.info("正在截取 OBS 程式輸出畫面...")
                current_scene = client.get_current_program_scene()
                scene_name = current_scene.current_program_scene_name
                
                screenshot_data = client.get_source_screenshot(
                    name=scene_name,
                    img_format=image_format,
                    width=width,
                    height=height,
                    quality=90  # 高品質截圖
                )
                filename = f"program_output_{timestamp}.{image_format}"
            
            # 解碼 base64 圖片資料
            image_data = screenshot_data.image_data
            # 移除 data URL 前綴（如果存在）
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            # 儲存截圖到檔案
            file_path = self.screenshots_dir / filename
            with open(file_path, 'wb') as f:
                f.write(base64.b64decode(image_data))
            
            logger.info(f"截圖已儲存至: {file_path}")
            
            return {
                "success": True,
                "filename": filename,
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size,
                "timestamp": timestamp,
                "width": width,
                "height": height,
                "format": image_format,
                "source_type": "source" if source_name else "scene" if scene_name else "program_output",
                "source_name": source_name or scene_name or "program_output"
            }
            
        except Exception as e:
            logger.error(f"截圖失敗: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_sources_list(self) -> Dict[str, Any]:
        """
        取得 OBS 中所有可用的來源列表
        
        Returns:
            Dict[str, Any]: 來源列表
        """
        try:
            client = self._get_client()
            
            # 取得當前場景的來源
            current_scene = client.get_current_program_scene()
            scene_items = client.get_scene_item_list(
                name=current_scene.current_program_scene_name  # 修正：使用 name 參數
            )
            
            sources = []
            for item in scene_items.scene_items:
                sources.append({
                    "source_name": item["sourceName"],  # 修正：使用字典鍵值
                    "source_type": item["sourceType"],  # 修正：使用字典鍵值
                    "visible": item["sceneItemEnabled"]  # 修正：使用字典鍵值
                })
            
            return {
                "success": True,
                "current_scene": current_scene.current_program_scene_name,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"取得來源列表失敗: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_scenes_list(self) -> Dict[str, Any]:
        """
        取得 OBS 中所有場景列表
        
        Returns:
            Dict[str, Any]: 場景列表
        """
        try:
            client = self._get_client()
            
            # 取得場景列表
            scenes_data = client.get_scene_list()
            
            scenes = []
            for scene in scenes_data.scenes:
                scenes.append({
                    "scene_name": scene["sceneName"],  # 修正：使用字典鍵值
                    "scene_index": scene["sceneIndex"]  # 修正：使用字典鍵值
                })
            
            return {
                "success": True,
                "current_scene": scenes_data.current_program_scene_name,
                "scenes": scenes
            }
            
        except Exception as e:
            logger.error(f"取得場景列表失敗: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# 建立全域服務實例
obs_screenshot_service = OBSScreenshotService() 