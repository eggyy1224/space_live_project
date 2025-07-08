#!/usr/bin/env python3
"""
太空直播系統 MCP 服務器
提供與太空站角色互動的工具
"""

import json
import sys
import requests
from fastmcp import FastMCP
from typing import List

# 後端 API 設定
BASE_URL = "http://localhost:8000"
SEND_MESSAGE_ENDPOINT = f"{BASE_URL}/api/control/send-message"

# 建立 MCP 服務器
mcp = FastMCP("SpaceLiveServer")

@mcp.tool()
def send_message(content: str, message_type: str = "chat-message") -> str:
    """
    向太空直播系統發送訊息，讓 AI 角色說話
    
    Args:
        content: 要發送的訊息內容
        message_type: 訊息類型，預設為 "chat-message"
    
    Returns:
        操作結果描述
    """
    try:
        payload = {
            "content": content,
            "message_type": message_type
        }
        
        response = requests.post(SEND_MESSAGE_ENDPOINT, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return f"✅ 訊息發送成功！連接數: {result.get('connections', 0)}。AI 角色說: \"{content}\""
        else:
            return f"❌ 發送失敗 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except requests.exceptions.Timeout:
        return "❌ 請求超時，服務器可能忙碌中"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def set_emotion(emotion: str, duration: float = 3.0) -> str:
    """
    設置 AI 角色的表情
    
    Args:
        emotion: 表情名稱，可用選項包括：
            基礎狀態: neutral, listening, thinking
            正面情緒: happy, joyful, content, amused, excited, interested, affectionate, proud, relieved, grateful, hopeful, serene, playful, triumphant
            負面情緒: sad, gloomy, disappointed, worried, angry, irritated, frustrated, fearful, nervous, disgusted, contemptuous, pain, embarrassed, jealous, regretful, guilty, ashamed, despairing, spiteful
            認知狀態: surprised, confused, skeptical, bored, sleepy, scheming, determined, impatient, shy, bashful, smug, awe, doubtful
        duration: 表情持續時間（秒），預設 3.0 秒
    
    Returns:
        操作結果描述
    """
    try:
        # 構建表情軌跡 payload
        payload = {
            "duration": duration,
            "keyframes": [
                {"tag": emotion, "proportion": 1.0}
            ]
        }
        
        emotion_endpoint = f"{BASE_URL}/api/control/emotion-trajectory"
        response = requests.post(emotion_endpoint, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return f"✅ 表情設置成功！AI 角色現在表現為 '{emotion}' 表情，持續 {duration} 秒"
        else:
            return f"❌ 表情設置失敗 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except requests.exceptions.Timeout:
        return "❌ 請求超時，服務器可能忙碌中"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
async def emotion_transition(start_emotion: str, end_emotion: str, duration: float = 5.0):
    """
    創建表情轉換動畫，從一種表情平滑過渡到另一種表情
    
    Args:
        start_emotion: 起始表情，參考 set_emotion 工具的可用表情列表
        end_emotion: 結束表情，參考 set_emotion 工具的可用表情列表
        duration: 轉換持續時間（秒），預設 5.0 秒
    
    Returns:
        操作結果描述
    """
    try:
        # 構建表情軌跡 payload，從起始表情過渡到結束表情
        payload = {
            "duration": duration,
            "keyframes": [
                {"tag": start_emotion, "proportion": 0.0},
                {"tag": end_emotion, "proportion": 1.0}
            ]
        }
        
        emotion_endpoint = f"{BASE_URL}/api/control/emotion-trajectory"
        response = requests.post(emotion_endpoint, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return f"✅ 表情轉換成功！AI 角色從 '{start_emotion}' 轉換到 '{end_emotion}'，轉換時間 {duration} 秒"
        else:
            return f"❌ 表情轉換失敗 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except requests.exceptions.Timeout:
        return "❌ 請求超時，服務器可能忙碌中"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def set_main_character_animation(animation: str, loop: bool = True, speed: float = 1.0) -> str:
    """
    控制主要 AI 角色的動畫動作
    
    Args:
        animation: 動畫名稱，可用選項包括：
            運動類: 運動1, 運動2, 飛1, 飛2
            日常類: 漂浮, 漂浮2, 划手機, 臥躺, 不穩, Tpose
            舞蹈類: 舞步1, 舞步2, 舞步3
        loop: 是否循環播放，預設為 True
        speed: 播放速度，預設為 1.0 (正常速度)
    
    Returns:
        操作結果描述
    """
    try:
        # 構建角色動畫 payload
        payload = {
            "animation": animation,
            "loop": loop,
            "speed": speed
        }
        
        animation_endpoint = f"{BASE_URL}/api/control/character/animation"
        response = requests.post(animation_endpoint, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            loop_text = "循環播放" if loop else "播放一次"
            return f"✅ 主角動畫設置成功！AI 角色現在執行 '{animation}' 動作，{loop_text}，速度 {speed}x"
        else:
            return f"❌ 主角動畫設置失敗 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except requests.exceptions.Timeout:
        return "❌ 請求超時，服務器可能忙碌中"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def set_main_character_animation_mix(animations_config: str, blend_mode: str = "normal", transition_duration: float = 0.5) -> str:
    """
    控制主要 AI 角色的多重動畫混合，可以同時播放多個動畫並控制它們的權重
    
    Args:
        animations_config: 動畫配置的 JSON 字串，格式為:
            [{"name": "動畫名稱", "weight": 權重值, "loop": 是否循環, "speed": 播放速度}, ...]
            範例: '[{"name": "運動1", "weight": 0.7, "loop": true, "speed": 1.0}, {"name": "舞步1", "weight": 0.3, "loop": true, "speed": 1.2}]'
            可用動畫: 運動1, 運動2, 飛1, 飛2, 漂浮, 漂浮2, 划手機, 臥躺, 不穩, Tpose, 舞步1, 舞步2, 舞步3
            權重範圍: 0.0-1.0，建議總權重保持在 1.0 左右
        blend_mode: 混合模式，可選項: "normal", "additive", "override"，預設為 "normal"
        transition_duration: 切換到混合模式的過渡時間（秒），預設為 0.5
    
    Returns:
        操作結果描述
    """
    try:
        # 解析動畫配置 JSON
        import json
        try:
            animations = json.loads(animations_config)
        except json.JSONDecodeError as e:
            return f"❌ 動畫配置 JSON 格式錯誤: {str(e)}"
        
        # 驗證動畫配置格式
        if not isinstance(animations, list) or len(animations) == 0:
            return "❌ 動畫配置必須是非空的陣列"
        
        # 驗證每個動畫配置
        total_weight = 0
        valid_animations = []
        for anim in animations:
            if not isinstance(anim, dict):
                return "❌ 每個動畫配置必須是對象"
            
            if "name" not in anim or "weight" not in anim:
                return "❌ 每個動畫配置必須包含 'name' 和 'weight' 欄位"
            
            weight = anim.get("weight", 1.0)
            if not isinstance(weight, (int, float)) or weight < 0 or weight > 1:
                return f"❌ 動畫 '{anim['name']}' 的權重必須在 0-1 之間"
            
            total_weight += weight
            
            # 設置預設值
            valid_anim = {
                "name": anim["name"],
                "weight": weight,
                "loop": anim.get("loop", True),
                "speed": anim.get("speed", 1.0)
            }
            valid_animations.append(valid_anim)
        
        # 檢查權重總和
        if total_weight > 1.1:
            return f"❌ 動畫權重總和 {total_weight:.2f} 過大，建議保持在 1.0 左右"
        
        # 構建角色動畫混合 payload
        payload = {
            "animations": valid_animations,
            "blendMode": blend_mode,
            "transitionDuration": transition_duration
        }
        
        animation_mix_endpoint = f"{BASE_URL}/api/control/character/animation-mix"
        response = requests.post(animation_mix_endpoint, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            anim_names = [anim["name"] for anim in valid_animations]
            weights = [f"{anim['name']}({anim['weight']:.1f})" for anim in valid_animations]
            return f"✅ 角色動畫混合設置成功！AI 角色現在同時執行 {len(valid_animations)} 個動畫: {', '.join(weights)}，混合模式: {blend_mode}"
        else:
            return f"❌ 角色動畫混合設置失敗 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except requests.exceptions.Timeout:
        return "❌ 請求超時，服務器可能忙碌中"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def stop_main_character_animation_mix() -> str:
    """
    停止主要 AI 角色的動畫混合，回到單一動畫模式
    
    Returns:
        操作結果描述
    """
    try:
        animation_mix_endpoint = f"{BASE_URL}/api/control/character/animation-mix/stop"
        response = requests.post(animation_mix_endpoint, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return f"✅ 主角動畫混合已停止！AI 角色回到單一動畫模式"
        else:
            return f"❌ 停止主角動畫混合失敗 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except requests.exceptions.Timeout:
        return "❌ 請求超時，服務器可能忙碌中"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def dance_group_animation(animation: str, speed: float = 1.0, loop: bool = True) -> str:
    """
    控制舞群的動畫動作

    Args:
        animation: 動畫名稱，必須是 `prototype/shared/config/animations.json` 中定義的名稱
        speed: 播放速度，預設為 1.0
        loop: 是否循環播放，預設為 True

    Returns:
        操作結果描述
    """
    try:
        # 構建舞群動畫 payload
        payload = {
            "animation": animation,
            "speed": speed,
            "loop": loop
        }
        
        animation_endpoint = f"{BASE_URL}/api/control/body-animation"
        response = requests.post(animation_endpoint, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            loop_text = "循環播放" if loop else "播放一次"
            return f"✅ 舞群動畫設置成功！舞群現在執行 '{animation}' 動作，{loop_text}，速度 {speed}x"
        else:
            return f"❌ 舞群動畫設置失敗 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except requests.exceptions.Timeout:
        return "❌ 請求超時，服務器可能忙碌中"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def set_dance_group(
    formation: str = 'circle', 
    count: int = 10, 
    scale: float = 5.0, 
    x: float = 0, 
    y: float = -25, 
    z: float = 0
) -> str:
    """
    一次性設置舞群的多個屬性，包括隊形、人數、大小和位移。
    如果未提供參數，將使用預設值。

    Args:
        formation: 隊形名稱 (預設: 'circle')
        count: 舞群人數 (預設: 10)
        scale: 舞群的整體縮放比例 (預設: 5.0)
        x: X 軸位移 (預設: 0)
        y: Y 軸位移 (預設: -25)
        z: Z 軸位移 (預設: 0)

    Returns:
        操作結果描述
    """
    try:
        # 後端要求所有欄位都必須存在
        payload = {
            "formation": formation,
            "dancerCount": count,
            "scale": scale,
            "position": [x, y, z]
        }

        response = requests.post(f"{BASE_URL}/api/control/dance_group", json=payload, timeout=10)
        
        if response.status_code == 200:
            return f"✅ 舞群屬性更新成功: {json.dumps(payload)}"
        else:
            return f"❌ 更新舞群屬性失敗 (HTTP {response.status_code}): {response.text}"
            
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def play_song(song_name: str, interrupt: bool = True) -> str:
    """
    播放歌曲檔案
    
    ⚠️ 重要：使用前必須先探索可用資源！不要猜測檔案名稱！
    
    探索指令：ls prototype/backend/songs/
    
    Args:
        song_name: 歌曲檔案名稱（必須是實際存在的檔案）
                  範例格式：'檔案名.mp3'
                  📁 檔案位置：prototype/backend/songs/
        interrupt: 是否中斷當前播放的歌曲，預設為 True
        
    使用步驟：
    1. 先執行：ls prototype/backend/songs/
    2. 選擇實際存在的檔案
    3. 再調用此工具
    
    Returns:
        操作結果描述
    """
    try:
        # 構建播放歌曲 payload
        payload = {
            "url": f"/songs-file/{song_name}",
            "interrupt": interrupt
        }
        
        play_audio_endpoint = f"{BASE_URL}/api/control/play-audio"
        response = requests.post(play_audio_endpoint, json=payload, timeout=10)
        
        if response.status_code == 200:
            return f"✅ 歌曲播放成功！AI 角色正在演唱 '{song_name}'。"
        else:
            return f"❌ 歌曲播放失敗 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except requests.exceptions.Timeout:
        return "❌ 請求超時，服務器可能忙碌中"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def play_background_music(bgm_name: str) -> str:
    """
    播放背景音樂檔案
    
    ⚠️ 重要：使用前必須先探索可用資源！不要猜測檔案名稱！
    
    探索指令：ls prototype/frontend/public/audio/BGM/
    
    Args:
        bgm_name: BGM 檔案名稱（必須是實際存在的檔案）
                 範例格式：'檔案名.mp3'
                 📁 檔案位置：prototype/frontend/public/audio/BGM/
                 
    使用步驟：
    1. 先執行：ls prototype/frontend/public/audio/BGM/
    2. 選擇實際存在的檔案
    3. 再調用此工具
    
    Returns:
        操作結果描述
    """
    try:
        payload = {"bgmUrl": f"/audio/BGM/{bgm_name}"}
        response = requests.post(f"{BASE_URL}/api/control/background-audio", json=payload, timeout=10)
        if response.status_code == 200:
            return f"✅ 背景音樂 '{bgm_name}' 開始播放。"
        else:
            return f"❌ 播放背景音樂失敗 (HTTP {response.status_code}): {response.text}"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def stop_background_music() -> str:
    """
    停止目前正在播放的背景音樂。
    """
    try:
        payload = {"bgmUrl": ""}
        response = requests.post(f"{BASE_URL}/api/control/background-audio", json=payload, timeout=10)
        if response.status_code == 200:
            return "✅ 背景音樂已停止。"
        else:
            return f"❌ 停止背景音樂失敗 (HTTP {response.status_code}): {response.text}"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def play_sound_effect(effect_name: str) -> str:
    """
    播放音效檔案
    
    ⚠️ 重要：使用前必須先探索可用資源！不要猜測檔案名稱！
    
    探索指令：ls prototype/frontend/public/audio/effects/
    
    Args:
        effect_name: 音效檔案名稱（必須是實際存在的檔案）
                    範例格式：'檔案名.mp3'
                    📁 檔案位置：prototype/frontend/public/audio/effects/
                    
    使用步驟：
    1. 先執行：ls prototype/frontend/public/audio/effects/
    2. 選擇實際存在的檔案
    3. 再調用此工具
    
    Returns:
        操作結果描述
    """
    try:
        payload = {"sfxUrl": f"/audio/effects/{effect_name}"}
        response = requests.post(f"{BASE_URL}/api/control/background-audio", json=payload, timeout=10)
        if response.status_code == 200:
            return f"✅ 音效 '{effect_name}' 已播放。"
        else:
            return f"❌ 播放音效失敗 (HTTP {response.status_code}): {response.text}"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def generate_sound_effect(
    prompt: str, 
    duration_seconds: float = 3.0, 
    prompt_influence: float = 0.6,
    filename: str = None,
    play_immediately: bool = True
) -> str:
    """
    使用 ElevenLabs API 即時生成客製化音效。

    ⚠️  重要：prompt 必須使用精確的英文描述，中文會導致音效品質不佳！
    
    建議的英文 prompt 範例：
    - "spaceship engine humming and vibrating steadily" (太空船引擎穩定嗡嗡聲)
    - "electronic malfunction with sparks crackling and warning beeps" (電子故障配電火花和警報聲)
    - "deep space ambient cosmic wind and distant rumbling" (深空環境宇宙風和遠方隆隆聲) 
    - "metal blast door sliding open with heavy mechanical sound" (金屬防爆門滑開的重機械聲)
    - "urgent warning alarm beeping rapidly with echo" (緊急警報快速嗶聲帶回音)
    - "rocket engine ignition with powerful thrust roar" (火箭引擎點火強力推進咆哮)
    - "atmospheric entry rumbling and plasma whistling" (大氣層進入隆隆聲和電漿嘯叫)
    - "reactor core humming with electrical discharge" (反應爐核心嗡嗡聲配電流放電)

    Args:
        prompt: 音效的英文描述文字，請使用專業的英文環境音效術語
        duration_seconds: 音效長度（秒），範圍 0.5-22.0，預設 3.0 秒
        prompt_influence: 對描述的遵循度，範圍 0.0-1.0，0.6 是平衡值
        filename: 自訂檔名（不含副檔名），不設定則自動產生
        play_immediately: 是否立即播放生成的音效，預設 True

    Returns:
        操作結果描述
    """
    try:
        payload = {
            "prompt": prompt,
            "duration_seconds": duration_seconds,
            "prompt_influence": prompt_influence,
            "play_immediately": play_immediately
        }
        
        if filename:
            payload["filename"] = filename
        
        response = requests.post(f"{BASE_URL}/api/control/generate-sound-effect", json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            message = f"✅ 音效生成成功！檔案: {result['filename']}"
            if result.get('played_immediately'):
                message += " 已立即播放"
            return message
        else:
            return f"❌ 音效生成失敗 (HTTP {response.status_code}): {response.text}"
    except requests.exceptions.Timeout:
        return "❌ 音效生成超時（這通常需要 10-30 秒），請稍後再試"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def set_camera_preset(preset_name: str, duration: float = 2.0) -> str:
    """
    設置攝影機預設位置，創造戲劇性的視覺效果
    
    Args:
        preset_name: 攝影機預設名稱，可用選項包括：
            基本視角: overview(總覽), head_close_up(頭部特寫), side_view(側面視角)
            環繞視角: center_orbit_high_1, center_orbit_high_2, center_orbit_low_1, center_orbit_low_2
            戲劇視角: dramatic_angle_1, dramatic_angle_2, low_angle_head(低角度頭部)
            動態視角: fly_by_left(左側飛越), fly_by_right(右側飛越), frontal_dynamic_low, frontal_dynamic_high
            特殊視角: top_down_center(俯視中心), behind_head_looking_out(頭後向外看)
            舞蹈視角: dance_circle_view(舞蹈圓圈視角), full_shot_dancers(舞者全景)
            頭部特寫: orbit_head_1, orbit_head_2
        duration: 鏡頭轉換時間（秒），預設 2.0 秒
    
    Returns:
        操作結果描述
    """
    try:
        payload = {
            "name": preset_name,
            "duration": duration
        }
        
        camera_endpoint = f"{BASE_URL}/api/control/camera/set-frontend-preset"
        response = requests.post(camera_endpoint, json=payload, timeout=10)
        
        if response.status_code == 200:
            return f"✅ 攝影機預設成功！鏡頭切換到 '{preset_name}' 位置，轉換時間 {duration} 秒"
        else:
            return f"❌ 攝影機設置失敗 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except requests.exceptions.Timeout:
        return "❌ 請求超時，服務器可能忙碌中"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool() 
def set_head_size(scale_factor: float) -> str:
    """
    調整 AI 角色的頭部大小，創造戲劇效果
    
    Args:
        scale_factor: 頭部縮放係數 (0.1 到 20.0)
                     1.0 = 正常大小
                     2.0-4.0 = 稍微放大，增加存在感 
                     5.0-10.0 = 明顯放大，戲劇效果
                     15.0+ = 極度放大，喜劇效果
    
    Returns:
        操作結果描述
    """
    try:
        # 限制縮放係數範圍
        scale_factor = max(0.1, min(20.0, scale_factor))
        
        payload = {
            "scaleFactor": scale_factor
        }
        
        head_size_endpoint = f"{BASE_URL}/api/control/head-size"
        response = requests.post(head_size_endpoint, json=payload, timeout=10)
        
        if response.status_code == 200:
            if scale_factor == 1.0:
                effect_desc = "正常大小"
            elif scale_factor < 1.0:
                effect_desc = "縮小效果"
            elif scale_factor <= 2.0:
                effect_desc = "稍微放大"
            elif scale_factor <= 5.0:
                effect_desc = "明顯放大，增加戲劇感"
            elif scale_factor <= 10.0:
                effect_desc = "大幅放大，強烈視覺衝擊"
            else:
                effect_desc = "極度放大，喜劇效果"
                
            return f"✅ 頭部大小調整成功！縮放係數: {scale_factor}x ({effect_desc})"
        else:
            return f"❌ 頭部大小調整失敗 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except requests.exceptions.Timeout:
        return "❌ 請求超時，服務器可能忙碌中"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def set_character_scale(scale: float) -> str:
    """
    調整 AI 角色的整體大小
    
    Args:
        scale: 縮放倍數 (建議範圍 0.1 到 3.0)
    
    Returns:
        操作結果描述
    """
    try:
        payload = {"scale": scale}
        response = requests.post(f"{BASE_URL}/api/control/character/scale", json=payload, timeout=10)
        if response.status_code == 200:
            return f"✅ 角色大小已設為 {scale} 倍。"
        else:
            return f"❌ 設定角色大小失敗 (HTTP {response.status_code}): {response.text}"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def set_character_position(x: float, y: float, z: float) -> str:
    """
    設定 AI 角色的位置
    
    Args:
        x: X 軸座標
        y: Y 軸座標
        z: Z 軸座標
        
    Returns:
        操作結果描述
    """
    try:
        payload = {"position": [x, y, z]}
        response = requests.post(f"{BASE_URL}/api/control/character/position", json=payload, timeout=10)
        if response.status_code == 200:
            return f"✅ 角色位置已設為 (X: {x}, Y: {y}, Z: {z})。"
        else:
            return f"❌ 設定角色位置失敗 (HTTP {response.status_code}): {response.text}"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def set_character_rotation(x: float, y: float, z: float) -> str:
    """
    設定 AI 角色的旋轉角度 (使用弧度)
    
    Args:
        x: X 軸旋轉角度 (弧度)
        y: Y 軸旋轉角度 (弧度)
        z: Z 軸旋轉角度 (弧度)
        
    Returns:
        操作結果描述
    """
    try:
        payload = {"rotation": [x, y, z]}
        response = requests.post(f"{BASE_URL}/api/control/character/rotation", json=payload, timeout=10)
        if response.status_code == 200:
            return f"✅ 角色已旋轉至 (X: {x}, Y: {y}, Z: {z}) 弧度。"
        else:
            return f"❌ 設定角色旋轉失敗 (HTTP {response.status_code}): {response.text}"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def reset_character_transform() -> str:
    """
    一鍵重置 AI 角色的位置、旋轉和大小
    
    Returns:
        操作結果描述
    """
    try:
        response = requests.post(f"{BASE_URL}/api/control/character/reset-transform", json={}, timeout=10)
        if response.status_code == 200:
            return "✅ 角色變換已重置。"
        else:
            return f"❌ 重置角色變換失敗 (HTTP {response.status_code}): {response.text}"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def set_character_morph(morph_name: str, value: float) -> str:
    """
    設定 AI 角色的指定 Morph Target
    
    Args:
        morph_name: 要控制的 Morph Target 名稱 (大小寫敏感)
        value: Morph Target 的強度值 (通常在 0.0 到 1.0 之間)
    
    Returns:
        操作結果描述
    """
    try:
        payload = {
            "outfit_morphs": {
                morph_name: value
            }
        }
        
        outfit_endpoint = f"{BASE_URL}/api/control/character/outfit"
        response = requests.post(outfit_endpoint, json=payload, timeout=10)
        
        if response.status_code == 200:
            return f"✅ 成功設定 Morph Target: '{morph_name}' 為 {value}"
        else:
            return f"❌ 設定 Morph Target 失敗 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except requests.exceptions.Timeout:
        return "❌ 請求超時，服務器可能忙碌中"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def set_environment_preset(preset: str) -> str:
    """
    設置場景的環境光照預設。

    Args:
        preset: 預設名稱。可用選項包括:
                'studio'(工作室), 'sunset'(夕陽), 'sunrise'(黎明), 'night'(夜晚), 
                'warehouse'(倉庫), 'forest'(森林), 'apartment'(公寓), 'city'(城市), 
                'park'(公園), 'hall'(大廳)

    Returns:
        操作結果描述
    """
    try:
        endpoint = f"{BASE_URL}/api/control/environment/preset"
        payload = {"preset": preset}
        response = requests.post(endpoint, json=payload, timeout=10)
        
        if response.status_code == 200:
            return f"✅ 環境光照預設已成功設置為 '{preset}'"
        else:
            return f"❌ 設置環境預設失敗 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.RequestException as e:
        return f"❌ 請求失敗: {e}"

@mcp.tool()
def set_light_intensity(intensity: float) -> str:
    """
    設置場景光照的強度。

    Args:
        intensity: 光照強度值，建議範圍 0.1 到 3.0。

    Returns:
        操作結果描述
    """
    try:
        endpoint = f"{BASE_URL}/api/control/environment/intensity"
        payload = {"intensity": intensity}
        response = requests.post(endpoint, json=payload, timeout=10)
        
        if response.status_code == 200:
            return f"✅ 光照強度已成功設置為 {intensity}"
        else:
            return f"❌ 設置光照強度失敗 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.RequestException as e:
        return f"❌ 請求失敗: {e}"

@mcp.tool()
def reset_environment_settings() -> str:
    """
    將所有環境光照設定重置為預設值。

    Returns:
        操作結果描述
    """
    try:
        endpoint = f"{BASE_URL}/api/control/environment/reset"
        # 根據測試腳本，發送一個包含任意內容的JSON payload
        payload = {"reset": True} 
        response = requests.post(endpoint, json=payload, timeout=10)
        
        if response.status_code == 200:
            return "✅ 環境光照設定已成功重置為預設值。"
        else:
            return f"❌ 重置環境設定失敗 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.RequestException as e:
        return f"❌ 請求失敗: {e}"

@mcp.tool()
async def set_body_shape(value: float):
    """
    Sets the character's body shape.

    Args:
        value (float): The value for the body shape, from 0.0 (thinnest) to 1.0 (fattest).
                       The value will be clamped between 0.0 and 1.0.
    """
    # Correct endpoint based on control.py
    base_url = f"{BASE_URL}/api/control/character/outfit"
    
    # Clamp the value to be between 0.0 and 1.0
    clamped_value = max(0.0, min(1.0, value))

    # Correct payload structure based on CharacterOutfitRequest in control.py
    payload = {
        "outfit_morphs": {
            "鍵 1": clamped_value,
            "錯置": clamped_value,
            "錯置.001": clamped_value
        }
    }
    
    try:
        response = requests.post(base_url, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        return f"Body shape set to {clamped_value}. API response: {response.json()}"
    except requests.exceptions.RequestException as e:
        error_message = f"Error setting body shape: {e}"
        if e.response is not None:
            error_message += f" - Response: {e.response.text}"
        print(error_message)
        return f"Failed to set body shape. Check the server logs. Details: {error_message}"

@mcp.tool()
def set_monitor_content(
    monitor_id: str,
    video_name: str = None,
    volume: float = None,
    visible: bool = None,
    playing: bool = None,
    playback_speed: float = None
) -> str:
    """
    控制螢幕顯示器的內容和播放狀態
    
    ⚠️ 重要：使用影片前必須先探索可用資源！不要猜測檔案名稱！
    
    探索指令：ls prototype/frontend/public/videos/
    
    Args:
        monitor_id: 螢幕 ID，可選值: "screen1", "screen2", "screen3"
        video_name: 影片檔案名稱（必須是實際存在的檔案）
                   📁 檔案位置：prototype/frontend/public/videos/
                   使用前請先執行：ls prototype/frontend/public/videos/
        volume: 音量 (0.0-1.0)，可選
        visible: 是否顯示螢幕，可選
        playing: 是否播放，可選
        playback_speed: 播放速度，可選（例如 1.0=正常, 2.0=雙倍速度）
        
    使用步驟（設定影片時）：
    1. 先執行：ls prototype/frontend/public/videos/
    2. 選擇實際存在的檔案
    3. 再調用此工具
    
    Returns:
        操作結果描述
    """
    try:
        payload = {}
        if video_name:
            payload['content'] = f"/videos/{video_name}"
        if volume is not None:
            payload['volume'] = volume
        if visible is not None:
            payload['visible'] = visible
        if playing is not None:
            payload['playing'] = playing
        if playback_speed is not None:
            payload['playbackSpeed'] = playback_speed

        if not payload:
            return "⚠️ 沒有提供任何要更新的參數。"

        endpoint = f"{BASE_URL}/api/monitors/{monitor_id}"
        response = requests.put(endpoint, json=payload, timeout=10)

        if response.status_code == 200:
            return f"✅ 螢幕 {monitor_id} 更新成功: {json.dumps(payload)}"
        else:
            return f"❌ 更新螢幕 {monitor_id} 失敗 (HTTP {response.status_code}): {response.text}"
            
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def generate_image_overlay(
    prompt: str,
    position: str = 'center',
    size: str = 'large',
    duration: float = 10.0,
    aspect_ratio: str = 'square',
    reference_images: List[str] = None
) -> str:
    """
    根據文字描述生成一張圖片，並作為浮動圖層顯示在畫面上。

    Args:
        prompt: 💡 建議使用英文描述獲得更好的生成效果！
                正確範例: 'A massive supernova exploding in vibrant colors and cosmic energy'
                也可使用中文: '一個巨大的超新星爆炸，充滿鮮豔色彩和宇宙能量'
        position: 圖片顯示位置 ('center', 'top-left', 'bottom-right' 等)。預設 'center'。
        size: 圖片的預設尺寸 ('small', 'medium', 'large')。預設 'large'。
        duration: 圖片顯示的持續時間（秒）。預設 10.0。
        aspect_ratio: 圖片的長寬比 ('square', 'portrait', 'landscape')。預設 'square'。
        reference_images: (可選) 參考圖片的檔案名稱列表。

    Returns:
        操作結果描述
    """
    try:
        payload = {
            "description": prompt,
            "position": position,
            "size": size,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "reference_images": reference_images
        }
        # 移除 payload 中值為 None 的鍵
        payload = {k: v for k, v in payload.items() if v is not None}

        response = requests.post(f"{BASE_URL}/api/generate-image", json=payload, timeout=60)
        if response.status_code == 200:
            return f"✅ 圖片浮層生成成功！URL: {response.json().get('url')}"
        else:
            return f"❌ 圖片浮層生成失敗 (HTTP {response.status_code}): {response.text}"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def generate_background_image(prompt: str, aspect_ratio: str = 'landscape', reference_images: List[str] = None) -> str:
    """
    根據文字描述生成一張背景圖片，並自動設為場景背景。

    Args:
        prompt: 💡 建議使用英文描述獲得更好的生成效果！
                正確範例: 'A futuristic space station interior with glowing control panels and stars visible through windows'
                也可使用中文: '未來感的太空站內部，發光的控制面板和透過窗戶可見的星星'
        aspect_ratio: 圖片的長寬比 ('square', 'portrait', 'landscape')。預設 'landscape'。
        reference_images: (可選) 參考圖片的檔案名稱列表。

    Returns:
        操作結果描述
    """
    try:
        payload = {
            "description": prompt, 
            "aspect_ratio": aspect_ratio,
            "reference_images": reference_images
        }
        # 移除 payload 中值為 None 的鍵
        payload = {k: v for k, v in payload.items() if v is not None}
        
        response = requests.post(f"{BASE_URL}/api/generate-background-image", json=payload, timeout=60)
        if response.status_code == 200:
            return f"✅ 背景圖片生成並設置成功！URL: {response.json().get('url')}"
        else:
            return f"❌ 背景圖片生成失敗 (HTTP {response.status_code}): {response.text}"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def take_selfie(
    prompt: str,
    reference_images: List[str] = None,
    position: str = 'center',
    size: str = 'large',
    duration: float = 15.0
) -> str:
    """
    讓 AI 角色拍一張自拍照。可以基於現有圖片進行修改。

    Args:
        prompt: 💡 建議使用英文描述獲得更好的生成效果！
                正確範例: 'AI character taking a selfie in space with Earth and stars in the background'
                也可使用中文: 'AI角色在太空中自拍，背景是地球和星星'
        reference_images: (可選) 參考圖片的檔案名稱列表 (例如 ['selfie_123.png', 'image_456.png'])。
        position: 圖片顯示位置。預設 'center'。
        size: 圖片尺寸。預設 'large'。
        duration: 顯示持續時間（秒）。預設 15.0。

    Returns:
        操作結果描述
    """
    try:
        payload = {
            "description": prompt,
            "modification": prompt, # description 和 modification 都用同一個 prompt
            "reference_images": reference_images,
            "position": position,
            "size": size,
            "duration": duration
        }
        response = requests.post(f"{BASE_URL}/api/take-selfie", json=payload, timeout=60)
        if response.status_code == 200:
            return f"✅ 自拍成功！URL: {response.json().get('url')}"
        else:
            return f"❌ 自拍失敗 (HTTP {response.status_code}): {response.text}"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def show_existing_image(
    filename: str,
    caption: str = None,
    position: str = 'center',
    size: str = 'large',
    duration: float = 15.0
) -> str:
    """
    顯示伺服器上已經存在的圖片。

    Args:
        filename: 要顯示的圖片檔案名稱。
        caption: (可選) 圖片的說明文字。
        position: 圖片顯示位置。預設 'center'。
        size: 圖片尺寸。預設 'large'。
        duration: 顯示持續時間（秒）。預設 15.0。

    Returns:
        操作結果描述
    """
    try:
        payload = {
            "filename": filename,
            "caption": caption,
            "position": position,
            "size": size,
            "duration": duration
        }
        response = requests.post(f"{BASE_URL}/api/show-existing-image", json=payload, timeout=10)
        if response.status_code == 200:
            return f"✅ 成功顯示圖片 '{filename}'。"
        else:
            return f"❌ 顯示圖片失敗 (HTTP {response.status_code}): {response.text}"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def speak_latest_space_news(limit: int = 3, intro_text: str = None) -> str:
    """
    獲取最新的太空新聞頭條，並讓 AI 角色播報出來。

    Args:
        limit: 要獲取的新聞數量。預設 3。
        intro_text: (可選) 自訂的開場白。

    Returns:
        操作結果描述
    """
    try:
        payload = {"limit": limit, "intro_text": intro_text}
        payload = {k: v for k, v in payload.items() if v is not None}
        response = requests.post(f"{BASE_URL}/api/news/speak-latest-news", json=payload, timeout=30)
        if response.status_code == 200:
            return f"✅ 新聞播報成功！內容: {response.json().get('news_content')}"
        else:
            return f"❌ 新聞播報失敗 (HTTP {response.status_code}): {response.text}"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def generate_map_image(
    latitude: float,
    longitude: float,
    zoom: int = 14,
    caption: str = None,
    position: str = 'center',
    size: str = 'large',
    duration: float = 25.0
) -> str:
    """
    根據經緯度生成一張 Google 地圖圖片並顯示。

    Args:
        latitude: 地圖中心的緯度。
        longitude: 地圖中心的經度。
        zoom: 縮放等級。預設 14。
        caption: (可選) 圖片的說明文字。
        position: 圖片顯示位置。預設 'center'。
        size: 圖片尺寸。預設 'large'。
        duration: 顯示持續時間（秒）。預設 25.0。

    Returns:
        操作結果描述
    """
    try:
        payload = {
            "latitude": latitude,
            "longitude": longitude,
            "zoom": zoom,
            "caption": caption,
            "position": position,
            "size": size,
            "duration": duration
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        response = requests.post(f"{BASE_URL}/api/generate-map-image", json=payload, timeout=20)
        if response.status_code == 200:
            return f"✅ 地圖生成成功！URL: {response.json().get('url')}"
        else:
            return f"❌ 地圖生成失敗 (HTTP {response.status_code}): {response.text}"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def search_nasa_image(
    query: str,
    caption: str = None,
    position: str = 'center',
    size: str = 'large',
    duration: float = 25.0
) -> str:
    """
    從 NASA 圖庫中搜尋圖片並顯示。

    Args:
        query: ⚠️ 【重要】搜尋關鍵字必須使用英文！NASA API 只接受英文查詢。
               正確範例: 'nebula', 'apollo 11', 'mars rover', 'hubble telescope', 'space station'
               錯誤範例: '星雲', '阿波羅', '火星探測器' (中文會導致搜尋失敗)
        caption: (可選) 自訂的圖片說明文字。
        position: 圖片顯示位置。預設 'center'。
        size: 圖片尺寸。預設 'large'。
        duration: 顯示持續時間（秒）。預設 25.0。

    Returns:
        操作結果描述
    """
    try:
        payload = {
            "query": query,
            "caption": caption,
            "position": position,
            "size": size,
            "duration": duration
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        response = requests.post(f"{BASE_URL}/api/search-nasa-image", json=payload, timeout=30)
        if response.status_code == 200:
            return f"✅ NASA 圖片搜尋成功！URL: {response.json().get('url')}"
        else:
            return f"❌ NASA 圖片搜尋失敗 (HTTP {response.status_code}): {response.text}"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def get_epic_image(
    date: str = None,
    caption: str = None,
    position: str = 'center',
    size: str = 'large',
    duration: float = 25.0
) -> str:
    """
    獲取 NASA EPIC 相機拍攝的地球全貌圖並顯示。

    Args:
        date: (可選) 指定日期 (格式: YYYY-MM-DD)。若無，則抓取最新圖片。
        caption: (可選) 圖片的說明文字。
        position: 圖片顯示位置。預設 'center'。
        size: 圖片尺寸。預設 'large'。
        duration: 顯示持續時間（秒）。預設 25.0。

    Returns:
        操作結果描述
    """
    try:
        payload = {
            "date": date,
            "caption": caption,
            "position": position,
            "size": size,
            "duration": duration
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        response = requests.post(f"{BASE_URL}/api/get-epic-image", json=payload, timeout=30)
        if response.status_code == 200:
            return f"✅ EPIC 地球圖片獲取成功！URL: {response.json().get('url')}"
        else:
            return f"❌ EPIC 地球圖片獲取失敗 (HTTP {response.status_code}): {response.text}"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def get_available_songs() -> str:
    """
    取得系統中所有可用的歌曲檔案
    
    Returns:
        歌曲清單的詳細資訊
    """
    try:
        response = requests.get(f"{BASE_URL}/api/resources/songs", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            songs_list = "\n".join([f"• {song['name']} ({song['size']} bytes)" for song in data['files']])
            return f"✅ 找到 {data['count']} 個歌曲檔案:\n\n{songs_list}"
        else:
            return f"❌ 無法取得歌曲清單 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def get_available_bgm() -> str:
    """
    取得系統中所有可用的背景音樂檔案
    
    Returns:
        BGM 清單的詳細資訊
    """
    try:
        response = requests.get(f"{BASE_URL}/api/resources/bgm", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            bgm_list = "\n".join([f"• {bgm['name']} ({bgm['size']} bytes)" for bgm in data['files']])
            return f"✅ 找到 {data['count']} 個 BGM 檔案:\n\n{bgm_list}"
        else:
            return f"❌ 無法取得 BGM 清單 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def get_available_effects() -> str:
    """
    取得系統中所有可用的音效檔案
    
    Returns:
        音效清單的詳細資訊
    """
    try:
        response = requests.get(f"{BASE_URL}/api/resources/effects", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            effects_list = "\n".join([f"• {effect['name']} ({effect['size']} bytes)" for effect in data['files']])
            return f"✅ 找到 {data['count']} 個音效檔案:\n\n{effects_list}"
        else:
            return f"❌ 無法取得音效清單 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def get_available_videos() -> str:
    """
    取得系統中所有可用的影片檔案
    
    Returns:
        影片清單的詳細資訊
    """
    try:
        response = requests.get(f"{BASE_URL}/api/resources/videos", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            videos_list = "\n".join([f"• {video['name']} ({video['size']} bytes)" for video in data['files']])
            return f"✅ 找到 {data['count']} 個影片檔案:\n\n{videos_list}"
        else:
            return f"❌ 無法取得影片清單 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def get_available_dance_group_animations() -> str:
    """
    取得系統中所有可用的舞群動畫檔案
    
    Returns:
        舞群動畫清單的詳細資訊
    """
    try:
        response = requests.get(f"{BASE_URL}/api/resources/animations", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # 清理動畫名稱，移除 .glb 後綴
            clean_animations = []
            for anim in data['files']:
                clean_name = anim['name'].replace('_animation.glb', '').replace('.glb', '')
                clean_animations.append(f"• {clean_name} ({anim['size']} bytes)")
            
            animations_list = "\n".join(clean_animations)
            return f"✅ 找到 {data['count']} 個舞群動畫檔案:\n\n{animations_list}\n\n💡 提示: 使用動畫時請直接輸入乾淨的名稱，例如: 'DancingTwerk', 'Breakdance1990' 等"
        else:
            return f"❌ 無法取得舞群動畫清單 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def get_all_resources() -> str:
    """
    取得系統中所有類型的媒體資源總覽
    
    Returns:
        所有資源的統計資訊
    """
    try:
        response = requests.get(f"{BASE_URL}/api/resources/all", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            summary = data['summary']
            
            return f"""✅ 系統資源總覽:
📊 總檔案數: {summary['total_files']}
🎵 歌曲檔案: {summary['songs_count']}
🎼 背景音樂: {summary['bgm_count']}
🔊 音效檔案: {summary['effects_count']}
🎬 影片檔案: {summary['videos_count']}
💃 動畫檔案: {summary['animations_count']}

💡 提示: 使用其他資源查詢工具來查看具體檔案清單"""
        else:
            return f"❌ 無法取得資源總覽 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def search_resources(query: str, resource_type: str = None, limit: int = 10) -> str:
    """
    搜索媒體資源
    
    Args:
        query: 搜索關鍵字
        resource_type: 限制搜索的資源類型，可選值: songs, bgm, effects, videos, animations
        limit: 結果數量限制，預設為 10
    
    Returns:
        搜索結果
    """
    try:
        params = {"query": query, "limit": limit}
        if resource_type:
            params["resource_type"] = resource_type
            
        response = requests.get(f"{BASE_URL}/api/resources/search", params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data['count'] == 0:
                return f"🔍 搜索關鍵字 '{query}' 沒有找到任何匹配的檔案"
            
            results_list = []
            for result in data['results']:
                results_list.append(f"• {result['name']} ({result['category']}) - {result['size']} bytes")
            
            results_text = "\n".join(results_list)
            return f"🔍 搜索 '{query}' 找到 {data['count']} 個結果:\n\n{results_text}"
        else:
            return f"❌ 搜索失敗 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def get_available_main_character_animations() -> str:
    """
    取得主要 AI 角色可用的動畫清單
    
    Returns:
        主角動畫清單（系統預設動畫集合）
    """
    # 主角專用動畫清單（系統中實際可用的動畫）
    main_character_animations = [
        # 運動類
        "運動1 - 運動動作1",
        "運動2 - 運動動作2", 
        "飛1 - 飛行動作1",
        "飛2 - 飛行動作2",
        
        # 日常類
        "漂浮 - 漂浮動作",
        "漂浮2 - 漂浮動作2",
        "划手機 - 滑手機動作",
        "臥躺 - 躺下動作",
        "不穩 - 不穩定動作",
        "Tpose - T字型姿勢",
        
        # 舞蹈類
        "舞步1 - 舞蹈動作1",
        "舞步2 - 舞蹈動作2",
        "舞步3 - 舞蹈動作3"
    ]
    
    animations_text = "\n".join([f"• {anim}" for anim in main_character_animations])
    
    return f"""✅ 主要 AI 角色可用動畫清單 ({len(main_character_animations)} 個):

{animations_text}

💡 提示: 這些是系統中實際可用的主角動畫，請使用 set_main_character_animation() 來播放
⚠️ 注意: 使用時請直接輸入動畫名稱，例如: "運動1", "漂浮", "舞步1" 等"""

@mcp.tool()
def set_main_character_animation_mix(animations_config: str, blend_mode: str = "normal", transition_duration: float = 0.5) -> str:
    """
    控制主要 AI 角色的多重動畫混合，可以同時播放多個動畫並控制它們的權重
    
    Args:
        animations_config: 動畫配置的 JSON 字串，格式為:
            [{"name": "動畫名稱", "weight": 權重值, "loop": 是否循環, "speed": 播放速度}, ...]
            範例: '[{"name": "運動1", "weight": 0.7, "loop": true, "speed": 1.0}, {"name": "舞步1", "weight": 0.3, "loop": true, "speed": 1.2}]'
            可用動畫: 運動1, 運動2, 飛1, 飛2, 漂浮, 漂浮2, 划手機, 臥躺, 不穩, Tpose, 舞步1, 舞步2, 舞步3
            權重範圍: 0.0-1.0，建議總權重保持在 1.0 左右
        blend_mode: 混合模式，可選項: "normal", "additive", "override"，預設為 "normal"
        transition_duration: 切換到混合模式的過渡時間（秒），預設為 0.5
    
    Returns:
        操作結果描述
    """
    try:
        # 解析動畫配置 JSON
        import json
        try:
            animations = json.loads(animations_config)
        except json.JSONDecodeError as e:
            return f"❌ 動畫配置 JSON 格式錯誤: {str(e)}"
        
        # 驗證動畫配置格式
        if not isinstance(animations, list) or len(animations) == 0:
            return "❌ 動畫配置必須是非空的陣列"
        
        # 驗證每個動畫配置
        total_weight = 0
        valid_animations = []
        for anim in animations:
            if not isinstance(anim, dict):
                return "❌ 每個動畫配置必須是對象"
            
            if "name" not in anim or "weight" not in anim:
                return "❌ 每個動畫配置必須包含 'name' 和 'weight' 欄位"
            
            weight = anim.get("weight", 1.0)
            if not isinstance(weight, (int, float)) or weight < 0 or weight > 1:
                return f"❌ 動畫 '{anim['name']}' 的權重必須在 0-1 之間"
            
            total_weight += weight
            
            # 設置預設值
            valid_anim = {
                "name": anim["name"],
                "weight": weight,
                "loop": anim.get("loop", True),
                "speed": anim.get("speed", 1.0)
            }
            valid_animations.append(valid_anim)
        
        # 檢查權重總和
        if total_weight > 1.1:
            return f"❌ 動畫權重總和 {total_weight:.2f} 過大，建議保持在 1.0 左右"
        
        # 構建角色動畫混合 payload
        payload = {
            "animations": valid_animations,
            "blendMode": blend_mode,
            "transitionDuration": transition_duration
        }
        
        animation_mix_endpoint = f"{BASE_URL}/api/control/character/animation-mix"
        response = requests.post(animation_mix_endpoint, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            anim_names = [anim["name"] for anim in valid_animations]
            weights = [f"{anim['name']}({anim['weight']:.1f})" for anim in valid_animations]
            return f"✅ 角色動畫混合設置成功！AI 角色現在同時執行 {len(valid_animations)} 個動畫: {', '.join(weights)}，混合模式: {blend_mode}"
        else:
            return f"❌ 角色動畫混合設置失敗 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except requests.exceptions.Timeout:
        return "❌ 請求超時，服務器可能忙碌中"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def stop_main_character_animation_mix() -> str:
    """
    停止主要 AI 角色的動畫混合，回到單一動畫模式
    
    Returns:
        操作結果描述
    """
    try:
        animation_mix_endpoint = f"{BASE_URL}/api/control/character/animation-mix/stop"
        response = requests.post(animation_mix_endpoint, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return f"✅ 主角動畫混合已停止！AI 角色回到單一動畫模式"
        else:
            return f"❌ 停止主角動畫混合失敗 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except requests.exceptions.Timeout:
        return "❌ 請求超時，服務器可能忙碌中"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def configure_obs_connection(host: str = "localhost", port: int = 4455, password: str = "", timeout: int = 10) -> str:
    """
    配置 OBS WebSocket 連接參數並重新連接
    
    Args:
        host: OBS WebSocket 主機位址，預設為 "localhost"
        port: OBS WebSocket 連接埠，預設為 4455
        password: OBS WebSocket 密碼，預設為空字串
        timeout: 連接逾時時間（秒），預設為 10 秒
    
    Returns:
        連接配置結果描述
    """
    try:
        # 建構連接設定 payload
        payload = {
            "host": host,
            "port": port,
            "password": password,
            "timeout": timeout
        }
        
        connection_endpoint = f"{BASE_URL}/api/perception/obs/connection"
        response = requests.post(connection_endpoint, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success", False):
                status = result.get("status", {})
                obs_version = status.get("obs_version", "未知")
                websocket_version = status.get("websocket_version", "未知")
                current_scene = status.get("current_scene", "未知")
                streaming = "🔴 串流中" if status.get("streaming", False) else "⚪ 未串流"
                recording = "🔴 錄影中" if status.get("recording", False) else "⚪ 未錄影"
                
                return f"✅ OBS 連接設定成功！\n🔗 連接位址: {host}:{port}\n🔑 密碼: {'已設定' if password else '無密碼'}\n⏱️ 逾時: {timeout}秒\n\n📊 OBS 狀態:\n• OBS 版本: {obs_version}\n• WebSocket 版本: {websocket_version}\n• 當前場景: {current_scene}\n• 串流狀態: {streaming}\n• 錄影狀態: {recording}"
            else:
                error_msg = result.get("message", "連接失敗")
                error_detail = result.get("error", "")
                return f"❌ OBS 連接設定失敗\n原因: {error_msg}\n詳情: {error_detail}"
        else:
            return f"❌ 連接設定請求失敗 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except requests.exceptions.Timeout:
        return "❌ 連接設定請求超時，後端服務器可能忙碌中"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def start_obs_streaming() -> str:
    """
    開始 OBS 串流
    
    Returns:
        串流開始結果描述
    """
    try:
        stream_endpoint = f"{BASE_URL}/api/perception/obs/stream/start"
        response = requests.post(stream_endpoint, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success", False):
                streaming = result.get("streaming", False)
                message = result.get("message", "串流已開始")
                
                if streaming:
                    return f"🔴 {message}\n✅ OBS 串流現在正在進行中！"
                else:
                    return f"⚠️ {message}\n❓ 串流狀態可能需要稍等才會生效"
            else:
                error_msg = result.get("message", "開始串流失敗")
                return f"❌ 開始串流失敗\n原因: {error_msg}"
        else:
            return f"❌ 串流請求失敗 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except requests.exceptions.Timeout:
        return "❌ 串流請求超時，後端服務器可能忙碌中"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def stop_obs_streaming() -> str:
    """
    停止 OBS 串流
    
    Returns:
        串流停止結果描述
    """
    try:
        stream_endpoint = f"{BASE_URL}/api/perception/obs/stream/stop"
        response = requests.post(stream_endpoint, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success", False):
                streaming = result.get("streaming", True)
                message = result.get("message", "串流已停止")
                
                if not streaming:
                    return f"⚪ {message}\n✅ OBS 串流已完全停止！"
                else:
                    return f"⚠️ {message}\n❓ 串流狀態可能需要稍等才會生效"
            else:
                error_msg = result.get("message", "停止串流失敗")
                return f"❌ 停止串流失敗\n原因: {error_msg}"
        else:
            return f"❌ 串流請求失敗 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except requests.exceptions.Timeout:
        return "❌ 串流請求超時，後端服務器可能忙碌中"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def connect_and_start_streaming(host: str = "localhost", port: int = 4455, password: str = "", timeout: int = 10) -> str:
    """
    連接 OBS 並立即開始串流
    
    Args:
        host: OBS WebSocket 主機位址，預設為 "localhost"
        port: OBS WebSocket 連接埠，預設為 4455
        password: OBS WebSocket 密碼，預設為空字串
        timeout: 連接逾時時間（秒），預設為 10 秒
    
    Returns:
        連接並開始串流的結果描述
    """
    try:
        # 步驟 1: 配置 OBS 連接
        connection_payload = {
            "host": host,
            "port": port,
            "password": password,
            "timeout": timeout
        }
        
        connection_endpoint = f"{BASE_URL}/api/perception/obs/connection"
        connection_response = requests.post(connection_endpoint, json=connection_payload, timeout=15)
        
        if connection_response.status_code != 200:
            return f"❌ OBS 連接失敗 (HTTP {connection_response.status_code}): {connection_response.text}"
        
        connection_result = connection_response.json()
        if not connection_result.get("success", False):
            error_msg = connection_result.get("message", "連接失敗")
            error_detail = connection_result.get("error", "")
            return f"❌ OBS 連接失敗\n原因: {error_msg}\n詳情: {error_detail}"
        
        # 步驟 2: 開始串流
        stream_endpoint = f"{BASE_URL}/api/perception/obs/stream/start"
        stream_response = requests.post(stream_endpoint, timeout=15)
        
        if stream_response.status_code != 200:
            return f"✅ OBS 連接成功，但串流開始失敗 (HTTP {stream_response.status_code}): {stream_response.text}"
        
        stream_result = stream_response.json()
        
        # 取得 OBS 狀態資訊
        status = connection_result.get("status", {})
        obs_version = status.get("obs_version", "未知")
        current_scene = status.get("current_scene", "未知")
        
        if stream_result.get("success", False):
            streaming = stream_result.get("streaming", False)
            stream_message = stream_result.get("message", "串流已開始")
            
            if streaming:
                return f"🎯 連接並開始串流成功！\n\n🔗 連接資訊:\n• 位址: {host}:{port}\n• OBS 版本: {obs_version}\n• 當前場景: {current_scene}\n\n🔴 串流狀態: {stream_message}\n✅ 串流正在進行中！"
            else:
                return f"🔗 OBS 連接成功，但串流狀態異常\n• 位址: {host}:{port}\n• OBS 版本: {obs_version}\n⚠️ 串流訊息: {stream_message}"
        else:
            stream_error = stream_result.get("message", "開始串流失敗")
            return f"🔗 OBS 連接成功，但無法開始串流\n• 位址: {host}:{port}\n• OBS 版本: {obs_version}\n❌ 串流錯誤: {stream_error}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except requests.exceptions.Timeout:
        return "❌ 連接或串流請求超時，後端服務器可能忙碌中"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def get_browser_screenshot() -> str:
    """
    擷取 OBS 中瀏覽器來源的即時截圖，並下載到本地 screen_shots 資料夾
    
    Returns:
        截圖結果描述和本地檔案路徑
    """
    import os
    from pathlib import Path
    
    try:
        # 建立本地 screen_shots 資料夾
        local_screenshots_dir = Path("screen_shots")
        local_screenshots_dir.mkdir(exist_ok=True)
        
        # 調用後端 OBS 截圖 API，指定來源為「瀏覽器」
        payload = {
            "source_name": "瀏覽器",
            "width": 1280,
            "height": 720,
            "image_format": "png"
        }
        
        screenshot_endpoint = f"{BASE_URL}/api/perception/obs/screenshot"
        response = requests.post(screenshot_endpoint, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success", False):
                filename = result.get("filename")
                file_size = result.get("file_size", 0)
                timestamp = result.get("timestamp")
                
                # 建構圖片下載 URL
                image_url = f"{BASE_URL}/api/perception/obs/screenshot/{filename}"
                
                # 下載圖片到本地
                download_response = requests.get(image_url, timeout=30)
                
                if download_response.status_code == 200:
                    # 儲存到本地 screen_shots 資料夾
                    local_file_path = local_screenshots_dir / filename
                    
                    with open(local_file_path, 'wb') as f:
                        f.write(download_response.content)
                    
                    # 驗證檔案是否成功儲存
                    if local_file_path.exists():
                        local_file_size = local_file_path.stat().st_size
                        
                        return f"✅ 瀏覽器截圖成功並已下載到本地！\n📷 檔案: {filename}\n📊 大小: {file_size:,} bytes\n🕐 時間戳: {timestamp}\n📁 本地路徑: {local_file_path.absolute()}\n💾 本地檔案大小: {local_file_size:,} bytes"
                    else:
                        return f"❌ 截圖成功但本地儲存失敗"
                else:
                    return f"❌ 截圖成功但下載失敗 (HTTP {download_response.status_code})"
            else:
                error_msg = result.get("error", "未知錯誤")
                return f"❌ 瀏覽器截圖失敗: {error_msg}"
        else:
            return f"❌ 截圖請求失敗 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except requests.exceptions.Timeout:
        return "❌ 截圖請求超時，OBS 或服務器可能忙碌中"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool()
def get_field_video_screenshot() -> str:
    """
    擷取 OBS 中展場視訊來源的即時截圖，並下載到本地 screen_shots 資料夾
    
    Returns:
        截圖結果描述和本地檔案路徑
    """
    import os
    from pathlib import Path
    
    try:
        # 建立本地 screen_shots 資料夾
        local_screenshots_dir = Path("screen_shots")
        local_screenshots_dir.mkdir(exist_ok=True)
        
        # 調用後端 OBS 截圖 API，指定來源為「展場視訊源」
        payload = {
            "source_name": "展場視訊源",
            "width": 1280,
            "height": 720,
            "image_format": "png"
        }
        
        screenshot_endpoint = f"{BASE_URL}/api/perception/obs/screenshot"
        response = requests.post(screenshot_endpoint, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success", False):
                filename = result.get("filename")
                file_size = result.get("file_size", 0)
                timestamp = result.get("timestamp")
                
                # 建構圖片下載 URL
                image_url = f"{BASE_URL}/api/perception/obs/screenshot/{filename}"
                
                # 下載圖片到本地
                download_response = requests.get(image_url, timeout=30)
                
                if download_response.status_code == 200:
                    # 儲存到本地 screen_shots 資料夾
                    local_file_path = local_screenshots_dir / filename
                    
                    with open(local_file_path, 'wb') as f:
                        f.write(download_response.content)
                    
                    # 驗證檔案是否成功儲存
                    if local_file_path.exists():
                        local_file_size = local_file_path.stat().st_size
                        
                        return f"✅ 展場視訊源截圖成功並已下載到本地！\n📷 檔案: {filename}\n📊 大小: {file_size:,} bytes\n🕐 時間戳: {timestamp}\n📁 本地路徑: {local_file_path.absolute()}\n💾 本地檔案大小: {local_file_size:,} bytes"
                    else:
                        return f"❌ 截圖成功但本地儲存失敗"
                else:
                    return f"❌ 截圖成功但下載失敗 (HTTP {download_response.status_code})"
            else:
                error_msg = result.get("error", "未知錯誤")
                return f"❌ 展場視訊源截圖失敗: {error_msg}"
        else:
            return f"❌ 截圖請求失敗 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except requests.exceptions.Timeout:
        return "❌ 截圖請求超時，OBS 或服務器可能忙碌中"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

if __name__ == "__main__":
    print("🚀 太空直播系統 MCP 服務器啟動中...", file=sys.stderr)
    print("📡 提供工具: send_message, set_emotion, emotion_transition, set_main_character_animation, set_main_character_animation_mix, stop_main_character_animation_mix, dance_group_animation, set_dance_group, play_song, play_background_music, stop_background_music, play_sound_effect, set_camera_preset, set_head_size, set_character_scale, set_character_position, set_character_rotation, reset_character_transform, set_character_morph, set_body_shape, set_monitor_content, generate_image_overlay, generate_background_image, take_selfie, show_existing_image, speak_latest_space_news, generate_map_image, search_nasa_image, get_epic_image, get_available_songs, get_available_bgm, get_available_effects, get_available_videos, get_available_main_character_animations, get_available_dance_group_animations, get_all_resources, search_resources, configure_obs_connection, start_obs_streaming, stop_obs_streaming, connect_and_start_streaming, get_browser_screenshot, get_field_video_screenshot", file=sys.stderr)
    print("🔗 連接後端: http://localhost:8000", file=sys.stderr)
    print("\n要在 Cursor 中使用，請在 settings.json 中添加此服務器配置", file=sys.stderr)
    
    mcp.run()

# Cursor MCP 配置範例:
# 在 Cursor settings.json 中添加:
# {
#   "mcpServers": {
#     "space_live": {
#       "command": "python3",
#       "args": ["prototype/backend/mcp_server/main.py"],
#       "cwd": "/Volumes/2024data/space_live_project"
#     }
#   }
# } 