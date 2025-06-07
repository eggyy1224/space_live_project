import base64
import json
import logging
import os
import time
from io import BytesIO

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


@router.post("/generate-image")
async def generate_image(request: ImageGenerationRequest):
    try:
        # 使用正確的Gemini圖像生成模型和配置
        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=f"Generate an image of: {request.description}",
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
        
        # 透過WebSocket廣播結果
        await manager.broadcast(json.dumps({
            "type": "generated-image", 
            "url": url,
            "caption": caption
        }))
        
        return {"success": True, "url": url, "caption": caption}
        
    except Exception as e:
        logging.error(f"Image generation failed: {e}")
        raise HTTPException(status_code=500, detail="Image generation failed")
