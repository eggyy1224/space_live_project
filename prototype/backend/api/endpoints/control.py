import asyncio
import json
import logging
import uuid
import os
import requests
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
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

# Freesound API 配置
FREESOUND_API_KEY = os.getenv("FREESOUND_API_KEY")
FREESOUND_API_URL = "https://freesound.org/apiv2"

# 生成音效的保存目錄
GENERATED_SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "../../../frontend/public/audio/generated_sounds")

# 創建目錄如果不存在
os.makedirs(GENERATED_SOUNDS_DIR, exist_ok=True)

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
    volume: Optional[float] = None     # 新增：BGM 音量控制


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


class DanceGroupRequest(BaseModel):
    """Request model for controlling the dance group."""
    formation: str = Field(..., description="The formation of the dancers (e.g., 'circle', 'grid', 'line').")
    dancerCount: int = Field(..., gt=0, description="The number of dancers.")
    position: List[float] = Field(..., min_items=3, max_items=3, description="The [x, y, z] position of the group.")
    scale: float = Field(..., gt=0, description="The scale of each dancer.")


class GenerateSoundEffectRequest(BaseModel):
    """Request model for generating sound effects using Freesound."""
    prompt: str = Field(..., description="Text description of the sound effect to search for on Freesound")
    duration_seconds: Optional[float] = Field(3.0, ge=0.5, le=22.0, description="Maximum duration in seconds (0.5-22.0)")
    filename: Optional[str] = Field(None, description="Custom filename (without extension)")
    play_immediately: Optional[bool] = Field(True, description="Whether to play the sound immediately after download")


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
                if audio_base64:  # 確保 audio_base64 不是 None
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

        # 新增：處理音量
        if request.volume is not None:
            audio_data["volume"] = request.volume

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


# ----------------- Realtime Voice Control -----------------

class RealtimeVoiceControlRequest(BaseModel):
    """Request model for controlling realtime voice mode on the frontend."""
    action: str  # 'start' or 'stop'

