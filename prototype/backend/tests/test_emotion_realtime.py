#!/usr/bin/env python3
"""
測試 Realtime API 的 emotion trajectory 功能
"""
import asyncio
import websockets
import json
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_realtime_emotion():
    """測試 Realtime API 的 emotion trajectory 功能"""
    # 連接到後端的 realtime WebSocket
    uri = "ws://localhost:8000/api/real-time/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("Connected to realtime WebSocket")
            
            # 等待連接穩定
            await asyncio.sleep(1)
            
            # 發送一段測試語音 (模擬)
            # 這裡我們直接說一段話來觸發emotion trajectory
            test_text = "你好！我今天心情很棒，想要展現一些開心的表情！"
            
            # 發送文字消息 (如果支援的話)
            test_message = {
                "type": "text_input",
                "text": test_text
            }
            
            await websocket.send(json.dumps(test_message))
            logger.info(f"Sent test message: {test_text}")
            
            # 監聽回應
            timeout = 30  # 30秒超時
            start_time = asyncio.get_event_loop().time()
            
            while True:
                try:
                    # 檢查超時
                    if asyncio.get_event_loop().time() - start_time > timeout:
                        logger.error("Test timeout after 30 seconds")
                        break
                    
                    # 接收消息
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    
                    # 檢查是否為文字數據
                    if message.startswith(b"TEXT_DATA:"):
                        text_data = message.decode('utf-8')[10:]  # 移除 "TEXT_DATA:" 前綴
                        logger.info(f"Received text data: {text_data}")
                        continue
                    
                    # 檢查是否為中斷信號
                    if message == b"INTERRUPT_SIGNAL":
                        logger.info("Received interrupt signal")
                        continue
                    
                    # 如果是音頻數據，記錄但不處理
                    if isinstance(message, bytes):
                        logger.info(f"Received audio data: {len(message)} bytes")
                        continue
                        
                except asyncio.TimeoutError:
                    logger.info("No message received in 5 seconds, continuing...")
                    continue
                except websockets.exceptions.ConnectionClosed:
                    logger.info("WebSocket connection closed")
                    break
                except Exception as e:
                    logger.error(f"Error receiving message: {e}")
                    break
                    
    except Exception as e:
        logger.error(f"Failed to connect to WebSocket: {e}")
        logger.info("Make sure the backend server is running on localhost:8000")

if __name__ == "__main__":
    print("Testing Realtime API emotion trajectory functionality...")
    print("Make sure to:")
    print("1. Start the backend server")
    print("2. Have a frontend connected to see the emotion effects")
    print("3. Set up your OpenAI API key")
    print()
    
    asyncio.run(test_realtime_emotion()) 