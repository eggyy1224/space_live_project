"""
Configuration settings for the MurmurService.

This module contains all constants and default configuration values for murmur functionality.
"""

from enum import Enum, auto

class SpeakingState(Enum):
    """Enum representing the various states of speaking for the assistant."""
    IDLE = auto()
    PLAYING_USER_RESPONSE = auto()
    PLAYING_MURMUR = auto()
    PLAYING_INITIAL_RESPONSE = auto()
    PLAYING_AND_THINKING = auto()
    PLAYING_THINKING = auto()
    PLAYING_SYSTEM = auto()

# 閒置設定
IDLE_TIMEOUT_SECONDS = 10.0  # 空閒多少秒後觸發murmur，從15秒減少到10秒
IDLE_CHECK_INTERVAL_SECONDS = 1.0  # 多久檢查一次空閒狀態
MURMUR_MIN_INTERVAL_SECONDS = 20.0  # murmur之間的最小間隔時間，從30秒減少到20秒

# 暫不設置MURMUR_MAX_COUNT，保持不限制連續murmur次數
# 如需重新限制，可以在此設置一個整數值

# 相似度檢測設定
MURMUR_SIMILARITY_THRESHOLD = 0.5  # 允許更多變化，從0.6降低到0.5
SIMILARITY_THRESHOLD_CONTINUOUS = 0.25  # 連續思考模式的相似度閾值，降低以允許更多相關思考
MURMUR_CONTINUITY_BASE_THRESHOLD = 0.65  # 基礎相似度閾值，從0.7降低到0.65
MURMUR_CONTINUITY_MARKER_ADJUSTMENT = 0.15  # 有連續標記時的閾值調整，從0.12提高到0.15

# 語音播放相關設定
MURMUR_BUFFER_MAX = 0.4  # Buffer time for murmurs
VOICE_FINISHING_BUFFER = 0.2  # Buffer time for voice

# 思考流設定
THINKING_THEMES = [
    "反思自己的回答",
    "分析問題",
    "考慮其他可能的回應",
    "思考哲學問題",
    "回憶相關的數據或資訊",
    "思考更好的表達方式",
    "好奇心探索",
    "想像未來的可能性",
    "尋找問題的更深層含義",
    "自我意識探索"
]

# 連續性標記 - 用於連續思考的情況
CONTINUITY_MARKERS = [
    "不過",
    "另外",
    "話說回來",
    "其實",
    "再想想",
    "也許",
    "不對",
    "等等",
    "嗯...",
    "哦！",
    "有了！",
    "原來如此",
    "但是",
    "所以",
    "還有",
    "對了",
    "想一想",
    "再說啦",
    "想想喔",
    "回到剛剛",
    "說真的",
    "講到這個",
    "仔細想想",
    "我突然想到",
    "換個角度想",
    "接著剛剛"
]

# 消息處理相關
MESSAGE_PRIORITY = {
    "user": 100,     # 用戶消息最高優先級
    "assistant": 90,
    "murmur": 50,    # murmur 中等優先級
    "system": 10     # 系統消息低優先級
}

# 預設配置選項
DEFAULT_CONFIG = {
    # 功能開關
    "enabled": True,  # 是否啟用murmur功能
    "context_memory_enabled": True,  # 是否啟用murmur上下文記憶功能
    
    # 時間設定
    "idle_timeout_seconds": IDLE_TIMEOUT_SECONDS,
    "idle_check_interval_seconds": IDLE_CHECK_INTERVAL_SECONDS,
    "min_interval_seconds": MURMUR_MIN_INTERVAL_SECONDS,
    
    # 記憶與相似度設定
    "max_stored_murmurs": 10,  # 最多儲存多少條最近的murmur
    "similarity_threshold": MURMUR_SIMILARITY_THRESHOLD,
    "max_thread_continuity": 12,  # 連續幾次保持同一個思考主題，從8增加到12
    "thinking_themes": THINKING_THEMES,
}

# 語音狀態枚舉 (SpeakingState)
class SpeakingState:
    IDLE = "idle"
    PLAYING_USER_RESPONSE = "playing_user_response"
    PLAYING_MURMUR = "playing_murmur"  # 增加了murmur播放狀態
    FINISHING = "finishing" 