@router.post("/control/realtime-voice")
async def control_realtime_voice(request: RealtimeVoiceControlRequest):
    """Broadcast start/stop command for realtime voice mode to frontend."""
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="沒有活動的前端連接")
        if request.action not in {"start", "stop"}:
            raise HTTPException(status_code=400, detail="action 必須是 'start' 或 'stop'")

        message = {
            "type": "realtime-voice-control",
            "action": request.action,
            "source": "api"
        }
        await manager.broadcast(json.dumps(message))
        logger.info(f"Broadcasted realtime voice control: {request.action}")
        return {"success": True, "action": request.action, "connections": len(manager.active_connections)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Realtime voice control failed: {e}")
        raise HTTPException(status_code=500, detail=f"Realtime voice control failed: {str(e)}")

# --- 新增：頭部大小與場景顯示控制 ---


class HeadSizeRequest(BaseModel):
    scaleFactor: float


class SceneDisplayRequest(BaseModel):
    displayScene: bool
    sceneName: Optional[str] = None
    # 房間變換參數
    position: Optional[List[float]] = None  # [x, y, z]
    rotation: Optional[List[float]] = None  # [x, y, z] 以度為單位
    scale: Optional[List[float]] = None     # [x, y, z] 或 [uniform] 統一縮放


VALID_SCENES = {"6面房間", "6面房間A"}


@router.post("/control/head-size")
async def set_head_size(request: HeadSizeRequest):
    """Set the scale of the head model on the frontend."""
    if not manager.active_connections:
        raise HTTPException(status_code=503, detail="沒有活動的前端連接")
    if request.scaleFactor <= 0 or request.scaleFactor > 20:
        raise HTTPException(status_code=400, detail="Invalid scaleFactor")

    message = {"type": "head-size", "scaleFactor": request.scaleFactor}
    await manager.broadcast(json.dumps(message))
    logger.info(f"Set head size: {request.scaleFactor}")
    return {"success": True, "scaleFactor": request.scaleFactor}


@router.post("/control/scene-display")
async def control_scene_display(request: SceneDisplayRequest):
    """
    控制3D場景 (如太空艙) 的顯示與變換
    """
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="No active frontend connections")

        payload = {
            "type": "scene-display",  # 統一為 scene-display
            "payload": {
                "displayScene": request.displayScene,
                "sceneName": request.sceneName,
                "position": request.position,
                "rotation": request.rotation,
                "scale": request.scale,
            }
        }

        await manager.broadcast(json.dumps(payload))

        logger.info(f"Broadcasted scene control: display={request.displayScene}, scene={request.sceneName}")
        return {"success": True, "message": "Scene control command sent"}
    except Exception as e:
        logger.error(f"Failed to control scene display: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 在文件末尾新增角色控制相關的請求模型和端點

class CharacterScaleRequest(BaseModel):
    """角色縮放控制請求模型"""
    scale: float  # 縮放比例，範圍 0.1-15.0

class CharacterPositionRequest(BaseModel):
    """角色位置控制請求模型"""
    position: List[float]  # [x, y, z] 座標

class CharacterRotationRequest(BaseModel):
    """角色旋轉控制請求模型"""
    rotation: List[float]  # [x, y, z] 旋轉角度 (弧度)

class CharacterOutfitRequest(BaseModel):
    """角色服裝控制請求模型"""
    outfit_morphs: Dict[str, float]  # morph target 名稱和數值的字典

class CharacterAnimationRequest(BaseModel):
    """角色動畫控制請求模型"""
    animation: str  # 動畫名稱
    loop: Optional[bool] = True
    speed: Optional[float] = 1.0

class CharacterAnimationMixRequest(BaseModel):
    """角色動畫混合控制請求模型"""
    animations: List[Dict[str, Any]]  # 動畫配置列表 [{"name": "run", "weight": 0.7, "loop": True, "speed": 1.0}]
    transitionDuration: Optional[float] = 0.5  # 切換到混合狀態的過渡時間
    blendMode: Optional[str] = "normal"  # normal, additive, override

class CharacterVisibilityRequest(BaseModel):
    """角色可見性控制請求模型"""
    visible: bool

class CharacterTransformResetRequest(BaseModel):
    """角色變換重置請求模型"""
    reset_position: Optional[bool] = True
    reset_rotation: Optional[bool] = True
    reset_scale: Optional[bool] = True


# === 環境光照控制請求模型 ===
class EnvironmentPresetRequest(BaseModel):
    """環境光照預設控制請求模型"""
    preset: str  # studio, sunset, dawn, night, warehouse, forest, apartment, city, park, lobby


class EnvironmentIntensityRequest(BaseModel):
    """環境光照強度控制請求模型"""
    intensity: float  # 範圍 0.1-3.0


class EnvironmentBackgroundRequest(BaseModel):
    """環境背景顯示控制請求模型"""
    background: bool  # 是否顯示環境作為背景


class EnvironmentConfigRequest(BaseModel):
    """環境光照完整配置請求模型"""
    preset: Optional[str] = None  # 環境預設
    intensity: Optional[float] = None  # 光照強度 (0.1-3.0)
    background: Optional[bool] = None  # 背景顯示


class EnvironmentResetRequest(BaseModel):
    """環境光照重置請求模型"""
    reset_to_defaults: bool = True

@router.post("/control/character/scale")
async def set_character_scale(request: CharacterScaleRequest):
    """設置角色縮放比例"""
    if not manager.active_connections:
        raise HTTPException(status_code=503, detail="沒有活動的前端連接")

    # 驗證縮放範圍
    if not (0.1 <= request.scale <= 15.0):
        raise HTTPException(status_code=400, detail="縮放比例必須在 0.1 到 15.0 之間")

    try:
        # 構建控制消息
        control_data = {
            "type": "character-control",
            "action": "scale",
            "payload": {
                "scale": request.scale
            }
        }

        await manager.broadcast(json.dumps(control_data))

        logger.info(f"API 設置角色縮放: {request.scale}")

        return {
            "success": True,
            "message": "角色縮放已設置",
            "scale": request.scale,
            "connections": len(manager.active_connections),
        }

    except Exception as e:
        logger.error(f"API 設置角色縮放失敗: {e}")
        raise HTTPException(status_code=500, detail=f"設置角色縮放失敗: {str(e)}")

@router.post("/control/character/position")
async def set_character_position(request: CharacterPositionRequest):
    """設置角色位置"""
    if not manager.active_connections:
        raise HTTPException(status_code=503, detail="沒有活動的前端連接")

    # 驗證位置參數
    if len(request.position) != 3:
        raise HTTPException(status_code=400, detail="位置必須包含 3 個座標值 [x, y, z]")

    try:
        # 構建控制消息
        control_data = {
            "type": "character-control",
            "action": "position",
            "payload": {
                "position": request.position
            }
        }

        await manager.broadcast(json.dumps(control_data))

        logger.info(f"API 設置角色位置: {request.position}")

        return {
            "success": True,
            "message": "角色位置已設置",
            "position": request.position,
            "connections": len(manager.active_connections),
        }

    except Exception as e:
        logger.error(f"API 設置角色位置失敗: {e}")
        raise HTTPException(status_code=500, detail=f"設置角色位置失敗: {str(e)}")

@router.post("/control/character/rotation")
async def set_character_rotation(request: CharacterRotationRequest):
    """設置角色旋轉"""
    if not manager.active_connections:
        raise HTTPException(status_code=503, detail="沒有活動的前端連接")

    # 驗證旋轉參數
    if len(request.rotation) != 3:
        raise HTTPException(status_code=400, detail="旋轉必須包含 3 個角度值 [x, y, z]")

    try:
        # 構建控制消息
        control_data = {
            "type": "character-control",
            "action": "rotation",
            "payload": {
                "rotation": request.rotation
            }
        }

        await manager.broadcast(json.dumps(control_data))

        logger.info(f"API 設置角色旋轉: {request.rotation}")

        return {
            "success": True,
            "message": "角色旋轉已設置",
            "rotation": request.rotation,
            "connections": len(manager.active_connections),
        }

    except Exception as e:
        logger.error(f"API 設置角色旋轉失敗: {e}")
        raise HTTPException(status_code=500, detail=f"設置角色旋轉失敗: {str(e)}")

@router.post("/control/character/outfit")
async def set_character_outfit(request: CharacterOutfitRequest):
    """控制角色服裝 (outfit_shoes030_1 等 morph targets)"""
    if not manager.active_connections:
        raise HTTPException(status_code=503, detail="沒有活動的前端連接")

    # 驗證 morph target 數值範圍
    for name, value in request.outfit_morphs.items():
        if not (0.0 <= value <= 1.0):
            raise HTTPException(
                status_code=400, 
                detail=f"Morph target '{name}' 的數值必須在 0.0 到 1.0 之間"
            )

    try:
        # 構建控制消息
        control_data = {
            "type": "character-control",
            "action": "outfit",
            "payload": {
                "morphTargets": request.outfit_morphs
            }
        }

        await manager.broadcast(json.dumps(control_data))

        logger.info(f"API 設置角色服裝: {request.outfit_morphs}")

        return {
            "success": True,
            "message": "角色服裝已設置",
            "outfit_morphs": request.outfit_morphs,
            "connections": len(manager.active_connections),
        }

    except Exception as e:
        logger.error(f"API 設置角色服裝失敗: {e}")
        raise HTTPException(status_code=500, detail=f"設置角色服裝失敗: {str(e)}")

@router.post("/control/character/animation")
async def set_character_animation(request: CharacterAnimationRequest):
    """設置角色動畫"""
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="沒有活動的前端連接")

        # 構建控制消息
        control_data = {
            "type": "character-control",
            "action": "animation",
            "payload": {
                "animation": request.animation,
                "loop": request.loop,
                "speed": request.speed
            }
        }

        await manager.broadcast(json.dumps(control_data))

        logger.info(f"API 設置角色動畫: {request.animation}")

        return {
            "success": True,
            "message": "角色動畫已設置",
            "animation": request.animation,
            "loop": request.loop,
            "speed": request.speed,
            "connections": len(manager.active_connections),
        }

    except Exception as e:
        logger.error(f"API 設置角色動畫失敗: {e}")
        raise HTTPException(status_code=500, detail=f"設置角色動畫失敗: {str(e)}")

