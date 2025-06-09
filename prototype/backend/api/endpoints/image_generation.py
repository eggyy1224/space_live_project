import json
import logging
import os
import time
from typing import Optional


from google import genai
from google.genai.types import GenerateContentConfig
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.config import settings

from .websocket import manager

router = APIRouter()

# 使用新的Google Gen AI SDK配置客戶端
client = genai.Client(api_key=settings.GOOGLE_API_KEY)

# 修正路徑：從 api/endpoints 向上三層到達 backend 目錄
GENERATED_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "generated_images"
)
os.makedirs(GENERATED_DIR, exist_ok=True)


class ImageGenerationRequest(BaseModel):
    description: str
    # 位置控制 (可選)
    position: Optional[str] = "center-right"  # center-right, top-right, bottom-right, center-left, top-left, bottom-left, center
    # 大小控制 (可選)
    size: Optional[str] = "medium"  # small, medium, large
    # 自定義位置 (可選，優先於 position)
    custom_position: Optional[dict] = None  # {"top": "50%", "right": "50px", "transform": "translateY(-50%)"}
    # 自定義大小 (可選，優先於 size)
    custom_size: Optional[dict] = None  # {"width": "350px", "height": "280px"}
    # 顯示持續時間 (可選，秒)
    duration: Optional[float] = 10.0
    # 圖像長寬比 (可選) square, portrait, landscape
    aspect_ratio: Optional[str] = None


class ShowExistingImageRequest(BaseModel):
    filename: str  # 圖片檔名，例如 "image_1749309153863.png"
    caption: Optional[str] = "現有圖片"  # 顯示的說明文字
    # 位置控制 (可選)
    position: Optional[str] = "center"  # center-right, top-right, bottom-right, center-left, top-left, bottom-left, center
    # 大小控制 (可選)
    size: Optional[str] = "large"  # small, medium, large
    # 自定義位置 (可選，優先於 position)
    custom_position: Optional[dict] = None
    # 自定義大小 (可選，優先於 size)
    custom_size: Optional[dict] = None
    # 顯示持續時間 (可選，秒)
    duration: Optional[float] = 15.0
    # 圖像長寬比 (可選)
    aspect_ratio: Optional[str] = "landscape"


@router.post("/generate-image")
async def generate_image(request: ImageGenerationRequest):
    try:
        # 構建包含長寬比資訊的描述
        prompt = f"Generate an image of: {request.description}"
        
        if request.aspect_ratio:
            aspect_map = {
                "square": "in a square format (1:1 aspect ratio)",
                "portrait": "in a portrait format (3:4 aspect ratio)",
                "landscape": "in a landscape format (4:3 aspect ratio)"
            }
            aspect_text = aspect_map.get(request.aspect_ratio, "")
            if aspect_text:
                prompt += f" {aspect_text}"
        
        # 使用正確的Gemini圖像生成模型和配置
        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=prompt,
            config=GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"]
            )
        )
        
        # 解析回應
        image_data = None
        caption = ""
        
        for part in response.candidates[0].content.parts:
            if part.text:
                caption = part.text.strip()
            elif part.inline_data:
                image_data = part.inline_data.data
        
        if not image_data:
            raise HTTPException(status_code=500, detail="No image generated")

        # 儲存圖像檔案
        filename = f"image_{int(time.time()*1000)}.png"
        file_path = os.path.join(GENERATED_DIR, filename)

        # 將圖像數據保存到檔案
        with open(file_path, "wb") as f:
            f.write(image_data)
        
        url = f"/generated-images/{filename}"
        
        # 處理位置和大小設定
        display_config = _get_display_config(request)

        # 透過WebSocket廣播結果，包含顯示配置
        await manager.broadcast(json.dumps({
            "type": "generated-image",
            "url": url,
            "caption": caption,
            "display_config": display_config,
            "duration": request.duration,
            "aspect_ratio": request.aspect_ratio
        }))

        return {
            "success": True,
            "url": url,
            "caption": caption,
            "display_config": display_config,
            "duration": request.duration,
            "aspect_ratio": request.aspect_ratio
        }
        
    except Exception as e:
        logging.error(f"Image generation failed: {e}")
        raise HTTPException(status_code=500, detail="Image generation failed")


def _get_display_config(request: ImageGenerationRequest) -> dict:
    """根據請求參數生成顯示配置"""
    config = {}
    
    # 處理位置
    if request.custom_position:
        config["position"] = request.custom_position
    else:
        position_presets = {
            "center-right": {"top": "50%", "right": "50px", "transform": "translateY(-50%)"},
            "top-right": {"top": "20px", "right": "20px"},
            "bottom-right": {"bottom": "20px", "right": "20px"},
            "center-left": {"top": "50%", "left": "50px", "transform": "translateY(-50%)"},
            "top-left": {"top": "20px", "left": "20px"},
            "bottom-left": {"bottom": "20px", "left": "20px"},
            "center": {"top": "50%", "left": "50%", "transform": "translate(-50%, -50%)"}
        }
        config["position"] = position_presets.get(request.position, position_presets["center-right"])
    
    # 處理大小
    if request.custom_size:
        config["size"] = request.custom_size
    else:
        size_presets = {
            "small": {"width": "250px", "height": "200px"},
            "medium": {"width": "350px", "height": "280px"},
            "large": {"width": "450px", "height": "360px"}
        }
        config["size"] = size_presets.get(request.size, size_presets["medium"])
    
    return config


@router.post("/show-existing-image")
async def show_existing_image(request: ShowExistingImageRequest):
    """顯示已存在的圖片"""
    try:
        # 檢查圖片文件是否存在
        file_path = os.path.join(GENERATED_DIR, request.filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Image file not found: {request.filename}")
        
        url = f"/generated-images/{request.filename}"
        
        # 使用相同的顯示配置邏輯
        display_config = _get_display_config_for_existing(request)

        # 透過WebSocket廣播結果
        await manager.broadcast(json.dumps({
            "type": "generated-image",
            "url": url,
            "caption": request.caption,
            "display_config": display_config,
            "duration": request.duration,
            "aspect_ratio": request.aspect_ratio
        }))

        return {
            "success": True,
            "url": url,
            "caption": request.caption,
            "display_config": display_config,
            "duration": request.duration,
            "aspect_ratio": request.aspect_ratio
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Show existing image failed: {e}")
        raise HTTPException(status_code=500, detail="Show existing image failed")


def _get_display_config_for_existing(request: ShowExistingImageRequest) -> dict:
    """根據請求參數生成顯示配置（用於現有圖片）"""
    config = {}
    
    # 處理位置
    if request.custom_position:
        config["position"] = request.custom_position
    else:
        position_presets = {
            "center-right": {"top": "50%", "right": "50px", "transform": "translateY(-50%)"},
            "top-right": {"top": "20px", "right": "20px"},
            "bottom-right": {"bottom": "20px", "right": "20px"},
            "center-left": {"top": "50%", "left": "50px", "transform": "translateY(-50%)"},
            "top-left": {"top": "20px", "left": "20px"},
            "bottom-left": {"bottom": "20px", "left": "20px"},
            "center": {"top": "50%", "left": "50%", "transform": "translate(-50%, -50%)"}
        }
        config["position"] = position_presets.get(request.position, position_presets["center"])
    
    # 處理大小
    if request.custom_size:
        config["size"] = request.custom_size
    else:
        size_presets = {
            "small": {"width": "250px", "height": "200px"},
            "medium": {"width": "350px", "height": "280px"},
            "large": {"width": "450px", "height": "360px"}
        }
        config["size"] = size_presets.get(request.size, size_presets["large"])
    
    return config
