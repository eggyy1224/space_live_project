import base64
import json
import logging
import os
import time

import google.generativeai as genai
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.config import settings

from .websocket import manager

router = APIRouter()

# Configure Gemini model
genai.configure(api_key=settings.GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-preview-image-generation")

GENERATED_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "generated_images"
)
os.makedirs(GENERATED_DIR, exist_ok=True)


class ImageGenerationRequest(BaseModel):
    description: str


@router.post("/generate-image")
async def generate_image(request: ImageGenerationRequest):
    try:
        response = await model.generate_content_async(request.description)
        part = response.candidates[0].content.parts[0]
        image_bytes = base64.b64decode(part.inline_data.data)
        filename = f"image_{int(time.time()*1000)}.png"
        file_path = os.path.join(GENERATED_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(image_bytes)
        url = f"/generated-images/{filename}"
        await manager.broadcast(json.dumps({"type": "generated-image", "url": url}))
        return {"success": True, "url": url}
    except Exception as e:
        logging.error(f"Image generation failed: {e}")
        raise HTTPException(status_code=500, detail="Image generation failed")