@router.post("/control/character/animation-mix")
async def set_character_animation_mix(request: CharacterAnimationMixRequest):
    """設置角色動畫混合"""
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="沒有活動的前端連接")

        # 驗證動畫配置
        total_weight = 0
        for anim_config in request.animations:
            if not anim_config.get("name"):
                raise HTTPException(status_code=400, detail="每個動畫配置必須包含 'name' 欄位")
            weight = anim_config.get("weight", 1.0)
            if not isinstance(weight, (int, float)) or weight < 0 or weight > 1:
                raise HTTPException(status_code=400, detail="動畫權重必須在 0-1 之間")
            total_weight += weight
        
        # 警告權重總和異常（但不阻止執行）
        if total_weight > 1.1:
            logger.warning(f"動畫權重總和 {total_weight:.2f} 超過 1.0，可能導致不自然的效果")

        # 構建控制消息
        control_data = {
            "type": "character-control",
            "action": "animation-mix",
            "payload": {
                "animations": request.animations,
                "transitionDuration": request.transitionDuration,
                "blendMode": request.blendMode
            }
        }

        await manager.broadcast(json.dumps(control_data))

        logger.info(f"API 設置角色動畫混合: {len(request.animations)} 個動畫")

        return {
            "success": True,
            "message": "角色動畫混合已設置",
            "animationCount": len(request.animations),
            "totalWeight": total_weight,
            "blendMode": request.blendMode,
            "connections": len(manager.active_connections),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API 設置角色動畫混合失敗: {e}")
        raise HTTPException(status_code=500, detail=f"設置角色動畫混合失敗: {str(e)}")

@router.post("/control/character/visibility")
async def set_character_visibility(request: CharacterVisibilityRequest):
    """設置角色可見性"""
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="沒有活動的前端連接")

        # 構建控制消息
        control_data = {
            "type": "character-control",
            "action": "visibility",
            "payload": {
                "visible": request.visible
            }
        }

        await manager.broadcast(json.dumps(control_data))

        logger.info(f"API 設置角色可見性: {request.visible}")

        return {
            "success": True,
            "message": "角色可見性已設置",
            "visible": request.visible,
            "connections": len(manager.active_connections),
        }

    except Exception as e:
        logger.error(f"API 設置角色可見性失敗: {e}")
        raise HTTPException(status_code=500, detail=f"設置角色可見性失敗: {str(e)}")

