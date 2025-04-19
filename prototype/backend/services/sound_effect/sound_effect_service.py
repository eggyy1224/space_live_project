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
                           volume: float = 0.5, complexity: int = 1, 
                           intensity: float = 1.0) -> Dict[str, Any]:
        """
        創建基於Tone.js的音效序列，融入更多表現力
        
        Args:
            base_frequency: 基礎頻率
            pattern: 音效模式 (neutral, excited, serious, question, thinking, success, important, tech, space, funny, fail, surprise)
            volume: 音量(0-1)
            complexity: 複雜度(1-3)，影響音效長度或層次
            intensity: 強度(0.5-1.5)，影響音量或音高變化幅度
            
        Returns:
            格式化的Tone.js音效命令
        """
        # 基礎音量和持續時間受強度影響
        base_volume = min(1.0, volume * intensity)
        base_duration = 0.1 * max(0.5, intensity) # 強度越高，基礎持續時間也可能稍長

        # 根據複雜度確定音效數量或變化
        num_effects = min(5, max(1, complexity + 1)) # 基礎效果數
        effects = []
        
        # --- 重新設計音效模式 ---
        
        if pattern == "excited":
            # 興奮模式 - 更快速、音高跳躍更大
            freq_multiplier = [1, 1.5, 2, 1.8] # 音高變化序列
            durations = [0.08, 0.06, 0.1, 0.08] # 持續時間變化
            wavetype = "triangle" if intensity > 1 else "sine"
            for i in range(min(num_effects, 4)):
                effects.append({
                    "type": "beep",
                    "options": {
                        "frequency": base_frequency * freq_multiplier[i] * (1 + (intensity - 1) * 0.2), # 強度影響音高
                        "duration": durations[i] * max(0.8, 1/intensity), # 強度越高可能越短促
                        "volume": min(1.0, base_volume + i * 0.05),
                        "wavetype": wavetype
                    },
                    "startTime": sum(durations[:i]) * 1000 * max(0.7, 1/intensity) # 開始時間也受強度影響，可能更快
                })

        elif pattern == "serious":
            # 嚴肅模式 - 較低沉、持續稍長、可能帶有輕微不和諧
            freq_multiplier = [1, 0.8, 0.7]
            durations = [0.2, 0.3, 0.25]
            wavetype = "sine"
            for i in range(min(num_effects, 3)):
                effects.append({
                    "type": "beep",
                    "options": {
                        "frequency": base_frequency * freq_multiplier[i] * (1 - (intensity - 1) * 0.1), # 強度越高越低沉?
                        "duration": durations[i] * base_duration / 0.1, # 持續時間受基礎持續時間影響
                        "volume": base_volume * (1 - i * 0.1),
                        "wavetype": wavetype
                    },
                    "startTime": sum(durations[:i]) * 1000 * 1.2 # 節奏稍慢
                })
            # 增加複雜度時，可能加入低頻噪音
            if complexity > 1:
                 effects.append({
                    "type": "noise",
                    "options": {
                        "noiseType": "brown", "volume": base_volume * 0.1, "duration": 0.5,
                        "filter": {"type": "lowpass", "frequency": 300, "Q": 1}
                    }, "startTime": sum(durations[:min(num_effects,3)]) * 1000 * 1.2 
                })

        elif pattern == "question":
            # 疑問模式 - 明顯的結尾上揚
            final_pitch_bend = 1.2 * intensity # 強度影響上揚幅度
            effects = [
                {"type": "beep", "options": {"frequency": base_frequency * 0.9, "duration": base_duration * 0.8, "volume": base_volume, "wavetype": "sine"}, "startTime": 0},
                {"type": "beep", "options": {"frequency": base_frequency * final_pitch_bend, "duration": base_duration * 1.5, "volume": base_volume, "wavetype": "sine"}, "startTime": 100}
            ]
            if complexity > 1: # 增加一點裝飾音
                 effects.insert(1, {"type": "beep", "options": {"frequency": base_frequency * 1.1, "duration": base_duration * 0.5, "volume": base_volume * 0.7, "wavetype": "sine"}, "startTime": 50})

        elif pattern == "thinking":
             # 思考模式 - 慢速、稀疏、帶點延遲感
             interval = 400 * max(1, intensity) # 強度越高，停頓越久?
             freq_multiplier = [1, 1.1, 0.95]
             wavetype = "sine"
             for i in range(min(num_effects, 3)):
                 effects.append({
                     "type": "beep",
                     "options": {
                         "frequency": base_frequency * freq_multiplier[i],
                         "duration": base_duration * 1.2,
                         "volume": base_volume * 0.8,
                         "wavetype": wavetype,
                         # 可以考慮加 reverb 或 delay 效果，但 Tone.js 內建支持有限
                         # "effects": [{"type": "reverb", "decay": 0.5}] # 假設有此類效果
                     },
                     "startTime": i * interval
                 })
             if complexity > 1: # 加入微弱噪音
                 effects.append({
                     "type": "noise", 
                     "options": {"noiseType": "pink", "volume": base_volume * 0.05, "duration": interval * 0.8 / 1000}, 
                     "startTime": (min(num_effects, 3) - 1) * interval + base_duration * 1200
                 })

        elif pattern == "success":
             # 成功模式 - 歡快、上行的 fanfare
             freq_multiplier = [1, 1.25, 1.5, 2] # 類似 C-E-G-C 的感覺
             durations = [0.1, 0.08, 0.1, 0.15]
             wavetype = "triangle" if intensity > 0.8 else "sine"
             start_time = 0
             for i in range(min(num_effects, 4)):
                 effects.append({
                     "type": "beep",
                     "options": {
                         "frequency": base_frequency * freq_multiplier[i] * (1 + (intensity - 1) * 0.1),
                         "duration": durations[i],
                         "volume": min(1.0, base_volume + i * 0.05),
                         "wavetype": wavetype
                     },
                     "startTime": start_time
                 })
                 start_time += durations[i] * 1000 * 0.8 # 節奏緊湊

        elif pattern == "important":
             # 重要信息模式 - 衝擊感、強調
             effects = [
                 {
                     "type": "beep",
                     "options": {
                         "frequency": base_frequency,
                         "duration": base_duration * 1.5,
                         "volume": base_volume * 1.1, # 音量稍大
                         "wavetype": "sawtooth" # 更具穿透力的波形
                     },
                     "startTime": 0
                 }
             ]
             if complexity >= 1: # 至少有一個重複音強調
                 effects.append({
                     "type": "beep",
                     "options": {
                         "frequency": base_frequency * 0.95, # 輕微失諧增加衝擊感
                         "duration": base_duration * 1.5,
                         "volume": base_volume * 1.1,
                         "wavetype": "sawtooth"
                     },
                     "startTime": base_duration * 1500 * 1.2 # 稍有停頓
                 })
             if complexity > 1: # 更複雜時加入噪音衝擊
                 effects.append({
                    "type": "noise", 
                    "options": {"noiseType": "white", "volume": base_volume * 0.2, "duration": 0.1, 
                                "filter": {"type":"bandpass", "frequency": 1500, "Q": 2}}, 
                    "startTime": base_duration * 1500 * 1.2 + base_duration * 1500
                 })
             
        elif pattern == "tech":
             # 科技模式 - 快速、斷奏、方波，加入琶音感
             arpeggio = [1, 1.5, 2, 1.5] # 琶音序列
             duration = 0.05 * max(0.7, 1/intensity) # 強度高則更短促
             interval = 60 * max(0.7, 1/intensity)
             wavetype = "square"
             for i in range(min(num_effects, 4)):
                 effects.append({
                     "type": "beep",
                     "options": {
                         "frequency": base_frequency * arpeggio[i],
                         "duration": duration,
                         "volume": base_volume * (1 - i * 0.1),
                         "wavetype": wavetype
                     },
                     "startTime": i * interval
                 })
             if complexity > 1: # 加入高頻噪音點綴
                 effects.append({
                     "type": "noise",
                     "options": {"noiseType": "white", "volume": base_volume * 0.15, "duration": 0.08, 
                                 "filter": {"type": "highpass", "frequency": 4000, "Q": 1}},
                     "startTime": min(num_effects, 4) * interval
                 })

        elif pattern == "space":
             # 太空模式 - 空靈、延遲感
             effects = [
                {"type": "noise", "options": {"noiseType": "pink", "volume": base_volume * 0.4, "duration": base_duration * 3, "filter": {"type": "lowpass", "frequency": 800, "Q": 1}}, "startTime": 0},
                {"type": "beep", "options": {"frequency": base_frequency, "duration": base_duration * 2, "volume": base_volume * 0.7, "wavetype": "sine"}, "startTime": 100},
             ]
             if complexity > 0: # 至少有一個回聲效果
                 effects.append({"type": "beep", "options": {"frequency": base_frequency * 1.5, "duration": base_duration * 1.5, "volume": base_volume * 0.5, "wavetype": "sine"}, "startTime": 350 + base_duration * 100})
             if complexity > 1: # 更複雜時再加一個更高更遠的回聲
                 effects.append({"type": "beep", "options": {"frequency": base_frequency * 1.8, "duration": base_duration * 1.0, "volume": base_volume * 0.4, "wavetype": "sine"}, "startTime": 700 + base_duration * 200})

        # --- 新增綜藝模式 ---
        elif pattern == "funny": 
            # 搞笑/捧哏 - 快速滑稽音效 (用兩個快速音模擬)
            effects = [
                {"type": "beep", "options": {"frequency": base_frequency * 1.5, "duration": 0.05, "volume": base_volume, "wavetype": "square"}, "startTime": 0},
                {"type": "beep", "options": {"frequency": base_frequency * 0.8, "duration": 0.1, "volume": base_volume, "wavetype": "square"}, "startTime": 50}
            ]
        
        elif pattern == "fail":
            # 失敗 - 模擬 Trombone 下滑音
            effects = [
                {"type": "beep", "options": {"frequency": base_frequency, "duration": 0.3 * intensity, "volume": base_volume, "wavetype": "sawtooth", "detune": 0}, "startTime": 0},
                # Tone.js 本身不支持直接滑音，用多個音符近似
                {"type": "beep", "options": {"frequency": base_frequency * 0.8, "duration": 0.1 * intensity, "volume": base_volume * 0.9, "wavetype": "sawtooth", "detune": -100}, "startTime": 300 * intensity},
                {"type": "beep", "options": {"frequency": base_frequency * 0.6, "duration": 0.1 * intensity, "volume": base_volume * 0.8, "wavetype": "sawtooth", "detune": -200}, "startTime": 400 * intensity}
            ]

        elif pattern == "surprise":
            # 驚訝 - 短促、尖銳的聲音
            effects = [
                {"type": "beep", "options": {"frequency": base_frequency * 2 * intensity, "duration": 0.08, "volume": base_volume * 1.1, "wavetype": "sawtooth"}, "startTime": 0},
            ]
            if complexity > 0: # 加一個快速衰減的噪音
                effects.append({"type": "noise", "options": {"noiseType": "white", "volume": base_volume * 0.3, "duration": 0.1}, "startTime": 50})
        
        else:  # neutral 或未知模式
            # 中性模式 - 簡單、無干擾
            effects = [
                {"type": "beep", "options": {"frequency": base_frequency, "duration": 0.08, "volume": base_volume * 0.8, "wavetype": "sine"}, "startTime": 0}
            ]
            if complexity > 1:
                effects.append({"type": "beep", "options": {"frequency": base_frequency * 1.1, "duration": 0.06, "volume": base_volume * 0.6, "wavetype": "sine"}, "startTime": 150})
        
        # 確保 startTime 是毫秒數值
        for effect in effects:
            if 'startTime' in effect and isinstance(effect['startTime'], (int, float)):
                effect['startTime'] = int(effect['startTime']) # 轉為整數毫秒
            else:
                effect['startTime'] = 0 # 預設值

        return SoundEffectService.create_synth_sound_command(effects) 