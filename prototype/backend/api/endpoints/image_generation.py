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
import httpx

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
# 背景圖片目錄 - 同步到前端
FRONTEND_BACKGROUND_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "../frontend/public/background_pictures"
)
os.makedirs(GENERATED_DIR, exist_ok=True)
os.makedirs(SELFIES_DIR, exist_ok=True)
os.makedirs(FRONTEND_BACKGROUND_DIR, exist_ok=True)


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


class BackgroundImageRequest(BaseModel):
    description: str  # 背景圖片描述
    aspect_ratio: Optional[str] = "16:9"  # 螢幕比例，預設 16:9
    # 參考圖像檔名 (可選，從 selfies 或 generated_images 資料夾)
    reference_image: Optional[str] = None  
    # 修改指令 (可選)
    modification: Optional[str] = None  # 例如: "基於這張自拍照創造背景", "融合多張照片的風格"


class MapGenerationRequest(BaseModel):
    latitude: float
    longitude: float
    zoom: int = 14
    size: str = "640x640"
    maptype: Optional[str] = "satellite"
    caption: Optional[str] = "地圖"
    duration: Optional[float] = 15.0


class NasaImageRequest(BaseModel):
    query: str
    caption: Optional[str] = None
    duration: Optional[float] = 15.0


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


@router.post("/generate-background-image")
async def generate_background_image(request: BackgroundImageRequest):
    """生成背景圖片並同步到前端"""
    try:
        # 構建背景圖片描述，針對螢幕比例優化
        aspect_map = {
            "16:9": "in widescreen format (16:9 aspect ratio)",
            "21:9": "in ultra-wide format (21:9 aspect ratio)", 
            "4:3": "in standard format (4:3 aspect ratio)",
            "1:1": "in square format (1:1 aspect ratio)"
        }
        
        aspect_text = aspect_map.get(request.aspect_ratio, "in widescreen format (16:9 aspect ratio)")
        base_prompt = f"Generate a stunning background image: {request.description}. Create it {aspect_text}, suitable for use as a computer screen background or wallpaper."
        
        # 處理參考圖像邏輯
        reference_image_name = request.reference_image
        
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
                    base_prompt += f". Based on the reference image provided, {request.modification}"
                else:
                    base_prompt += ". Based on the reference image provided, create a background that incorporates the style, colors, or visual elements from this image"
                
                logging.info(f"Using reference image for background: {ref_path}, size: {len(reference_image_data)} bytes")
                
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
                    logging.error(f"Multi-modal background generation failed: {multimodal_error}")
                    # 如果多模態失敗，回退到純文字
                    response = client.models.generate_content(
                        model="gemini-2.0-flash-preview-image-generation",
                        contents=base_prompt,
                        config=GenerateContentConfig(
                            response_modalities=["TEXT", "IMAGE"]
                        )
                    )
            else:
                logging.warning(f"Reference image not found for background: {reference_image_name}")
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
            raise HTTPException(status_code=500, detail="No background image generated")

        # 生成檔名
        filename = f"background_{int(time.time()*1000)}.png"
        
        # 儲存到後端 generated_images 資料夾
        backend_file_path = os.path.join(GENERATED_DIR, filename)
        with open(backend_file_path, "wb") as f:
            f.write(image_data)
        
        # 同步到前端 background_pictures 資料夾
        frontend_file_path = os.path.join(FRONTEND_BACKGROUND_DIR, filename)
        with open(frontend_file_path, "wb") as f:
            f.write(image_data)
        
        logging.info(f"Background image saved to: {backend_file_path} and {frontend_file_path}")
        
        # 透過 WebSocket 廣播背景圖片更新
        await manager.broadcast(json.dumps({
            "type": "background-image-generated",
            "filename": filename,
            "caption": caption,
            "aspect_ratio": request.aspect_ratio,
            "description": request.description,
            "timestamp": int(time.time()*1000)
        }))

        return {
            "success": True,
            "filename": filename,
            "caption": caption,
            "aspect_ratio": request.aspect_ratio,
            "backend_path": f"/generated-images/{filename}",
            "frontend_path": f"/background_pictures/{filename}",
            "description": request.description,
            "reference_image": reference_image_name
        }
        
    except Exception as e:
        logging.error(f"Background image generation failed: {e}")
        raise HTTPException(status_code=500, detail="Background image generation failed")


@router.post("/set-background-image")
async def set_background_image(request: dict):
    """直接設置指定的圖片為背景，並同步到前端"""
    try:
        filename = request.get("filename")
        if not filename:
            raise HTTPException(status_code=400, detail="Missing filename")
        
        # 檢查檔案是否存在於 frontend 的 background_pictures 目錄
        frontend_file_path = os.path.join(FRONTEND_BACKGROUND_DIR, filename)
        if not os.path.exists(frontend_file_path):
            raise HTTPException(status_code=404, detail=f"Background image not found: {filename}")
        
        # 透過 WebSocket 廣播背景圖片變更
        await manager.broadcast(json.dumps({
            "type": "background-image-changed",
            "filename": filename,
            "enabled": True,
            "timestamp": int(time.time()*1000)
        }))

        return {
            "success": True,
            "filename": filename,
            "message": f"Background set to {filename}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Set background image failed: {e}")
        raise HTTPException(status_code=500, detail="Set background image failed")