@router.post("/control/character/reset-transform")
async def reset_character_transform(request: CharacterTransformResetRequest):
    """重置角色變換 (位置、旋轉、縮放)"""
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="沒有活動的前端連接")

        # 構建控制消息
        control_data = {
            "type": "character-control",
            "action": "reset-transform",
            "payload": {
                "resetPosition": request.reset_position,
                "resetRotation": request.reset_rotation,
                "resetScale": request.reset_scale
            }
        }

        await manager.broadcast(json.dumps(control_data))

        logger.info(f"API 重置角色變換")

        return {
            "success": True,
            "message": "角色變換已重置",
            "reset_position": request.reset_position,
            "reset_rotation": request.reset_rotation,
            "reset_scale": request.reset_scale,
            "connections": len(manager.active_connections),
        }

    except Exception as e:
        logger.error(f"API 重置角色變換失敗: {e}")
        raise HTTPException(status_code=500, detail=f"重置角色變換失敗: {str(e)}")

@router.get("/control/character/status")
async def get_character_status():
    """獲取角色當前狀態"""
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="沒有活動的前端連接")

        # 構建狀態查詢消息
        control_data = {
            "type": "character-control",
            "action": "get-status",
            "payload": {}
        }

        await manager.broadcast(json.dumps(control_data))

        logger.info("API 查詢角色狀態")

        return {
            "success": True,
            "message": "角色狀態查詢已發送",
            "connections": len(manager.active_connections),
        }

    except Exception as e:
        logger.error(f"API 查詢角色狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=f"查詢角色狀態失敗: {str(e)}")

# === 環境光照控制端點 ===

@router.post("/control/environment/preset")
async def set_environment_preset(request: EnvironmentPresetRequest):
    """設定環境光照預設"""
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="沒有活動的前端連接")

        # 驗證預設名稱
        valid_presets = ["studio", "sunset", "dawn", "night", "warehouse", "forest", "apartment", "city", "park", "lobby"]
        if request.preset not in valid_presets:
            raise HTTPException(status_code=400, detail=f"無效的環境預設。支援的預設: {', '.join(valid_presets)}")

        # 構建控制消息
        control_message = {
            "type": "environment-preset",
            "payload": {
                "preset": request.preset,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "api"
            }
        }

        await manager.broadcast(json.dumps(control_message))
        logger.info(f"API 設定環境預設: {request.preset}")

        return {
            "success": True,
            "message": f"環境預設已設定為: {request.preset}",
            "preset": request.preset,
            "connections": len(manager.active_connections)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API 設定環境預設失敗: {e}")
        raise HTTPException(status_code=500, detail=f"設定環境預設失敗: {str(e)}")


@router.post("/control/environment/intensity")
async def set_environment_intensity(request: EnvironmentIntensityRequest):
    """設定環境光照強度"""
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="沒有活動的前端連接")

        # 驗證強度範圍
        if not (0.1 <= request.intensity <= 3.0):
            raise HTTPException(status_code=400, detail="光照強度必須在0.1到3.0之間")

        # 構建控制消息
        control_message = {
            "type": "environment-intensity",
            "payload": {
                "intensity": request.intensity,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "api"
            }
        }

        await manager.broadcast(json.dumps(control_message))
        logger.info(f"API 設定環境光照強度: {request.intensity}")

        return {
            "success": True,
            "message": f"環境光照強度已設定為: {request.intensity}",
            "intensity": request.intensity,
            "connections": len(manager.active_connections)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API 設定環境光照強度失敗: {e}")
        raise HTTPException(status_code=500, detail=f"設定環境光照強度失敗: {str(e)}")


@router.post("/control/environment/background")
async def set_environment_background(request: EnvironmentBackgroundRequest):
    """設定環境背景顯示"""
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="沒有活動的前端連接")

        # 構建控制消息
        control_message = {
            "type": "environment-background",
            "payload": {
                "background": request.background,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "api"
            }
        }

        await manager.broadcast(json.dumps(control_message))
        logger.info(f"API 設定環境背景顯示: {request.background}")

        return {
            "success": True,
            "message": f"環境背景顯示已設定為: {'開啟' if request.background else '關閉'}",
            "background": request.background,
            "connections": len(manager.active_connections)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API 設定環境背景顯示失敗: {e}")
        raise HTTPException(status_code=500, detail=f"設定環境背景顯示失敗: {str(e)}")


@router.post("/control/environment/config")
async def set_environment_config(request: EnvironmentConfigRequest):
    """設定環境光照完整配置（批量設定）"""
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="沒有活動的前端連接")

        # 驗證輸入
        valid_presets = ["studio", "sunset", "dawn", "night", "warehouse", "forest", "apartment", "city", "park", "lobby"]
        
        if request.preset is not None and request.preset not in valid_presets:
            raise HTTPException(status_code=400, detail=f"無效的環境預設。支援的預設: {', '.join(valid_presets)}")
        
        if request.intensity is not None and not (0.1 <= request.intensity <= 3.0):
            raise HTTPException(status_code=400, detail="光照強度必須在0.1到3.0之間")

        # 構建配置對象
        config = {}
        if request.preset is not None:
            config["preset"] = request.preset
        if request.intensity is not None:
            config["intensity"] = request.intensity
        if request.background is not None:
            config["background"] = request.background

        if not config:
            raise HTTPException(status_code=400, detail="至少需要提供一個配置參數")

        # 構建控制消息
        control_message = {
            "type": "environment-config",
            "payload": {
                **config,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "api"
            }
        }

        await manager.broadcast(json.dumps(control_message))
        logger.info(f"API 設定環境光照配置: {config}")

        return {
            "success": True,
            "message": "環境光照配置已更新",
            "config": config,
            "connections": len(manager.active_connections)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API 設定環境光照配置失敗: {e}")
        raise HTTPException(status_code=500, detail=f"設定環境光照配置失敗: {str(e)}")


@router.post("/control/environment/reset")
async def reset_environment_settings(request: EnvironmentResetRequest):
    """重置環境光照設定到預設值"""
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="沒有活動的前端連接")

        # 構建重置消息
        control_message = {
            "type": "environment-reset",
            "payload": {
                "reset_to_defaults": request.reset_to_defaults,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "api"
            }
        }

        await manager.broadcast(json.dumps(control_message))
        logger.info("API 重置環境光照設定")

        return {
            "success": True,
            "message": "環境光照設定已重置為預設值",
            "defaults": {
                "preset": "studio",
                "intensity": 1.0,
                "background": False
            },
            "connections": len(manager.active_connections)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API 重置環境光照設定失敗: {e}")
        raise HTTPException(status_code=500, detail=f"重置環境光照設定失敗: {str(e)}")


@router.get("/control/environment/status")
async def get_environment_status():
    """獲取環境光照狀態"""
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="沒有活動的前端連接")

        # 構建狀態查詢消息
        status_request = {
            "type": "environment-status-request",
            "payload": {
                "timestamp": datetime.utcnow().isoformat(),
                "source": "api"
            }
        }

        await manager.broadcast(json.dumps(status_request))
        logger.info("API 請求環境光照狀態")

        # 注意：實際狀態會通過WebSocket回傳，這裡只返回請求確認
        return {
            "success": True,
            "message": "環境光照狀態查詢已發送",
            "note": "實際狀態將通過WebSocket回傳",
            "connections": len(manager.active_connections)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API 獲取環境光照狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取環境光照狀態失敗: {str(e)}")


@router.post("/control/dance_group")
async def control_dance_group(request: DanceGroupRequest):
    """Controls the formation, count, position, and scale of the dance group."""
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="No active frontend connections.")

        message_data = {
            "type": "dance_group_update",
            "payload": request.dict()
        }

        await manager.broadcast(json.dumps(message_data))

        logger.info(f"API broadcasting dance group update: {request.dict()}")

        return {
            "success": True,
            "message": "Dance group update broadcasted to frontend.",
            "data": request.dict()
        }

    except Exception as e:
        logger.error(f"API failed to control dance group: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to control dance group: {str(e)}")


