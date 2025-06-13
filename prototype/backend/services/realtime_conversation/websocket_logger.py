"""
WebSocket 日誌記錄器
專門用於記錄 OpenAI Realtime API 的 WebSocket 連線行為和事件。
"""

import os
import json
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


class WebSocketLogger:
    """WebSocket 會話日誌記錄器"""
    
    def __init__(self, logs_dir: str = "logs"):
        """
        初始化日誌記錄器
        
        Args:
            logs_dir: 日誌檔案目錄路徑
        """
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)
        
        # 為每個會話生成唯一 ID
        self.session_id = str(uuid.uuid4())[:8]  # 只取前8個字符，足夠辨識
        self.session_start_time = datetime.now()
        
        # 建立日誌檔案路徑
        timestamp = self.session_start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"session_{timestamp}_{self.session_id}.log"
        self.log_file_path = self.logs_dir / filename
        
        # 記錄器狀態
        self._is_active = True
        self._event_count = 0
        
        # 初始化日誌檔案
        self._init_log_file()
    
    def _init_log_file(self):
        """初始化日誌檔案並寫入會話開始資訊"""
        session_info = {
            "session_id": self.session_id,
            "start_time": self.session_start_time.isoformat(),
            "log_file": str(self.log_file_path),
            "format_version": "1.0"
        }
        
        with open(self.log_file_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write(f"🚀 REALTIME CONVERSATION SESSION LOG\n")
            f.write("="*80 + "\n")
            f.write(f"Session ID: {self.session_id}\n")
            f.write(f"Start Time: {self.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Log File: {self.log_file_path}\n")
            f.write("="*80 + "\n\n")
        
        print(f"📝 WebSocket 日誌記錄器已啟動")
        print(f"Session ID: {self.session_id}")
        print(f"Log File: {self.log_file_path}")
    
    def log_connection_start(self, url: str, headers: Dict[str, str]):
        """記錄連線開始"""
        if not self._is_active:
            return
            
        self._write_log("CONNECTION", "START", {
            "url": url,
            "headers": {k: v if k != "Authorization" else "Bearer [HIDDEN]" for k, v in headers.items()},
            "timestamp": datetime.now().isoformat()
        })
    
    def log_connection_success(self):
        """記錄連線成功"""
        if not self._is_active:
            return
            
        self._write_log("CONNECTION", "SUCCESS", {
            "message": "Successfully connected to OpenAI Realtime API",
            "timestamp": datetime.now().isoformat()
        })
    
    def log_session_config_sent(self, config: Dict[str, Any]):
        """記錄會話配置已發送"""
        if not self._is_active:
            return
            
        # 只記錄配置的基本資訊，避免日誌過大
        config_summary = {
            "modalities": config.get("session", {}).get("modalities", []),
            "voice": config.get("session", {}).get("voice"),
            "tools_count": len(config.get("session", {}).get("tools", [])),
            "turn_detection": config.get("session", {}).get("turn_detection", {}).get("type")
        }
        
        self._write_log("SESSION", "CONFIG_SENT", {
            "config_summary": config_summary,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_audio_chunk_sent(self, chunk_number: int, chunk_size: int):
        """記錄音頻塊發送"""
        if not self._is_active:
            return
            
        self._write_log("AUDIO", "CHUNK_SENT", {
            "chunk_number": chunk_number,
            "size_bytes": chunk_size,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_event_received(self, event_type: str, event_data: Dict[str, Any]):
        """記錄接收到的 OpenAI 事件"""
        if not self._is_active:
            return
        
        # 根據事件類型記錄不同詳細程度的資訊
        if event_type == "response.audio.delta":
            # 音頻事件只記錄大小，不記錄內容
            delta_size = len(event_data.get("delta", "")) if "delta" in event_data else 0
            log_data = {
                "delta_size": delta_size,
                "timestamp": datetime.now().isoformat()
            }
        elif event_type == "response.output_item.done":
            # Function call 事件記錄詳細資訊
            item = event_data.get("item", {})
            if item.get("type") == "function_call":
                log_data = {
                    "function_name": item.get("name"),
                    "call_id": item.get("call_id"),
                    "arguments": item.get("arguments", "{}"),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                log_data = {
                    "item_type": item.get("type"),
                    "timestamp": datetime.now().isoformat()
                }
        else:
            # 其他事件記錄基本資訊
            log_data = {
                "event_summary": self._summarize_event(event_data),
                "timestamp": datetime.now().isoformat()
            }
        
        self._write_log("EVENT", event_type.upper().replace(".", "_"), log_data)
    
    def log_function_call_executed(self, function_name: str, call_id: str, result: Dict[str, Any]):
        """記錄 Function Call 執行結果"""
        if not self._is_active:
            return
            
        self._write_log("FUNCTION", "EXECUTED", {
            "function_name": function_name,
            "call_id": call_id,
            "success": result.get("success", False),
            "error": result.get("error"),
            "timestamp": datetime.now().isoformat()
        })
    
    def log_audio_processed(self, input_size: int, output_size: int):
        """記錄音頻處理資訊"""
        if not self._is_active:
            return
            
        self._write_log("AUDIO", "PROCESSED", {
            "input_size_bytes": input_size,
            "output_size_bytes": output_size,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_error(self, error_type: str, error_message: str, details: Optional[Dict[str, Any]] = None):
        """記錄錯誤事件"""
        if not self._is_active:
            return
            
        error_data = {
            "error_type": error_type,
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        }
        
        if details:
            error_data["details"] = details
            
        self._write_log("ERROR", error_type.upper(), error_data)
    
    def log_connection_closed(self, reason: Optional[str] = None):
        """記錄連線關閉"""
        if not self._is_active:
            return
            
        duration = datetime.now() - self.session_start_time
        
        self._write_log("CONNECTION", "CLOSED", {
            "reason": reason or "Normal closure",
            "session_duration_seconds": duration.total_seconds(),
            "total_events": self._event_count,
            "timestamp": datetime.now().isoformat()
        })
        
        # 寫入會話結束資訊
        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write("\n" + "="*80 + "\n")
            f.write(f"📊 SESSION SUMMARY\n")
            f.write("="*80 + "\n")
            f.write(f"Session Duration: {duration}\n")
            f.write(f"Total Events: {self._event_count}\n")
            f.write(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n")
        
        self._is_active = False
        print(f"📝 WebSocket 日誌記錄完成: {self.log_file_path}")
    
    def _write_log(self, category: str, action: str, data: Dict[str, Any]):
        """寫入日誌到檔案"""
        if not self._is_active:
            return
            
        self._event_count += 1
        
        # 格式化時間戳
        now = datetime.now()
        timestamp = now.strftime("%H:%M:%S.%f")[:-3]  # 毫秒精度
        
        # 建立日誌行
        log_line = f"[{timestamp}] {category:>10} | {action:>20} | {json.dumps(data, ensure_ascii=False)}\n"
        
        # 寫入檔案
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_line)
        except Exception as e:
            print(f"❌ 日誌寫入失敗: {e}")
    
    def _summarize_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """總結事件資料，避免日誌過大"""
        summary = {}
        
        # 只保留關鍵欄位
        key_fields = ["type", "event_id", "item_id", "output_index", "content_index", "status"]
        
        for field in key_fields:
            if field in event_data:
                summary[field] = event_data[field]
        
        # 如果有巢狀的 item 物件，也提取關鍵資訊
        if "item" in event_data and isinstance(event_data["item"], dict):
            item = event_data["item"]
            summary["item_type"] = item.get("type")
            summary["item_status"] = item.get("status")
        
        return summary
    
    @property
    def session_info(self) -> Dict[str, Any]:
        """取得當前會話資訊"""
        return {
            "session_id": self.session_id,
            "log_file_path": str(self.log_file_path),
            "start_time": self.session_start_time.isoformat(),
            "duration_seconds": (datetime.now() - self.session_start_time).total_seconds(),
            "event_count": self._event_count,
            "is_active": self._is_active
        } 