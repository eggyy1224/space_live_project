from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from services.physical_light_control import PhysicalLightControlService

router = APIRouter(prefix="/physical-light", tags=["physical-light"])

class SetBrightnessRequest(BaseModel):
    brightness: int = Field(..., ge=0, le=65535, description="燈光亮度 0~65535")

service = PhysicalLightControlService()

@router.post("/set-brightness")
def set_brightness(req: SetBrightnessRequest):
    try:
        ok = service.set_brightness(req.brightness)
        if not ok:
            raise HTTPException(status_code=500, detail="picoled 控制失敗")
        return {"success": True, "brightness": req.brightness}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"未知錯誤: {e}")

# 新增 WebSocket 端點
@router.websocket("/ws/brightness")
async def websocket_brightness(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            brightness = data.get("brightness")
            if isinstance(brightness, int) and 0 <= brightness <= 65535:
                service.set_brightness(brightness)
    except WebSocketDisconnect:
        print("[WS] physical-light 斷線")
    except Exception as e:
        print(f"[WS] physical-light 控制錯誤: {e}")