@router.post("/control/generate-sound-effect")
async def generate_sound_effect(request: GenerateSoundEffectRequest):
    """
    從 Freesound 搜尋並下載音效。
    """
    if not FREESOUND_API_KEY:
        raise HTTPException(status_code=500, detail="Freesound API key is not configured.")

    try:
        # 1. 搜尋音效
        search_url = f"{FREESOUND_API_URL}/search/text/"
        params = {
            "query": request.prompt,
            "filter": f"duration:[0.5 TO {request.duration_seconds}]",
            "sort": "rating_desc",
            "fields": "id,name,previews",
            "token": FREESOUND_API_KEY
        }
        
        logger.info(f"Searching Freesound for: '{request.prompt}'")
        search_response = requests.get(search_url, params=params, timeout=15)
        search_response.raise_for_status()
        search_results = search_response.json()

        if not search_results or not search_results.get("results"):
            raise HTTPException(status_code=404, detail=f"No sounds found for prompt: '{request.prompt}'")

        # 2. 選擇第一個音效並取得預覽 URL
        best_result = search_results["results"][0]
        sound_name = best_result.get("name")
        preview_url = best_result.get("previews", {}).get("preview-hq-mp3")

        if not preview_url:
            raise HTTPException(status_code=404, detail=f"No high-quality MP3 preview found for sound: {sound_name}")

        logger.info(f"Found sound: '{sound_name}'. Downloading from: {preview_url}")
        
        # 3. 下載音效
        download_response = requests.get(preview_url, timeout=20)
        download_response.raise_for_status()
        audio_data = download_response.content

        # 4. 儲存並播放
        if request.filename:
            filename = f"{request.filename}.mp3"
        else:
            # 使用 sound name 和 id 創建一個較為乾淨的檔名
            clean_name = "".join(e for e in sound_name if e.isalnum() or e in " _-").strip()
            filename = f"freesound_{clean_name}_{best_result['id']}.mp3"
        
        file_path = os.path.join(GENERATED_SOUNDS_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(audio_data)

        logger.info(f"Sound effect saved to: {file_path}")
        
        # 透過 WebSocket 廣播播放指令
        if request.play_immediately:
            audio_url = f"/audio/generated_sounds/{filename}"
            # 修正：使用 'audio-control' 型別和 'sfxUrl' 欄位，以符合前端的音訊播放邏輯
            await manager.broadcast(json.dumps({
                "type": "audio-control",
                "sfxUrl": audio_url
            }))
            logger.info(f"Broadcasted play command for SFX: {audio_url}")
            
        return {
            "success": True,
            "message": f"Successfully downloaded sound effect '{sound_name}'",
            "filename": filename,
            "path": f"/audio/generated_sounds/{filename}"
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Freesound API request failed: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to communicate with Freesound: {e}")
    except Exception as e:
        logger.error(f"Sound effect generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
