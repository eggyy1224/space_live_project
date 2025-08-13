from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
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
        print("[WS] physical-light 斷線，清理資源...")
        # 主動釋放 serial port 資源
        service._close_serial_connection()
    except Exception as e:
        print(f"[WS] physical-light 控制錯誤: {e}")
        # 發生例外時也要釋放資源
        service._close_serial_connection()
    finally:
        # 確保無論如何都會釋放資源
        print("[WS] physical-light WebSocket 結束，釋放所有資源")
        service._close_serial_connection()

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