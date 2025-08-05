"""
YouTube 聊天室即時監控服務

使用 pytchat 庫來即時監控 YouTube 直播聊天室的訊息
"""

import pytchat
import asyncio
import threading
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import re
import requests
import subprocess
from utils.logger import logger


@dataclass
class ChatMessage:
    """聊天訊息資料結構"""
    id: str
    author: str
    message: str
    timestamp: str
    datetime: str
    elapsed_time: Optional[str] = None
    amount_value: Optional[float] = None
    amount_string: Optional[str] = None
    currency: Optional[str] = None
    message_type: str = "textMessage"
    author_channel_id: Optional[str] = None
    is_verified: bool = False
    is_owner: bool = False
    is_sponsor: bool = False
    is_moderator: bool = False


class YouTubeChatMonitorService:
    """YouTube 聊天室監控服務 (單例模式)"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(YouTubeChatMonitorService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 只在第一次初始化時設置屬性
        if not hasattr(self, '_initialized'):
            self.chat_instance = None
            self.is_monitoring = False
            self.monitoring_thread = None
            self.message_buffer: List[ChatMessage] = []
            self.max_buffer_size = 100
            self.current_video_id = None
            self._stop_event = threading.Event()
            self._initialized = True
        
    def extract_video_id(self, url: str) -> Optional[str]:
        """從 YouTube URL 中提取 video_id"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/live/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/v/([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # 如果已經是 video_id 格式
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
            
        return None
    
    def get_live_video_id_from_channel(self, channel_id: str) -> Optional[str]:
        """從頻道 ID 自動獲取當前直播的 video_id"""
        try:
            logger.info(f"正在從頻道 {channel_id} 獲取當前直播 video_id")
            
            # 使用 /live 端點獲取當前直播資訊
            live_url = f"https://www.youtube.com/channel/{channel_id}/live"
            
            # 發送 HTTP 請求
            response = requests.get(live_url, timeout=10)
            response.raise_for_status()
            
            # 從 HTML 中提取 video_id
            import re
            pattern = r'"videoId":"([^"]*)"'
            matches = re.findall(pattern, response.text)
            
            if matches:
                video_id = matches[0]
                logger.info(f"成功獲取當前直播 video_id: {video_id}")
                return video_id
            else:
                logger.warning(f"頻道 {channel_id} 目前沒有進行直播")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"獲取直播資訊時網路錯誤: {e}")
            return None
        except Exception as e:
            logger.error(f"獲取直播 video_id 時發生錯誤: {e}")
            return None
    
    def start_monitoring_by_channel(self, channel_id: str) -> Dict[str, Any]:
        """使用頻道 ID 開始監控當前直播聊天室"""
        try:
            logger.info(f"開始通過頻道 ID 監控: {channel_id}")
            
            # 先獲取當前直播的 video_id
            video_id = self.get_live_video_id_from_channel(channel_id)
            if not video_id:
                return {
                    "success": False,
                    "error": f"頻道 {channel_id} 目前沒有進行直播",
                    "monitoring": False
                }
            
            # 使用獲取到的 video_id 開始監控
            return self.start_monitoring(video_id)
            
        except Exception as e:
            logger.error(f"通過頻道 ID 開始監控時發生錯誤: {e}")
            return {
                "success": False,
                "error": str(e),
                "monitoring": False
            }
    
    def start_monitoring(self, video_url_or_id: str) -> Dict[str, Any]:
        """開始監控指定的 YouTube 直播聊天室"""
        try:
            video_id = self.extract_video_id(video_url_or_id)
            if not video_id:
                raise ValueError(f"無法從 URL 中提取 video_id: {video_url_or_id}")
            
            # 如果已經在監控其他直播，先停止
            if self.is_monitoring:
                self.stop_monitoring()
                
            logger.info(f"開始監控 YouTube 聊天室，video_id: {video_id}")
            
            # 建立 pytchat 實例
            self.chat_instance = pytchat.create(video_id=video_id)
            self.current_video_id = video_id
            self.is_monitoring = True
            self._stop_event.clear()
            
            # 清空訊息緩衝區
            self.message_buffer.clear()
            
            # 在背景執行緒中開始監控
            self.monitoring_thread = threading.Thread(
                target=self._monitor_chat_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            
            return {
                "success": True,
                "video_id": video_id,
                "message": f"成功開始監控 YouTube 聊天室",
                "monitoring": True
            }
            
        except Exception as e:
            logger.error(f"開始監控 YouTube 聊天室時發生錯誤: {e}")
            self.is_monitoring = False
            return {
                "success": False,
                "error": str(e),
                "monitoring": False
            }
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """停止監控聊天室"""
        try:
            if not self.is_monitoring:
                return {
                    "success": True,
                    "message": "沒有正在進行的監控",
                    "monitoring": False
                }
            
            logger.info("正在停止 YouTube 聊天室監控")
            
            # 設定停止事件
            self._stop_event.set()
            self.is_monitoring = False
            
            # 關閉 pytchat 實例
            if self.chat_instance:
                try:
                    self.chat_instance.terminate()
                except:
                    pass
                self.chat_instance = None
            
            # 等待監控執行緒結束
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5)
            
            self.current_video_id = None
            
            return {
                "success": True,
                "message": "成功停止 YouTube 聊天室監控",
                "monitoring": False
            }
            
        except Exception as e:
            logger.error(f"停止監控時發生錯誤: {e}")
            return {
                "success": False,
                "error": str(e),
                "monitoring": self.is_monitoring
            }
    
    def _monitor_chat_loop(self):
        """聊天監控主迴圈（在背景執行緒中執行）"""
        try:
            while self.is_monitoring and not self._stop_event.is_set():
                if not self.chat_instance or not self.chat_instance.is_alive():
                    logger.warning("聊天實例已停止，結束監控")
                    break
                
                try:
                    # 取得新的聊天訊息
                    chat_data = self.chat_instance.get()
                    
                    for chat_item in chat_data.sync_items():
                        message = self._convert_chat_item(chat_item)
                        self._add_message_to_buffer(message)
                        
                        logger.info(f"收到聊天訊息: {message.author} - {message.message}")
                    
                    # 短暫休息避免過度佔用 CPU
                    if not self._stop_event.wait(0.5):
                        continue
                    else:
                        break
                        
                except Exception as e:
                    logger.error(f"處理聊天訊息時發生錯誤: {e}")
                    if not self._stop_event.wait(2):
                        continue
                    else:
                        break
                        
        except Exception as e:
            logger.error(f"聊天監控迴圈發生錯誤: {e}")
        finally:
            self.is_monitoring = False
            logger.info("YouTube 聊天室監控已結束")
    
    def _convert_chat_item(self, chat_item) -> ChatMessage:
        """將 pytchat 的聊天項目轉換為內部格式"""
        return ChatMessage(
            id=chat_item.id,
            author=chat_item.author.name,
            message=chat_item.message,
            timestamp=str(chat_item.timestamp),
            datetime=chat_item.datetime,
            elapsed_time=getattr(chat_item, 'elapsedTime', None),
            amount_value=getattr(chat_item, 'amountValue', None),
            amount_string=getattr(chat_item, 'amountString', None),
            currency=getattr(chat_item, 'currency', None),
            message_type=chat_item.type,
            author_channel_id=chat_item.author.channelId,
            is_verified=chat_item.author.isVerified,
            is_owner=chat_item.author.isChatOwner,
            is_sponsor=chat_item.author.isChatSponsor,
            is_moderator=chat_item.author.isChatModerator
        )
    
    def _add_message_to_buffer(self, message: ChatMessage):
        """將訊息加入緩衝區"""
        self.message_buffer.append(message)
        
        # 限制緩衝區大小
        if len(self.message_buffer) > self.max_buffer_size:
            self.message_buffer.pop(0)
    
    def get_recent_messages(self, limit: int = 20) -> List[Dict[str, Any]]:
        """取得最近的聊天訊息（從最新到最舊的順序）"""
        # 取得最後的 N 條訊息，然後反轉順序（最新的在前面）
        recent_messages = self.message_buffer[-limit:] if limit > 0 else self.message_buffer
        recent_messages = list(reversed(recent_messages))  # 反轉順序，最新的在前
        return [asdict(msg) for msg in recent_messages]
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """取得監控狀態"""
        return {
            "monitoring": self.is_monitoring,
            "video_id": self.current_video_id,
            "message_count": len(self.message_buffer),
            "chat_alive": self.chat_instance.is_alive() if self.chat_instance else False
        }
    
    def clear_message_buffer(self) -> Dict[str, Any]:
        """清空訊息緩衝區"""
        cleared_count = len(self.message_buffer)
        self.message_buffer.clear()
        
        return {
            "success": True,
            "cleared_count": cleared_count,
            "message": f"已清空 {cleared_count} 條訊息"
        }
    
    def search_messages(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        """在訊息緩衝區中搜尋包含關鍵字的訊息"""
        keyword_lower = keyword.lower()
        matching_messages = []
        
        for message in reversed(self.message_buffer):
            if (keyword_lower in message.message.lower() or 
                keyword_lower in message.author.lower()):
                matching_messages.append(asdict(message))
                
                if len(matching_messages) >= limit:
                    break
        
        return matching_messages
    
    def get_user_messages(self, username: str, limit: int = 20) -> List[Dict[str, Any]]:
        """取得特定使用者的訊息"""
        user_messages = []
        
        for message in reversed(self.message_buffer):
            if message.author.lower() == username.lower():
                user_messages.append(asdict(message))
                
                if len(user_messages) >= limit:
                    break
        
        return user_messages
    
    def __del__(self):
        """析構函數，確保正確清理資源"""
        if self.is_monitoring:
            self.stop_monitoring()