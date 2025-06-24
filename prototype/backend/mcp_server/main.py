#!/usr/bin/env python3
"""
太空直播系統 MCP 服務器
提供與太空站角色互動的工具
"""

import json
import sys
import requests
from fastmcp import FastMCP

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
def emotion_transition(start_emotion: str, end_emotion: str, duration: float = 5.0) -> str:
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

if __name__ == "__main__":
    print("🚀 太空直播系統 MCP 服務器啟動中...", file=sys.stderr)
    print("📡 提供工具: send_message, set_emotion, emotion_transition, character_animation", file=sys.stderr)
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