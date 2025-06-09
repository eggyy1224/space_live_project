import json
import logging
import os
import time
import base64
from typing import Optional
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import glob

from google import genai
from google.genai.types import GenerateContentConfig, Content, Part
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
SELFIES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "selfies"
)
os.makedirs(GENERATED_DIR, exist_ok=True)
os.makedirs(SELFIES_DIR, exist_ok=True)


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


class SelfieRequest(BaseModel):
    description: str = "拍一張自拍照"  # 自拍描述
    # 參考圖像檔名 (可選，從 selfies 或 generated_images 資料夾)
    reference_image: Optional[str] = None  
    # 修改指令 (可選)
    modification: Optional[str] = None  # 例如: "換個表情", "換個姿勢", "改變背景"
    # 是否自動使用最新的自拍作為參考 (可選)
    use_latest_selfie: Optional[bool] = False
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
    aspect_ratio: Optional[str] = "portrait"  # 自拍通常是直向
    # 是否添加時間戳章 (可選)
    add_timestamp: Optional[bool] = True


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


def _add_timestamp_to_image(image_data: bytes) -> bytes:
    """為圖像添加時間戳章"""
    try:
        # 打開圖像
        image = Image.open(io.BytesIO(image_data))
        
        # 創建可繪製對象
        draw = ImageDraw.Draw(image)
        
        # 獲取當前時間
        timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        
        # 嘗試載入字體，如果失敗則使用預設字體
        try:
            # 在 macOS 上嘗試使用系統字體
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        except:
            try:
                # 嘗試其他常見字體路徑
                font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 20)
            except:
                # 使用預設字體
                font = ImageFont.load_default()
        
        # 獲取圖像尺寸
        width, height = image.size
        
        # 計算文字位置 (右下角)
        text_bbox = draw.textbbox((0, 0), timestamp, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = width - text_width - 10
        y = height - text_height - 10
        
        # 繪製半透明背景
        background_bbox = [x - 5, y - 5, x + text_width + 5, y + text_height + 5]
        draw.rectangle(background_bbox, fill=(0, 0, 0, 128))
        
        # 繪製時間戳文字
        draw.text((x, y), timestamp, fill=(255, 255, 255, 255), font=font)
        
        # 將修改後的圖像轉換回 bytes
        output = io.BytesIO()
        image.save(output, format='PNG')
        return output.getvalue()
        
    except Exception as e:
        logging.warning(f"Failed to add timestamp: {e}")
        # 如果添加時間戳失敗，返回原始圖像
        return image_data


def _get_latest_selfie() -> Optional[str]:
    """獲取最新的自拍檔名"""
    try:
        # 獲取所有自拍檔案
        selfie_files = glob.glob(os.path.join(SELFIES_DIR, "selfie_*.png"))
        
        if not selfie_files:
            return None
        
        # 按修改時間排序，取最新的
        latest_file = max(selfie_files, key=os.path.getmtime)
        
        # 只返回檔名
        return os.path.basename(latest_file)
        
    except Exception as e:
        logging.error(f"Failed to get latest selfie: {e}")
        return None


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


@router.post("/continue-selfie")
async def continue_selfie(request: dict):
    """繼續自拍 - 自動使用最新的自拍作為參考圖像"""
    try:
        # 獲取修改指令
        modification = request.get("modification", "稍微改變一下表情和姿勢")
        position = request.get("position", "center")
        size = request.get("size", "large")
        duration = request.get("duration", 20.0)
        
        # 創建自拍請求，自動使用最新自拍
        selfie_request = SelfieRequest(
            description="繼續自拍",
            use_latest_selfie=True,
            modification=modification,
            position=position,
            size=size,
            duration=duration,
            add_timestamp=True
        )
        
        # 調用原有的自拍功能
        return await take_selfie(selfie_request)
        
    except Exception as e:
        logging.error(f"Continue selfie failed: {e}")
        raise HTTPException(status_code=500, detail="Continue selfie failed")


@router.post("/take-selfie")
async def take_selfie(request: SelfieRequest):
    """拍自拍照 - 可以基於參考圖像生成新的自拍"""
    try:
        # 構建自拍提示
        base_prompt = f"Take a selfie: {request.description}"
        
        if request.aspect_ratio:
            aspect_map = {
                "square": "in a square format (1:1 aspect ratio)",
                "portrait": "in a portrait format (3:4 aspect ratio)", 
                "landscape": "in a landscape format (4:3 aspect ratio)"
            }
            aspect_text = aspect_map.get(request.aspect_ratio, "")
            if aspect_text:
                base_prompt += f" {aspect_text}"
        
        # 處理參考圖像邏輯
        reference_image_name = request.reference_image
        
        # 如果啟用了自動使用最新自拍，且沒有指定參考圖像
        if request.use_latest_selfie and not reference_image_name:
            latest_selfie = _get_latest_selfie()
            if latest_selfie:
                reference_image_name = latest_selfie
                logging.info(f"Auto-using latest selfie as reference: {latest_selfie}")
        
        # 如果有參考圖像，使用多模態輸入
        if reference_image_name:
            # 先檢查 selfies 資料夾，再檢查 generated_images 資料夾
            ref_path_selfies = os.path.join(SELFIES_DIR, reference_image_name)
            ref_path_generated = os.path.join(GENERATED_DIR, reference_image_name)
            
            ref_path = None
            if os.path.exists(ref_path_selfies):
                ref_path = ref_path_selfies
            elif os.path.exists(ref_path_generated):
                ref_path = ref_path_generated
            
            if ref_path:
                # 讀取參考圖像
                with open(ref_path, "rb") as f:
                    reference_image_data = f.read()
                
                # 修改提示詞，指示基於參考圖像
                if request.modification:
                    base_prompt += f". Based on the reference selfie image provided, {request.modification}"
                else:
                    base_prompt += ". Based on the reference selfie image provided, create a similar but slightly different selfie with natural variations in pose, expression, or lighting"
                
                logging.info(f"Using reference image: {ref_path}, size: {len(reference_image_data)} bytes")
                
                # 使用多模態輸入 - 圖像 + 文字
                try:
                    response = client.models.generate_content(
                        model="gemini-2.0-flash-preview-image-generation",
                        contents=[
                            {"role": "user", "parts": [
                                {"inline_data": {"mime_type": "image/png", "data": base64.b64encode(reference_image_data).decode('utf-8')}},
                                {"text": base_prompt}
                            ]}
                        ],
                        config=GenerateContentConfig(
                            response_modalities=["TEXT", "IMAGE"]
                        )
                    )
                except Exception as multimodal_error:
                    logging.error(f"Multi-modal input failed: {multimodal_error}")
                    # 如果多模態失敗，回退到純文字
                    response = client.models.generate_content(
                        model="gemini-2.0-flash-preview-image-generation",
                        contents=base_prompt,
                        config=GenerateContentConfig(
                            response_modalities=["TEXT", "IMAGE"]
                        )
                    )
            else:
                logging.warning(f"Reference image not found: {reference_image_name}")
                # 如果找不到參考圖像，使用純文字生成
                response = client.models.generate_content(
                    model="gemini-2.0-flash-preview-image-generation",
                    contents=base_prompt,
                    config=GenerateContentConfig(
                        response_modalities=["TEXT", "IMAGE"]
                    )
                )
        else:
            # 沒有參考圖像，使用純文字生成
            response = client.models.generate_content(
                model="gemini-2.0-flash-preview-image-generation",
                contents=base_prompt,
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
            raise HTTPException(status_code=500, detail="No selfie generated")

        # 添加時間戳章（如果啟用）
        final_image_data = image_data
        if request.add_timestamp:
            final_image_data = _add_timestamp_to_image(image_data)
            logging.info("Added timestamp to selfie")

        # 儲存自拍照到 selfies 資料夾
        filename = f"selfie_{int(time.time()*1000)}.png"
        file_path = os.path.join(SELFIES_DIR, filename)

        # 將圖像數據保存到檔案
        with open(file_path, "wb") as f:
            f.write(final_image_data)
        
        # 同時也複製到 generated_images 以便前端訪問
        generated_file_path = os.path.join(GENERATED_DIR, filename)
        with open(generated_file_path, "wb") as f:
            f.write(final_image_data)
        
        url = f"/generated-images/{filename}"
        
        # 處理位置和大小設定
        display_config = _get_display_config_for_selfie(request)

        # 透過WebSocket廣播結果
        await manager.broadcast(json.dumps({
            "type": "generated-image",
            "url": url,
            "caption": f"📸 自拍照：{caption}",
            "display_config": display_config,
            "duration": request.duration,
            "aspect_ratio": request.aspect_ratio
        }))

        return {
            "success": True,
            "url": url,
            "caption": f"📸 自拍照：{caption}",
            "display_config": display_config,
            "duration": request.duration,
            "aspect_ratio": request.aspect_ratio,
            "selfie_filename": filename,
            "reference_image": reference_image_name
        }
        
    except Exception as e:
        logging.error(f"Selfie generation failed: {e}")
        raise HTTPException(status_code=500, detail="Selfie generation failed")


def _get_display_config_for_selfie(request: SelfieRequest) -> dict:
    """根據請求參數生成顯示配置（用於自拍）"""
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
