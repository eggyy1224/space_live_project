import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.camera_control import CameraControlService

from ..endpoints.websocket import manager, murmur_service
from ..endpoints.websocket import \
    save_audio_and_set_url as \
    save_websocket_audio  # 導入 WebSocket 連接管理器和 MurmurService
from ..endpoints.websocket import tts_service

# 設置日誌
logger = logging.getLogger(__name__)

# 創建路由
router = APIRouter()

# Service instance to manage camera presets
camera_service = CameraControlService()


# 定義請求模型
class SendMessageRequest(BaseModel):
    content: str
    message_type: Optional[str] = "chat-message"


class TriggerMurmurRequest(BaseModel):
    topic: Optional[str] = None
    force: Optional[bool] = False


class PlayAudioRequest(BaseModel):
    url: str
    interrupt: Optional[bool] = False


class BackgroundAudioRequest(BaseModel):
    bgmUrl: Optional[str] = None
    sfxUrl: Optional[str] = None
    bgmPlaying: Optional[bool] = None  # 新增：控制BGM播放/暫停


class MurmurModeRequest(BaseModel):
    enabled: bool


class EmotionalTrajectoryRequest(BaseModel):
    duration: float
    keyframes: List[Dict[str, Any]]


class CameraAngles(BaseModel):
    """Camera orientation specified in degrees."""

    pitch: float
    yaw: float
    roll: float
    fov: Optional[float] = None


class CameraTransitionRequest(CameraAngles):
    duration: float = 1.0


class CameraPresetRequest(CameraAngles):
    name: str


class FrontendPresetRequest(BaseModel):
    """Request model for directly loading a frontend camera preset."""

    name: str
    duration: float = 5.0


class BodyAnimationCommand(BaseModel):
    """Request model for controlling body animations."""

    state: Optional[str] = "play"
    animation: Optional[str] = None
    sequence: Optional[List[Dict[str, Any]]] = None
    loop: Optional[bool] = None
    loopCount: Optional[int] = None
    speed: Optional[float] = None
    transitionDuration: Optional[float] = None


@router.post("/control/send-message")
async def send_message_to_frontend(request: SendMessageRequest):
    """
    透過 API 向前端發送消息 (模擬機器人回應)
    """
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="沒有活動的前端連接")

        audio_url_for_message = None
        if request.content:
            logger.info(
                f"API /send-message: 正在為內容進行 TTS: '{request.content[:30]}...'"
            )
            tts_result = await tts_service.synthesize_speech(request.content)
            if tts_result and tts_result.get("audio"):
                audio_base64 = tts_result.get("audio")
                temp_message_obj_for_audio = {
                    "id": f"api-tts-{uuid.uuid4().hex[:8]}",
                }
                await save_websocket_audio(
                    audio_base64, temp_message_obj_for_audio, is_murmur=False
                )
                audio_url_for_message = temp_message_obj_for_audio.get("audioUrl")
                if audio_url_for_message:
                    logger.info(
                        f"API /send-message: TTS 成功，音訊 URL: {audio_url_for_message}"
                    )
                else:
                    logger.warning(
                        "API /send-message: save_websocket_audio 未能生成 audioUrl"
                    )
            else:
                logger.warning(
                    f"API /send-message: TTS 失敗或未返回音訊內容 for: '{request.content[:30]}...'"
                )

        bot_message = {
            "id": f"api-bot-{int(asyncio.get_event_loop().time() * 1000)}",
            "role": "bot",
            "content": request.content,
            "timestamp": datetime.utcnow().isoformat(),
            "audioUrl": audio_url_for_message,
            "isFromAPI": True,
        }

        message_data = {"type": request.message_type, "message": bot_message}

        await manager.broadcast(json.dumps(message_data))

        logger.info(f"API 發送消息到前端: {request.content}")

        return {
            "success": True,
            "message": "消息已發送到前端",
            "connections": len(manager.active_connections),
        }

    except Exception as e:
        logger.error(f"API 發送消息失敗: {e}")
        raise HTTPException(status_code=500, detail=f"發送消息失敗: {str(e)}")


@router.post("/control/trigger-murmur")
async def trigger_murmur(request: TriggerMurmurRequest):
    """
    透過 API 觸發前端的 murmur (自言自語)
    """
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="沒有活動的前端連接")

        # 構建觸發消息 - 這裡我們可以向 WebSocket 發送一個特殊的觸發信號
        trigger_data = {
            "type": "trigger-murmur",
            "payload": {
                "topic": request.topic,
                "force": request.force,
                "source": "api",
            },
        }

        await manager.broadcast(json.dumps(trigger_data))

        logger.info(f"API 觸發 murmur，主題: {request.topic}")

        return {
            "success": True,
            "message": "murmur 觸發信號已發送",
            "topic": request.topic,
        }

    except Exception as e:
        logger.error(f"API 觸發 murmur 失敗: {e}")
        raise HTTPException(status_code=500, detail=f"觸發 murmur 失敗: {str(e)}")


