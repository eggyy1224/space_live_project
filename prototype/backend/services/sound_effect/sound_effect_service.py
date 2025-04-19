import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SoundEffectService:
    """音效服務類 - 生成前端可理解的音效指令"""
    
    @staticmethod
    def create_synth_sound_command(effects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        創建合成音效命令
        
        Args:
            effects: 音效列表，每個音效包含type, options, startTime等
            
        Returns:
            格式化的音效命令
        """
        try:
            logger.info(f"開始創建合成音效命令，包含 {len(effects)} 個音效")
            
            # 驗證每個音效是否有必要的字段
            for i, effect in enumerate(effects):
                if 'type' not in effect:
                    logger.warning(f"音效 #{i} 缺少必要的 'type' 字段")
                    return {"error": "音效格式錯誤: 缺少type"}
                
                # 記錄音效詳情
                logger.debug(f"音效 #{i}: type={effect.get('type')}, "
                           f"startTime={effect.get('startTime')}, "
                           f"options={effect.get('options')}")
                
                # 確保startTime是數字
                if 'startTime' in effect and not isinstance(effect['startTime'], (int, float)):
                    try:
                        effect['startTime'] = float(effect['startTime'])
                        logger.debug(f"音效 #{i} startTime 已轉換為浮點數: {effect['startTime']}")
                    except (ValueError, TypeError):
                        effect['startTime'] = 0
                        logger.warning(f"音效 #{i} startTime 格式錯誤，設為預設值 0")
            
            # 創建命令
            command = {
                "type": "audio-effect",
                "payload": {
                    "synthMode": True,
                    "effects": effects
                }
            }
            
            logger.info(f"生成合成音效命令成功，共 {len(effects)} 個效果")
            logger.debug(f"完整音效命令: {json.dumps(command)[:200]}...")
            return command
        except Exception as e:
            logger.error(f"創建合成音效命令時出錯: {str(e)}")
            import traceback
            logger.error(f"錯誤堆疊: {traceback.format_exc()}")
            return {"error": f"創建音效命令失敗: {str(e)}"}
    
    @staticmethod
    def create_background_music_command(music_id: str, volume: float = 0.3, loop: bool = True) -> Dict[str, Any]:
        """
        創建背景音樂命令
        
        Args:
            music_id: 音樂識別碼
            volume: 音量 (0-1)
            loop: 是否循環播放
            
        Returns:
            格式化的背景音樂命令
        """
        command = {
            "type": "audio-effect",
            "payload": {
                "backgroundMusic": True,
                "musicId": music_id,
                "volume": max(0, min(1, volume)),
                "loop": loop
            }
        }
        
        logger.debug(f"生成背景音樂命令: {json.dumps(command)}")
        return command
        
    @staticmethod
    def create_ambient_sound_effects() -> Dict[str, Any]:
        """
        創建環境音效 - 太空站背景聲
        
        Returns:
            格式化的環境音效命令
        """
        effects = [
            # 低頻環境嗡嗡聲
            {
                "type": "noise",
                "options": {
                    "noiseType": "brown",
                    "volume": 0.15,
                    "duration": 10.0,
                    "filter": {
                        "type": "lowpass",
                        "frequency": 200,
                        "Q": 1
                    }
                },
                "startTime": 0
            },
            # 偶爾的電子嗶聲
            {
                "type": "beep",
                "options": {
                    "frequency": 1200,
                    "duration": 0.1,
                    "volume": 0.2,
                    "wavetype": "sine"
                },
                "startTime": 2000
            },
            # 另一個電子嗶聲
            {
                "type": "beep",
                "options": {
                    "frequency": 900,
                    "duration": 0.15,
                    "volume": 0.15,
                    "wavetype": "sine"
                },
                "startTime": 5000
            },
            # 設備運行聲
            {
                "type": "noise",
                "options": {
                    "noiseType": "pink",
                    "volume": 0.1,
                    "duration": 3.0,
                    "filter": {
                        "type": "bandpass",
                        "frequency": 500,
                        "Q": 2
                    }
                },
                "startTime": 7000
            }
        ]
        
        return SoundEffectService.create_synth_sound_command(effects)
        
    @staticmethod
    def create_greeting_sound() -> Dict[str, Any]:
        """
        創建歡迎音效
        
        Returns:
            格式化的歡迎音效命令
        """
        effects = [
            {
                "type": "beep",
                "options": {
                    "frequency": 880,
                    "duration": 0.1,
                    "volume": 0.6,
                    "wavetype": "sine" 
                },
                "startTime": 0
            },
            {
                "type": "beep",
                "options": {
                    "frequency": 1320,
                    "duration": 0.1,
                    "volume": 0.6,
                    "wavetype": "sine"
                },
                "startTime": 150
            }
        ]
        
        return SoundEffectService.create_synth_sound_command(effects)
        
    @staticmethod
    def create_tone_sequence(base_frequency: float, pattern: str = "neutral", 
                           volume: float = 0.5, complexity: int = 1) -> Dict[str, Any]:
        """
        創建基於Tone.js的音效序列
        
        Args:
            base_frequency: 基礎頻率
            pattern: 音效模式，可以是"neutral", "excited", "serious"等
            volume: 音量(0-1)
            complexity: 複雜度(1-3)
            
        Returns:
            格式化的Tone.js音效命令
        """
        # 根據複雜度確定音效數量
        num_effects = min(5, max(1, complexity * 2))
        effects = []
        
        if pattern == "excited":
            # 興奮模式 - 上升音階
            for i in range(num_effects):
                effects.append({
                    "type": "beep",
                    "options": {
                        "frequency": base_frequency * (1 + i * 0.2),
                        "duration": 0.1,
                        "volume": min(1.0, volume + i * 0.05),
                        "wavetype": "triangle"
                    },
                    "startTime": i * 100
                })
        
        elif pattern == "serious":
            # 嚴肅模式 - 下降音階
            for i in range(num_effects):
                effects.append({
                    "type": "beep",
                    "options": {
                        "frequency": base_frequency * (1 - i * 0.1),
                        "duration": 0.2,
                        "volume": volume,
                        "wavetype": "sine"
                    },
                    "startTime": i * 200
                })
        
        elif pattern == "question":
            # 疑問模式 - 上升音調
            effects = [
                {
                    "type": "beep",
                    "options": {
                        "frequency": base_frequency * 0.8,
                        "duration": 0.1,
                        "volume": volume,
                        "wavetype": "sine" 
                    },
                    "startTime": 0
                },
                {
                    "type": "beep",
                    "options": {
                        "frequency": base_frequency * 1.2,
                        "duration": 0.2,
                        "volume": volume,
                        "wavetype": "sine" 
                    },
                    "startTime": 150
                }
            ]
        
        elif pattern == "tech":
            # 科技模式 - 數字化聲音
            effects = [
                {
                    "type": "beep",
                    "options": {
                        "frequency": base_frequency,
                        "duration": 0.05,
                        "volume": volume,
                        "wavetype": "square" 
                    },
                    "startTime": 0
                },
                {
                    "type": "beep",
                    "options": {
                        "frequency": base_frequency * 1.5,
                        "duration": 0.03,
                        "volume": volume * 0.8,
                        "wavetype": "square" 
                    },
                    "startTime": 60
                },
                {
                    "type": "beep",
                    "options": {
                        "frequency": base_frequency * 0.8,
                        "duration": 0.04,
                        "volume": volume * 0.7,
                        "wavetype": "square" 
                    },
                    "startTime": 130
                }
            ]
            
            # 對於高複雜度，添加噪音
            if complexity > 1:
                effects.append({
                    "type": "noise",
                    "options": {
                        "noiseType": "white",
                        "volume": volume * 0.3,
                        "duration": 0.1,
                        "filter": {
                            "type": "highpass",
                            "frequency": 3000,
                            "Q": 1
                        }
                    },
                    "startTime": 200
                })
        
        elif pattern == "space":
            # 太空模式 - 環境聲
            effects = [
                {
                    "type": "noise",
                    "options": {
                        "noiseType": "pink",
                        "volume": volume * 0.4,
                        "duration": 0.3,
                        "filter": {
                            "type": "lowpass",
                            "frequency": 800,
                            "Q": 1
                        }
                    },
                    "startTime": 0
                },
                {
                    "type": "beep",
                    "options": {
                        "frequency": base_frequency,
                        "duration": 0.2,
                        "volume": volume * 0.6,
                        "wavetype": "sine" 
                    },
                    "startTime": 150
                }
            ]
            
            # 對於高複雜度，添加更多元素
            if complexity > 1:
                effects.append({
                    "type": "beep",
                    "options": {
                        "frequency": base_frequency * 1.5,
                        "duration": 0.1,
                        "volume": volume * 0.5,
                        "wavetype": "sine" 
                    },
                    "startTime": 350
                })
        
        else:  # neutral
            # 中性模式 - 簡單音效
            effects = [
                {
                    "type": "beep",
                    "options": {
                        "frequency": base_frequency,
                        "duration": 0.1,
                        "volume": volume,
                        "wavetype": "sine" 
                    },
                    "startTime": 0
                }
            ]
            
            # 對於高複雜度，添加更多音效
            if complexity > 1:
                effects.append({
                    "type": "beep",
                    "options": {
                        "frequency": base_frequency * 1.2,
                        "duration": 0.1,
                        "volume": volume * 0.8,
                        "wavetype": "sine" 
                    },
                    "startTime": 200
                })
            
            if complexity > 2:
                effects.append({
                    "type": "beep",
                    "options": {
                        "frequency": base_frequency * 1.4,
                        "duration": 0.1,
                        "volume": volume * 0.7,
                        "wavetype": "sine" 
                    },
                    "startTime": 400
                })
        
        return SoundEffectService.create_synth_sound_command(effects) 