import json
import logging
from typing import AsyncIterator

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException

from services.realtime_conversation import RealtimeConversationService

router = APIRouter()

# Global flag for realtime conversation availability
realtime_enabled: bool = True
logger = logging.getLogger(__name__)


async def _iter_chunks(websocket: WebSocket) -> AsyncIterator[bytes]:
    """Yield binary chunks received from the websocket."""
    try:
        while True:
            chunk = await websocket.receive_bytes()
            yield chunk
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected during chunk iteration")
        return
    except Exception as e:
        logger.error(f"Error during chunk iteration: {e}")
        return


@router.websocket("/real-time/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    try:
        logger.info("New real-time WebSocket connection attempt")
        # Check if realtime conversation is enabled
        if not realtime_enabled:
            logger.warning("Realtime conversation is currently disabled - rejecting connection")
            await websocket.close(code=1000)
            return
        await websocket.accept()
        logger.info("Real-time WebSocket connection accepted")
        
        service = RealtimeConversationService()
        connection_active = True
        
        try:
            async for audio in service.stream_conversation(_iter_chunks(websocket)):
                # 檢查連接是否仍然活躍
                if not connection_active:
                    logger.info("Connection no longer active, stopping audio stream")
                    break
                    
                try:
                    await websocket.send_bytes(audio)
                except WebSocketDisconnect:
                    logger.info("WebSocket disconnected during audio send")
                    connection_active = False
                    break
                except Exception as e:
                    logger.error(f"Error sending audio bytes: {e}")
                    connection_active = False
                    break
        except Exception as e:
            logger.error(f"Error in audio stream processing: {e}")
            connection_active = False
                
    except WebSocketDisconnect:
        logger.info("Real-time WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error in real-time WebSocket endpoint: {e}")
    finally:
        try:
            if websocket.client_state.name != "DISCONNECTED":
                await websocket.close()
        except Exception:
            pass


# ----------------- Realtime Conversation Control Endpoints -----------------

@router.post("/real-time/enable")
async def enable_realtime_conversation():
    """啟用實時對話功能 (允許 WebSocket 連線)"""
    global realtime_enabled
    realtime_enabled = True
    logger.info("Realtime conversation enabled via API")
    return {"success": True, "enabled": True}


@router.post("/real-time/disable")
async def disable_realtime_conversation():
    """停用實時對話功能 (拒絕新的 WebSocket 連線)"""
    global realtime_enabled
    realtime_enabled = False
    logger.info("Realtime conversation disabled via API")
    return {"success": True, "enabled": False}


@router.get("/real-time/status")
async def realtime_conversation_status():
    """查詢實時對話功能狀態"""
    return {"enabled": realtime_enabled}