@router.post("/control/murmur-mode")
async def set_murmur_mode(request: MurmurModeRequest):
    """啟用或停用 murmur 功能"""
    try:
        new_state = murmur_service.toggle_enabled(request.enabled)
        logger.info(f"Murmur mode set to {new_state}")
        return {"success": True, "enabled": new_state}
    except Exception as e:
        logger.error(f"API 切換 murmur 模式失敗: {e}")
        raise HTTPException(status_code=500, detail=f"切換 murmur 模式失敗: {str(e)}")


@router.post("/control/play-audio")
async def play_audio_on_frontend(request: PlayAudioRequest):
    """
    透過 API 在前端播放音頻
    """
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="沒有活動的前端連接")

        # 構建音頻播放消息
        audio_data = {
            "type": "play-audio",
            "id": f"api-audio-{uuid.uuid4().hex[:8]}",
            "url": request.url,
            "interrupt": request.interrupt,
        }

        await manager.broadcast(json.dumps(audio_data))

        logger.info(f"API 觸發音頻播放: {request.url}")

        return {"success": True, "message": "音頻播放信號已發送", "url": request.url}

    except Exception as e:
        logger.error(f"API 播放音頻失敗: {e}")
        raise HTTPException(status_code=500, detail=f"播放音頻失敗: {str(e)}")


@router.post("/control/background-audio")
async def background_audio_control(request: BackgroundAudioRequest):
    """透過 API 控制背景音樂或音效"""
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="沒有活動的前端連接")

        audio_data: Dict[str, Any] = {"type": "audio-control"}

        # 處理 BGM URL（包含空字串停止功能）
        if request.bgmUrl is not None:  # 使用 is not None 來包含空字串
            audio_data["bgmUrl"] = request.bgmUrl
            # 如果是空字串，表示停止BGM
            if request.bgmUrl == "":
                audio_data["bgmPlaying"] = False
            else:
                audio_data["bgmPlaying"] = True

        # 處理明確的播放/暫停控制
        if request.bgmPlaying is not None:
            audio_data["bgmPlaying"] = request.bgmPlaying

        # 處理音效 URL
        if request.sfxUrl is not None:
            audio_data["sfxUrl"] = request.sfxUrl

        await manager.broadcast(json.dumps(audio_data))

        logger.info(f"API 發送背景音訊控制: {audio_data}")

        return {"success": True, "message": "背景音訊控制已發送"}

    except Exception as e:
        logger.error(f"API 發送背景音訊控制失敗: {e}")
        raise HTTPException(status_code=500, detail=f"背景音訊控制失敗: {str(e)}")


@router.post("/control/emotion-trajectory")
async def send_emotion_trajectory(request: EmotionalTrajectoryRequest):
    """
    透過 API 發送情緒軌跡到前端
    """
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="沒有活動的前端連接")

        # 構建情緒軌跡消息
        emotion_data = {
            "type": "emotionalTrajectory",
            "payload": {"duration": request.duration, "keyframes": request.keyframes},
        }

        await manager.broadcast(json.dumps(emotion_data))

        logger.info(f"API 發送情緒軌跡，時長: {request.duration}s")

        return {
            "success": True,
            "message": "情緒軌跡已發送",
            "duration": request.duration,
        }

    except Exception as e:
        logger.error(f"API 發送情緒軌跡失敗: {e}")
        raise HTTPException(status_code=500, detail=f"發送情緒軌跡失敗: {str(e)}")


@router.get("/control/status")
async def get_frontend_status():
    """
    獲取前端連接狀態
    """
    return {
        "active_connections": len(manager.active_connections),
        "is_available": len(manager.active_connections) > 0,
        "connections_detail": [
            {"client": str(conn.client)} for conn in manager.active_connections
        ],
    }


@router.post("/control/broadcast")
async def broadcast_custom_message(message: Dict[str, Any]):
    """
    向前端廣播自定義消息
    """
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="沒有活動的前端連接")

        await manager.broadcast(json.dumps(message))

        logger.info(f"API 廣播自定義消息: {message.get('type', 'unknown')}")

        return {
            "success": True,
            "message": "自定義消息已廣播",
            "connections": len(manager.active_connections),
        }

    except Exception as e:
        logger.error(f"API 廣播消息失敗: {e}")
        raise HTTPException(status_code=500, detail=f"廣播消息失敗: {str(e)}")


