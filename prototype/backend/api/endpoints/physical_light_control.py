from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from services.physical_light_control import PhysicalLightControlService

router = APIRouter(prefix="/physical-light", tags=["physical-light"])

class SetBrightnessRequest(BaseModel):
    brightness: int = Field(..., ge=0, le=65535, description="燈光亮度 0~65535")

class SetChannelBrightnessRequest(BaseModel):
    channel: int = Field(..., ge=0, le=3, description="燈光通道 0~3")
    brightness: int = Field(..., description="通道 0 僅接受 0/1；通道 1-3 接受 0~65535")

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


@router.post("/set-channel-brightness")
def set_channel_brightness(req: SetChannelBrightnessRequest):
    """設定單一路燈亮度。channel 0 僅接受 0/1；channel 1-3 接受 0~65535。"""
    try:
        ok = service.set_channel_brightness(req.channel, req.brightness)
        if not ok:
            raise HTTPException(status_code=500, detail="picoled 控制失敗")
        return {"success": True, "channel": req.channel, "brightness": req.brightness}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"未知錯誤: {e}")

@router.post("/reset-connection")
def reset_serial_connection():
    """手動重置 serial port 連線，用於恢復被鎖死的連線"""
    try:
        success = service.force_reset_connection()
        if success:
            return {"success": True, "message": "Serial port 連線已重置"}
        else:
            raise HTTPException(status_code=500, detail="重置連線失敗")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重置連線時發生錯誤: {e}")

@router.get("/connection-status")
async def get_connection_status():
    """非阻塞連線狀態查詢：不做任何掃描或阻塞操作。"""
    try:
        is_connected = service.is_connected()
        payload = {
            "connected": is_connected,
            "port": service._serial_port if is_connected else None,
            "baudrate": service._baudrate
        }
        return JSONResponse(content=payload)
    except Exception as e:
        payload = {
            "connected": False,
            "error": str(e),
            "port": None,
            "baudrate": service._baudrate
        }
        return JSONResponse(content=payload)
