"""
Perception API 端點

處理感知模組相關的 API 請求，包括：
- OBS 畫面截圖
- OBS 狀態查詢
- OBS 來源和場景列表
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from pathlib import Path
from typing import Optional

from dtos.requests import OBSScreenshotRequest, OBSConnectionRequest
from dtos.responses import (
    OBSScreenshotResponse,
    OBSStatusResponse,
    OBSSourcesResponse,
    OBSScenesResponse
)
from services.perception import OBSScreenshotService
from utils.logger import logger

router = APIRouter()

# 建立 OBS 截圖服務實例
obs_service = OBSScreenshotService()


@router.get("/perception/obs/status", response_model=OBSStatusResponse)
async def get_obs_status():
    """
    取得 OBS 連接狀態和基本資訊
    
    Returns:
        OBSStatusResponse: OBS 狀態資訊
    """
    try:
        logger.info("正在查詢 OBS 狀態...")
        status_data = obs_service.get_obs_status()
        return OBSStatusResponse(**status_data)
    except Exception as e:
        logger.error(f"查詢 OBS 狀態時發生錯誤: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢 OBS 狀態失敗: {str(e)}"
        )


@router.post("/perception/obs/screenshot", response_model=OBSScreenshotResponse)
async def take_obs_screenshot(request: OBSScreenshotRequest):
    """
    擷取 OBS 畫面截圖
    
    Args:
        request: 截圖請求參數
        
    Returns:
        OBSScreenshotResponse: 截圖結果
    """
    try:
        logger.info(f"收到 OBS 截圖請求: {request.dict()}")
        
        # 驗證圖片格式
        if request.image_format not in ["png", "jpg", "jpeg"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支援的圖片格式，僅支援 png、jpg、jpeg"
            )
        
        # 驗證解析度
        if request.width <= 0 or request.height <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="寬度和高度必須大於 0"
            )
        
        if request.width > 4096 or request.height > 4096:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="解析度過高，最大支援 4096x4096"
            )
        
        # 執行截圖
        result = obs_service.take_screenshot(
            source_name=request.source_name,
            scene_name=request.scene_name,
            width=request.width,
            height=request.height,
            image_format=request.image_format
        )
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "截圖失敗")
            )
        
        return OBSScreenshotResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"執行 OBS 截圖時發生錯誤: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"截圖失敗: {str(e)}"
        )


@router.get("/perception/obs/sources", response_model=OBSSourcesResponse)
async def get_obs_sources():
    """
    取得 OBS 當前場景的來源列表
    
    Returns:
        OBSSourcesResponse: 來源列表
    """
    try:
        logger.info("正在查詢 OBS 來源列表...")
        sources_data = obs_service.get_sources_list()
        return OBSSourcesResponse(**sources_data)
    except Exception as e:
        logger.error(f"查詢 OBS 來源列表時發生錯誤: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢來源列表失敗: {str(e)}"
        )


@router.get("/perception/obs/scenes", response_model=OBSScenesResponse)
async def get_obs_scenes():
    """
    取得 OBS 所有場景列表
    
    Returns:
        OBSScenesResponse: 場景列表
    """
    try:
        logger.info("正在查詢 OBS 場景列表...")
        scenes_data = obs_service.get_scenes_list()
        return OBSScenesResponse(**scenes_data)
    except Exception as e:
        logger.error(f"查詢 OBS 場景列表時發生錯誤: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢場景列表失敗: {str(e)}"
        )


@router.get("/perception/obs/screenshot/{filename}")
async def download_screenshot(filename: str):
    """
    下載截圖檔案
    
    Args:
        filename: 截圖檔案名稱
        
    Returns:
        FileResponse: 截圖檔案
    """
    try:
        screenshots_dir = Path("screenshots")  # 修正：使用正確的相對路徑
        file_path = screenshots_dir / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="找不到指定的截圖檔案"
            )
        
        if not file_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="指定的路徑不是檔案"
            )
        
        # 檢查檔案是否在正確的目錄內（安全性考量）
        if not str(file_path.absolute()).startswith(str(screenshots_dir.absolute())):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無法存取指定的檔案"
            )
        
        logger.info(f"提供截圖檔案下載: {filename}")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/octet-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下載截圖檔案時發生錯誤: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"下載檔案失敗: {str(e)}"
        )


@router.post("/perception/obs/connection")
async def configure_obs_connection(request: OBSConnectionRequest):
    """
    設定 OBS WebSocket 連接參數
    
    Args:
        request: 連接設定參數
        
    Returns:
        dict: 設定結果
    """
    try:
        logger.info(f"更新 OBS 連接設定: {request.host}:{request.port}")
        
        # 先斷開現有連接
        obs_service.disconnect()
        
        # 更新連接參數
        obs_service.host = request.host
        obs_service.port = request.port
        obs_service.password = request.password
        obs_service.timeout = request.timeout
        
        # 測試新的連接
        status_data = obs_service.get_obs_status()
        
        if status_data.get("connected", False):
            return {
                "success": True,
                "message": "OBS 連接設定已更新並成功連接",
                "status": status_data
            }
        else:
            return {
                "success": False,
                "message": "OBS 連接設定已更新但無法連接",
                "error": status_data.get("error")
            }
        
    except Exception as e:
        logger.error(f"設定 OBS 連接時發生錯誤: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"設定連接失敗: {str(e)}"
        )


@router.delete("/perception/obs/disconnect")
async def disconnect_obs():
    """
    中斷 OBS WebSocket 連接
    
    Returns:
        dict: 中斷結果
    """
    try:
        logger.info("正在中斷 OBS 連接...")
        obs_service.disconnect()
        
        return {
            "success": True,
            "message": "已成功中斷 OBS 連接"
        }
        
    except Exception as e:
        logger.error(f"中斷 OBS 連接時發生錯誤: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"中斷連接失敗: {str(e)}"
        ) 