@router.post("/control/camera/set-angle")
async def set_camera_angle(request: CameraAngles):
    """Set camera orientation instantly on the frontend."""
    if not manager.active_connections:
        raise HTTPException(status_code=503, detail="沒有活動的前端連接")
    message = {"type": "camera-angle", "payload": request.dict()}
    await manager.broadcast(json.dumps(message))
    logger.info(f"Set camera angle: {request.dict()}")
    return {"success": True}


@router.post("/control/camera/transition")
async def transition_camera_angle(request: CameraTransitionRequest):
    """Smoothly transition the camera to the given orientation."""
    if not manager.active_connections:
        raise HTTPException(status_code=503, detail="沒有活動的前端連接")
    message = {
        "type": "camera-transition",
        "payload": request.dict(),
    }
    await manager.broadcast(json.dumps(message))
    logger.info(
        f"Transition camera to {request.pitch},{request.yaw},{request.roll} in {request.duration}s"
    )
    return {"success": True}


@router.post("/control/camera/save-preset")
async def save_camera_preset(request: CameraPresetRequest):
    """Save or update a camera preset on the server."""
    camera_service.save_preset(
        request.name, request.pitch, request.yaw, request.roll, request.fov
    )
    logger.info(f"Saved camera preset: {request.name}")
    return {"success": True}


@router.post("/control/camera/load-preset")
async def load_camera_preset(name: str, duration: float = 1.0):
    """Recall a stored camera preset and broadcast to frontend."""
    preset = camera_service.get_preset(name)
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    payload = {
        **preset,
        "duration": duration,
    }
    message = {"type": "camera-transition", "payload": payload}
    await manager.broadcast(json.dumps(message))
    logger.info(f"Loaded camera preset: {name}")
    return {"success": True}


@router.post("/control/camera/set-frontend-preset")
async def set_frontend_camera_preset(request: FrontendPresetRequest):
    """Broadcast a preset name to the frontend for direct loading."""
    if not request.name:
        raise HTTPException(status_code=422, detail="Preset name required")
    if not manager.active_connections:
        raise HTTPException(status_code=503, detail="沒有活動的前端連接")

    payload = {"name": request.name, "duration": request.duration}
    message = {"type": "set-frontend-camera-preset", "payload": payload}
    await manager.broadcast(json.dumps(message))
    logger.info(f"Broadcast frontend camera preset: {payload}")
    return {"success": True}


@router.post("/control/body-animation")
async def control_body_animation(command: BodyAnimationCommand):
    """Broadcast body animation commands to the frontend."""
    if not manager.active_connections:
        raise HTTPException(status_code=503, detail="沒有活動的前端連接")

    payload = {k: v for k, v in command.dict().items() if v is not None}
    message = {"type": "body-animation", "payload": payload}
    await manager.broadcast(json.dumps(message))
    logger.info(f"Broadcast body animation command: {payload}")
    return {"success": True}


# --- 新增：頭部大小與場景顯示控制 ---


class HeadSizeRequest(BaseModel):
    scaleFactor: float


class SceneDisplayRequest(BaseModel):
    displayScene: bool
    sceneName: Optional[str] = None


VALID_SCENES = {"room-a", "room-b"}


@router.post("/control/head-size")
async def set_head_size(request: HeadSizeRequest):
    """Set the scale of the head model on the frontend."""
    if not manager.active_connections:
        raise HTTPException(status_code=503, detail="沒有活動的前端連接")
    if request.scaleFactor <= 0 or request.scaleFactor > 5:
        raise HTTPException(status_code=400, detail="Invalid scaleFactor")

    message = {"type": "head-size", "scaleFactor": request.scaleFactor}
    await manager.broadcast(json.dumps(message))
    logger.info(f"Set head size: {request.scaleFactor}")
    return {"success": True, "scaleFactor": request.scaleFactor}


@router.post("/control/scene-display")
async def control_scene_display(request: SceneDisplayRequest):
    """Toggle or change the active 3D scene on the frontend."""
    if not manager.active_connections:
        raise HTTPException(status_code=503, detail="沒有活動的前端連接")

    if request.sceneName and request.sceneName not in VALID_SCENES:
        raise HTTPException(status_code=404, detail="Scene not found")

    payload = {"displayScene": request.displayScene, "sceneName": request.sceneName}
    message = {"type": "scene-display", "payload": payload}
    await manager.broadcast(json.dumps(message))
    logger.info(f"Scene display control: {payload}")
    return {"success": True}
