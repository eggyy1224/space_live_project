from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from services.physical_light_control import PhysicalLightControlService
import asyncio

router = APIRouter(prefix="/physical-light", tags=["physical-light"])

class SetBrightnessRequest(BaseModel):
    brightness: int = Field(..., ge=0, le=65535, description="燈光亮度 0~65535")

class SetChannelBrightnessRequest(BaseModel):
    channel: int = Field(..., ge=0, le=3, description="燈光通道 0~3")
    brightness: int = Field(..., description="通道 0 僅接受 0/1；通道 1-3 接受 0~65535")

service = PhysicalLightControlService()

# 亮度 WebSocket 串流的伺服器側保護開關（預設關閉，避免非會話期間噴發訊號）
_BRIGHTNESS_STREAM_ENABLED = False

class ToggleBrightnessStreamRequest(BaseModel):
    enabled: bool = Field(..., description="是否允許透過 WS 傳入的亮度串流覆寫燈光")

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
    """接收前端的亮度流，但以固定頻率（預設 20Hz）批次套用最後一筆，避免高頻連發塞爆 serial 與日誌。"""
    await websocket.accept()

    latest_brightness: int = 0
    applied_brightness: int = -1
    stopped: bool = False
    apply_interval_sec: float = 0.05  # 20Hz

    async def apply_loop():
        nonlocal applied_brightness
        try:
            while not stopped:
                if _BRIGHTNESS_STREAM_ENABLED:
                    # 僅在變化時才下發，避免重複寫入與日誌洪流
                    if latest_brightness != applied_brightness:
                        try:
                            service.set_brightness(latest_brightness)
                            applied_brightness = latest_brightness
                        except Exception:
                            # 出錯就嘗試關閉連線以自我修復
                            service._close_serial_connection()
                await asyncio.sleep(apply_interval_sec)
        finally:
            # 離開時確保關閉 serial
            service._close_serial_connection()

    loop_task = asyncio.create_task(apply_loop())

    try:
        while True:
            data = await websocket.receive_json()
            # 僅更新最新亮度；是否套用由 apply_loop 控制
            br = data.get("brightness")
            if isinstance(br, int):
                if br < 0:
                    br = 0
                elif br > 65535:
                    br = 65535
                latest_brightness = br
    except WebSocketDisconnect:
        print("[WS] physical-light 斷線，清理資源...")
    except Exception as e:
        print(f"[WS] physical-light 控制錯誤: {e}")
    finally:
        print("[WS] physical-light WebSocket 結束，釋放所有資源")
        stopped = True
        try:
            await loop_task
        except Exception:
            pass
        service._close_serial_connection()

@router.post("/toggle-brightness-stream")
def toggle_brightness_stream(req: ToggleBrightnessStreamRequest):
    """啟用/停用來自前端的亮度 WS 串流輸入。
    - 會話開始時應啟用；會話結束時務必停用，避免後續殘留訊號。
    """
    global _BRIGHTNESS_STREAM_ENABLED
    _BRIGHTNESS_STREAM_ENABLED = bool(req.enabled)
    return {"success": True, "enabled": _BRIGHTNESS_STREAM_ENABLED}

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