@router.post("/disable-background-image")
async def disable_background_image():
    """停用背景圖片"""
    try:
        # 透過 WebSocket 廣播背景圖片停用
        await manager.broadcast(json.dumps({
            "type": "background-image-changed",
            "filename": None,
            "enabled": False,
            "timestamp": int(time.time()*1000)
        }))

        return {
            "success": True,
            "message": "Background image disabled"
        }
        
    except Exception as e:
        logging.error(f"Disable background image failed: {e}")
        raise HTTPException(status_code=500, detail="Disable background image failed")


@router.post("/generate-map-image")
async def generate_map_image(request: MapGenerationRequest):
    """從 Google Maps Static API 產生一張地圖圖片並顯示"""
    try:
        if not settings.GOOGLE_API_KEY:
            raise HTTPException(status_code=500, detail="Google API key is not configured")

        map_url = (
            f"https://maps.googleapis.com/maps/api/staticmap"
            f"?center={request.latitude},{request.longitude}"
            f"&zoom={request.zoom}"
            f"&size={request.size}"
            f"&maptype={request.maptype}"
            f"&key={settings.GOOGLE_API_KEY}"
        )
        
        async with httpx.AsyncClient() as client:
            response = await client.get(map_url)
            response.raise_for_status()  # Raise an exception for bad status codes
        
        image_data = response.content

        # 儲存圖像檔案
        filename = f"map_{int(time.time()*1000)}.png"
        file_path = os.path.join(GENERATED_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(image_data)
        
        url = f"/generated-images/{filename}"
        
        # 使用一個簡化的 display_config，或可擴充
        display_config = {
            "position": {"top": "50%", "left": "50%", "transform": "translate(-50%, -50%)"},
            "size": {"width": "640px", "height": "640px"}
        }

        # 透過WebSocket廣播結果
        await manager.broadcast(json.dumps({
            "type": "generated-image",
            "url": url,
            "caption": request.caption,
            "display_config": display_config,
            "duration": request.duration
        }))

        return {
            "success": True,
            "url": url,
            "caption": request.caption
        }

    except httpx.HTTPStatusError as e:
        logging.error(f"Failed to fetch map from Google Maps API: {e}")
        # Google回傳的錯誤可能包含有用的資訊
        error_detail = e.response.text
        try:
            if "API key not valid" in error_detail or "ApiTarget.ENABLE" in error_detail:
                 raise HTTPException(status_code=400, detail="Google Maps API error: The API key is invalid or the Maps Static API is not enabled.")
            raise HTTPException(status_code=e.response.status_code, detail=f"Google Maps API error: {error_detail}")
        except Exception:
             raise HTTPException(status_code=e.response.status_code, detail=f"Failed to fetch map from Google Maps API: {error_detail}")
    except Exception as e:
        logging.error(f"Map generation failed: {e}")
        raise HTTPException(status_code=500, detail="Map generation failed")


@router.post("/search-nasa-image")
async def search_nasa_image(request: NasaImageRequest):
    """從 NASA Image and Video Library API 搜尋圖片並顯示"""
    try:
        nasa_api_url = "https://images-api.nasa.gov/search"
        params = {"q": request.query, "media_type": "image"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(nasa_api_url, params=params)
            response.raise_for_status()
        
        data = response.json()
        items = data.get("collection", {}).get("items", [])
        
        if not items:
            raise HTTPException(status_code=404, detail=f"No images found for query: '{request.query}'")

        # 選擇第一張圖片
        first_item = items[0]
        image_url = first_item.get("links", [{}])[0].get("href")
        image_title = first_item.get("data", [{}])[0].get("title")

        if not image_url:
            raise HTTPException(status_code=404, detail="Could not find image URL in NASA API response.")
            
        caption = request.caption or image_title or "NASA Image"

        # 使用一個簡化的 display_config
        display_config = {
            "position": {"top": "50%", "left": "50%", "transform": "translate(-50%, -50%)"},
            "size": {"width": "auto", "height": "auto", "max-width": "80vw", "max-height": "80vh"}
        }

        # 透過WebSocket廣播結果
        await manager.broadcast(json.dumps({
            "type": "generated-image",
            "url": image_url,
            "caption": caption,
            "display_config": display_config,
            "duration": request.duration
        }))

        return {
            "success": True,
            "url": image_url,
            "caption": caption
        }

    except httpx.HTTPStatusError as e:
        logging.error(f"Failed to fetch image from NASA API: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=f"NASA API error: {e.response.text}")
    except Exception as e:
        logging.error(f"NASA image search failed: {e}")
        raise HTTPException(status_code=500, detail="NASA image search failed")
