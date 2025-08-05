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
from services.perception import OBSScreenshotService, VisionAnalysisService
from utils.logger import logger
import httpx
import json

router = APIRouter()

# 建立服務實例
obs_service = OBSScreenshotService()
vision_service = VisionAnalysisService()


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


@router.post("/perception/obs/stream/start")
async def start_obs_streaming():
    """
    開始 OBS 串流
    
    Returns:
        dict: 串流開始結果
    """
    try:
        logger.info("正在開始 OBS 串流...")
        result = obs_service.start_streaming()
        
        if result.get("success", False):
            return {
                "success": True,
                "message": result.get("message", "串流已開始"),
                "streaming": result.get("streaming", False)
            }
        else:
            return {
                "success": False,
                "message": result.get("message", "開始串流失敗"),
                "streaming": result.get("streaming", False)
            }
        
    except Exception as e:
        logger.error(f"開始 OBS 串流時發生錯誤: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"開始串流失敗: {str(e)}"
        )


@router.post("/perception/obs/stream/stop")
async def stop_obs_streaming():
    """
    停止 OBS 串流
    
    Returns:
        dict: 串流停止結果
    """
    try:
        logger.info("正在停止 OBS 串流...")
        result = obs_service.stop_streaming()
        
        if result.get("success", False):
            return {
                "success": True,
                "message": result.get("message", "串流已停止"),
                "streaming": result.get("streaming", False)
            }
        else:
            return {
                "success": False,
                "message": result.get("message", "停止串流失敗"),
                "streaming": result.get("streaming", True)
            }
        
    except Exception as e:
        logger.error(f"停止 OBS 串流時發生錯誤: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"停止串流失敗: {str(e)}"
        )


@router.post("/perception/obs/record/start")
async def start_obs_recording():
    """
    開始 OBS 錄影
    
    Returns:
        dict: 錄影開始結果
    """
    try:
        logger.info("正在開始 OBS 錄影...")
        result = obs_service.start_recording()
        
        if result.get("success", False):
            return {
                "success": True,
                "message": result.get("message", "錄影已開始"),
                "recording": result.get("recording", False)
            }
        else:
            return {
                "success": False,
                "message": result.get("message", "開始錄影失敗"),
                "recording": result.get("recording", False)
            }
        
    except Exception as e:
        logger.error(f"開始 OBS 錄影時發生錯誤: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"開始錄影失敗: {str(e)}"
        )


@router.post("/perception/obs/record/stop")
async def stop_obs_recording():
    """
    停止 OBS 錄影
    
    Returns:
        dict: 錄影停止結果
    """
    try:
        logger.info("正在停止 OBS 錄影...")
        result = obs_service.stop_recording()
        
        if result.get("success", False):
            return {
                "success": True,
                "message": result.get("message", "錄影已停止"),
                "recording": result.get("recording", False)
            }
        else:
            return {
                "success": False,
                "message": result.get("message", "停止錄影失敗"),
                "recording": result.get("recording", True)
            }
        
    except Exception as e:
        logger.error(f"停止 OBS 錄影時發生錯誤: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"停止錄影失敗: {str(e)}"
        )


@router.post("/perception/capture-and-analyze")
async def capture_and_analyze_field():
    """
    整合端點：截圖展場視訊源 -> 顯示圖片 -> 分析圖片內容
    
    執行流程：
    1. 使用 OBS 截圖 API 擷取「展場視訊源」
    2. 透過 show_existing_image 顯示截圖到前端
    3. 使用視覺分析服務分析圖片內容
    4. 回傳分析結果
    
    Returns:
        dict: 包含截圖資訊和分析結果
    """
    try:
        logger.info("開始執行展場視訊源截圖分析流程...")
        
        # 步驟 1: OBS 截圖
        logger.info("步驟 1: 截圖展場視訊源...")
        screenshot_result = obs_service.take_screenshot(
            source_name="展場視訊源",
            scene_name="場景 2",  # 根據之前的測試，使用場景 2
            width=1920,
            height=1080,
            image_format="png"
        )
        
        if not screenshot_result.get("success", False):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"OBS 截圖失敗: {screenshot_result.get('error', '未知錯誤')}"
            )
        
        filename = screenshot_result["filename"]
        file_path = screenshot_result["file_path"]
        
        logger.info(f"截圖成功: {filename}")
        
        # 步驟 2: 顯示圖片到前端
        logger.info("步驟 2: 顯示截圖到前端...")
        async with httpx.AsyncClient() as client:
            show_image_payload = {
                "filename": filename,
                "caption": "展場視訊源即時截圖",
                "position": "center-left",
                "size": "large",
                "duration": 20.0
            }
            
            show_response = await client.post(
                "http://localhost:8000/api/show-existing-image",
                json=show_image_payload,
                timeout=10.0
            )
            
            if show_response.status_code != 200:
                logger.warning(f"顯示圖片失敗: {show_response.status_code}")
            else:
                logger.info("圖片已顯示到前端")
        
        # 步驟 3: 分析圖片內容
        logger.info("步驟 3: 分析圖片內容...")
        
        # 確保使用完整的檔案路徑
        import os
        if not os.path.isabs(file_path):
            # 如果是相對路徑，組合成絕對路徑
            BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            full_image_path = os.path.join(BACKEND_DIR, file_path)
        else:
            full_image_path = file_path
        
        analysis_result = await vision_service.analyze_image(
            image_path=full_image_path,
            analysis_type="exhibition"
        )
        
        # 整合回傳結果
        result = {
            "success": True,
            "screenshot": {
                "filename": filename,
                "file_path": file_path,
                "file_size": screenshot_result.get("file_size"),
                "timestamp": screenshot_result.get("timestamp"),
                "width": screenshot_result.get("width"),
                "height": screenshot_result.get("height"),
                "format": screenshot_result.get("format"),
                "source_name": screenshot_result.get("source_name")
            },
            "analysis": analysis_result,
            "display_status": "圖片已顯示到前端" if show_response.status_code == 200 else "圖片顯示失敗"
        }
        
        logger.info("展場視訊源截圖分析流程完成")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"展場視訊源截圖分析流程失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"截圖分析流程失敗: {str(e)}"
        ) 