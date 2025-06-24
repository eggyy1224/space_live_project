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

@mcp.tool
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

@mcp.tool
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

@mcp.tool
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

@mcp.tool
def character_animation(animation: str, loop: bool = True, speed: float = 1.0) -> str:
    """
    控制 AI 角色的動畫動作
    
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
            return f"✅ 角色動畫設置成功！AI 角色現在執行 '{animation}' 動作，{loop_text}，速度 {speed}x"
        else:
            return f"❌ 角色動畫設置失敗 (HTTP {response.status_code}): {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000"
    except requests.exceptions.Timeout:
        return "❌ 請求超時，服務器可能忙碌中"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool
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

@mcp.tool
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

@mcp.tool
def play_song(song_name: str, interrupt: bool = True) -> str:
    """
    讓 AI 角色播放歌曲或特殊音效（例如唱歌、動物叫聲等）。
    這會讓角色看起來像在唱歌或發出那個聲音。
    
    Args:
        song_name: 歌曲的檔案名稱。可以使用 `prototype/backend/songs/` 目錄中的任何檔案。
                   範例: '歌劇1.mp3', '電子音樂.mp3', '雞叫1.mp3', '貓叫1.mp3' 等。
                   要查看所有可用選項，可執行 `ls prototype/backend/songs/` 指令。
        interrupt: 是否中斷目前正在說的話。預設為 True。
    
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

@mcp.tool
def play_background_music(bgm_name: str) -> str:
    """
    播放背景音樂(BGM)。音樂會循環播放。

    Args:
        bgm_name: BGM 的檔案名稱。必須是 'prototype/frontend/public/audio/BGM/' 目錄中存在的檔案。
                  範例: 'spacelive_theme.mp3', 'heavy_metal_bgm_01.mp3'
                  要查看所有可用選項，可執行 `ls prototype/frontend/public/audio/BGM/`

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

@mcp.tool
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

@mcp.tool
def play_sound_effect(effect_name: str) -> str:
    """
    播放一次性的音效(SFX)。

    Args:
        effect_name: 音效的檔案名稱。必須是 'prototype/frontend/public/audio/effects/' 目錄中存在的檔案。
                     範例: '電子砲1.mp3', '警告音1.mp3'
                     要查看所有可用選項，可執行 `ls prototype/frontend/public/audio/effects/`

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

@mcp.tool
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

@mcp.tool 
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

@mcp.tool
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

@mcp.tool
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

@mcp.tool
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

@mcp.tool
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

@mcp.tool
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

@mcp.tool
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

@mcp.tool
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

@mcp.tool
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

@mcp.tool
async def set_body_shape(value: float):
    """
    Sets the character's body shape.

    Args:
        value (float): The value for the body shape, from 0.0 (thinnest) to 1.0 (fattest).
                       The value will be clamped between 0.0 and 1.0.
    """
    # Correct endpoint based on control.py
    base_url = "{BASE_URL}/api/control/character/outfit"
    
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

@mcp.tool
def set_monitor_content(
    monitor_id: str,
    video_name: str = None,
    volume: float = None,
    visible: bool = None,
    playing: bool = None,
    playback_speed: float = None
) -> str:
    """
    控制指定的螢幕（Monitor）

    Args:
        monitor_id: 螢幕的 ID (例如: 'screen1', 'screen2')
        video_name: 要播放的影片檔案名稱。必須是 'prototype/frontend/public/videos/' 中存在的檔案。
        volume: 音量 (0.0 到 1.0)
        visible: 是否可見 (True 或 False)
        playing: 是否播放 (True 或 False)
        playback_speed: 影片播放速度 (例如: 1.0 為正常速度, 2.0 為兩倍速)

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

@mcp.tool
def generate_image_overlay(
    prompt: str,
    position: str = 'center',
    size: str = 'large',
    duration: float = 10.0,
    aspect_ratio: str = 'square'
) -> str:
    """
    根據文字描述生成一張圖片，並作為浮動圖層顯示在畫面上。

    Args:
        prompt: 用於生成圖片的文字描述。
        position: 圖片顯示位置 ('center', 'top-left', 'bottom-right' 等)。預設 'center'。
        size: 圖片的預設尺寸 ('small', 'medium', 'large')。預設 'large'。
        duration: 圖片顯示的持續時間（秒）。預設 10.0。
        aspect_ratio: 圖片的長寬比 ('square', 'portrait', 'landscape')。預設 'square'。

    Returns:
        操作結果描述
    """
    try:
        payload = {
            "description": prompt,
            "position": position,
            "size": size,
            "duration": duration,
            "aspect_ratio": aspect_ratio
        }
        response = requests.post(f"{BASE_URL}/api/generate-image", json=payload, timeout=60)
        if response.status_code == 200:
            return f"✅ 圖片浮層生成成功！URL: {response.json().get('url')}"
        else:
            return f"❌ 圖片浮層生成失敗 (HTTP {response.status_code}): {response.text}"
    except Exception as e:
        return f"❌ 發生錯誤: {str(e)}"

@mcp.tool
def generate_background_image(prompt: str, aspect_ratio: str = 'landscape', reference_images: List[str] = None) -> str:
    """
    根據文字描述生成一張背景圖片，並自動設為場景背景。

    Args:
        prompt: 用於生成圖片的文字描述。
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

@mcp.tool
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
        prompt: 自拍的描述或對參考圖片的修改指令。
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

@mcp.tool
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

@mcp.tool
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

@mcp.tool
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

@mcp.tool
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
        query: 搜尋的關鍵字 (例如 'nebula', 'apollo 11')。
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

@mcp.tool
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

if __name__ == "__main__":
    print("🚀 太空直播系統 MCP 服務器啟動中...", file=sys.stderr)
    print("📡 提供工具: send_message, set_emotion, emotion_transition, character_animation, dance_group_animation, set_dance_group, play_song, play_background_music, stop_background_music, play_sound_effect, set_camera_preset, set_head_size, set_character_scale, set_character_position, set_character_rotation, reset_character_transform, set_character_morph, set_body_shape, set_monitor_content, generate_image_overlay, generate_background_image, take_selfie, show_existing_image, speak_latest_space_news, generate_map_image, search_nasa_image, get_epic_image", file=sys.stderr)
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