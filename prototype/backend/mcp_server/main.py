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

if __name__ == "__main__":
    print("🚀 太空直播系統 MCP 服務器啟動中...", file=sys.stderr)
    print("📡 提供工具: send_message", file=sys.stderr)
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