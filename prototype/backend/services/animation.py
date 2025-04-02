import random
from typing import Dict, List, Optional

# 導入表情相關常量
from utils.constants import (
    PRESET_EXPRESSIONS,
    EMOTION_TO_MORPH_TARGETS
)

class AnimationService:
    """動畫與表情生成服務"""
    
    def create_transition_morph(
        self, 
        current_morph: Dict[str, float], 
        target_morph: Dict[str, float], 
        speed: float = 0.2
    ) -> Dict[str, float]:
        """
        創建過渡的Morph Target值
        
        Args:
            current_morph: 當前Morph狀態
            target_morph: 目標Morph狀態
            speed: 過渡速度
            
        Returns:
            過渡後的Morph狀態
        """
        result = {}
        
        for key in current_morph:
            current_val = current_morph[key]
            target_val = target_morph.get(key, 0.0)
            
            # 按速度向目標值過渡
            diff = target_val - current_val
            result[key] = current_val + diff * speed
        
        return result
    
    def calculate_morph_targets(self, emotion: str) -> Dict[str, float]:
        """
        計算指定情緒的Morph Target值
        
        Args:
            emotion: 情緒類型
            
        Returns:
            Morph Target字典
        """
        # 檢查情緒是否在預設表情中
        if emotion in PRESET_EXPRESSIONS:
            # 深拷貝以避免修改原始數據
            morph_targets = PRESET_EXPRESSIONS[emotion].copy()
            
            # 如果emotion是"reset"，確保所有值都是0
            if emotion == "reset":
                return morph_targets
                
            # 添加隨機眨眼的可能性
            if random.random() < 0.05:  # 5%機率眨眼
                morph_targets["eyeBlinkLeft"] = random.uniform(0.7, 1.0)
                morph_targets["eyeBlinkRight"] = random.uniform(0.7, 1.0)
                
            # 返回處理後的morph_targets
            return morph_targets
            
        # 如果找不到匹配的情緒，返回空字典
        print(f"警告: 找不到情緒 '{emotion}' 的表情設置")
        return {}
        
    def create_lipsync_morph(self, text: str, emotion: str = "neutral", duration: float = 3.0) -> List[Dict[str, float]]:
        """
        根據文本創建唇型同步幀序列，並融合情緒表情
        
        Args:
            text: 文本內容
            emotion: 情緒類型，默認為neutral
            duration: 持續時間
            
        Returns:
            唇型同步幀序列
        """
        # 簡化版的唇型同步算法
        
        # 獲取情緒基本表情
        emotion_morphs = EMOTION_TO_MORPH_TARGETS.get(emotion, EMOTION_TO_MORPH_TARGETS["neutral"]).copy()
        
        # 計算大約有多少個字符
        text_length = len(text.strip())
        
        # 根據文本長度調整持續時間（中文一個字約0.24秒，考慮更快的語速）
        if duration < text_length * 0.24:
            duration = text_length * 0.24
        
        # 計算需要多少幀
        # 假設30fps的播放速度
        frame_rate = 30
        total_frames = int(duration * frame_rate)
        
        # 創建幀序列
        frames = []
        
        # 主要變化的Morph Target - 包含嘴部和臉部表情
        mouth_morphs = {
            # 嘴部相關
            "jawOpen": 0.0,         # 下巴開合
            "mouthOpen": 0.0,       # 嘴巴開合
            "mouthFunnel": 0.0,     # 嘴巴圓形
            "mouthPucker": 0.0,     # 嘴巴撅起
            "mouthLeft": 0.0,       # 嘴巴左移
            "mouthRight": 0.0,      # 嘴巴右移
            "mouthSmileLeft": 0.0,  # 左邊微笑
            "mouthSmileRight": 0.0, # 右邊微笑
            "mouthFrownLeft": 0.0,  # 左邊撇嘴
            "mouthFrownRight": 0.0, # 右邊撇嘴
            "mouthStretchLeft": 0.0,# 嘴巴左拉伸
            "mouthStretchRight": 0.0,# 嘴巴右拉伸
            # 眉毛和眼睛相關
            "browInnerUp": 0.0,     # 內眉毛上揚
            "browOuterUpLeft": 0.0, # 左外眉毛上揚
            "browOuterUpRight": 0.0,# 右外眉毛上揚
            "eyeWideLeft": 0.0,     # 左眼睜大
            "eyeWideRight": 0.0,    # 右眼睜大
            "eyeSquintLeft": 0.0,   # 左眼瞇起
            "eyeSquintRight": 0.0,  # 右眼瞇起
            # 臉頰相關
            "cheekPuff": 0.0,       # 臉頰鼓起
            "cheekSquintLeft": 0.0, # 左臉頰擠壓
            "cheekSquintRight": 0.0,# 右臉頰擠壓
            # 增加更多眼睛和眉毛相關的形態值
            "eyeBlinkLeft": 0.0,    # 左眼眨眼
            "eyeBlinkRight": 0.0,   # 右眼眨眼
            "browDownLeft": 0.0,    # 左眉下垂
            "browDownRight": 0.0,   # 右眉下垂
            "noseSneerLeft": 0.0,   # 左鼻翼擴張
            "noseSneerRight": 0.0,  # 右鼻翼擴張
        }
        
        # 字符映射到唇型形態和表情
        char_to_morph = {
            'a': {'mouthOpen': 0.7, 'jawOpen': 0.4, 'eyeWideLeft': 0.1, 'eyeWideRight': 0.1},
            'e': {'mouthStretchLeft': 0.5, 'mouthStretchRight': 0.5, 'mouthOpen': 0.3, 'jawOpen': 0.2},
            'i': {'mouthStretchLeft': 0.7, 'mouthStretchRight': 0.7, 'mouthOpen': 0.2, 'eyeSquintLeft': 0.1, 'eyeSquintRight': 0.1},
            'o': {'mouthFunnel': 0.8, 'mouthOpen': 0.5, 'jawOpen': 0.3, 'eyeWideLeft': 0.2, 'eyeWideRight': 0.2},
            'u': {'mouthPucker': 0.8, 'mouthFunnel': 0.3, 'jawOpen': 0.2, 'browInnerUp': 0.1},
            'm': {'mouthPucker': 0.7, 'cheekPuff': 0.1},
            'b': {'mouthPucker': 0.5, 'mouthOpen': 0.1, 'cheekPuff': 0.3},
            'p': {'mouthPucker': 0.6, 'mouthOpen': 0.1, 'cheekPuff': 0.4},
            'w': {'mouthPucker': 0.8, 'browOuterUpLeft': 0.1, 'browOuterUpRight': 0.1},
            'f': {'mouthPucker': 0.3, 'mouthStretchLeft': 0.4, 'mouthStretchRight': 0.4, 'browInnerUp': 0.2},
            'v': {'mouthPucker': 0.3, 'mouthStretchLeft': 0.4, 'mouthStretchRight': 0.4, 'mouthOpen': 0.1},
        }
        
        # 簡化的中文字符到口型映射（中文使用拼音為基礎）
        cn_char_to_morph = {
            '啊': {'mouthOpen': 0.8, 'jawOpen': 0.7, 'eyeWideLeft': 0.3, 'eyeWideRight': 0.3, 'browOuterUpLeft': 0.2, 'browOuterUpRight': 0.2, 'browInnerUp': 0.2},
            '哦': {'mouthFunnel': 0.8, 'mouthOpen': 0.6, 'jawOpen': 0.4, 'eyeWideLeft': 0.2, 'eyeWideRight': 0.2, 'browInnerUp': 0.15},
            '嗯': {'mouthPucker': 0.5, 'jawOpen': 0.1, 'eyeSquintLeft': 0.2, 'eyeSquintRight': 0.2, 'browInnerUp': 0.2, 'cheekSquintLeft': 0.2, 'cheekSquintRight': 0.2},
            '吧': {'mouthPucker': 0.6, 'mouthOpen': 0.3, 'jawOpen': 0.2, 'cheekPuff': 0.2, 'browInnerUp': 0.1},
            '嘴': {'mouthStretchLeft': 0.5, 'mouthStretchRight': 0.5, 'mouthOpen': 0.4, 'eyeSquintLeft': 0.1, 'eyeSquintRight': 0.1, 'browInnerUp': 0.1},
            '呼': {'mouthFunnel': 0.6, 'mouthOpen': 0.3, 'jawOpen': 0.2, 'cheekPuff': 0.4, 'eyeWideLeft': 0.1, 'eyeWideRight': 0.1},
            '嘿': {'mouthStretchLeft': 0.4, 'mouthStretchRight': 0.4, 'mouthOpen': 0.6, 'jawOpen': 0.3, 'mouthSmileLeft': 0.3, 'mouthSmileRight': 0.3, 'eyeSquintLeft': 0.2, 'eyeSquintRight': 0.2},
            '嘻': {'mouthStretchLeft': 0.7, 'mouthStretchRight': 0.7, 'mouthOpen': 0.3, 'mouthSmileLeft': 0.5, 'mouthSmileRight': 0.5, 'eyeSquintLeft': 0.3, 'eyeSquintRight': 0.3, 'cheekSquintLeft': 0.3, 'cheekSquintRight': 0.3},
            '呵': {'mouthOpen': 0.5, 'jawOpen': 0.3, 'cheekSquintLeft': 0.2, 'cheekSquintRight': 0.2, 'mouthSmileLeft': 0.2, 'mouthSmileRight': 0.2},
            '哈': {'mouthOpen': 0.8, 'jawOpen': 0.6, 'eyeWideLeft': 0.4, 'eyeWideRight': 0.4, 'browOuterUpLeft': 0.3, 'browOuterUpRight': 0.3, 'browInnerUp': 0.2},
            '喔': {'mouthFunnel': 0.7, 'mouthOpen': 0.5, 'jawOpen': 0.3, 'browInnerUp': 0.2, 'eyeWideLeft': 0.15, 'eyeWideRight': 0.15},
            '！': {'eyeWideLeft': 0.4, 'eyeWideRight': 0.4, 'browOuterUpLeft': 0.3, 'browOuterUpRight': 0.3, 'browInnerUp': 0.3, 'mouthOpen': 0.2},
            '？': {'browInnerUp': 0.4, 'browOuterUpLeft': 0.3, 'browOuterUpRight': 0.3, 'eyeWideLeft': 0.2, 'eyeWideRight': 0.2, 'mouthStretchLeft': 0.1, 'mouthStretchRight': 0.1},
            '。': {'browInnerUp': 0.0, 'browOuterUpLeft': 0.0, 'browOuterUpRight': 0.0, 'eyeBlinkLeft': 0.1, 'eyeBlinkRight': 0.1},
            
            # 添加更多表情豐富的字符映射
            '哇': {'mouthFunnel': 0.9, 'jawOpen': 0.6, 'mouthOpen': 0.7, 'eyeWideLeft': 0.5, 'eyeWideRight': 0.5, 'browInnerUp': 0.4, 'browOuterUpLeft': 0.3, 'browOuterUpRight': 0.3},
            '呀': {'mouthOpen': 0.7, 'jawOpen': 0.5, 'eyeWideLeft': 0.3, 'eyeWideRight': 0.3, 'browInnerUp': 0.2, 'cheekSquintLeft': 0.1, 'cheekSquintRight': 0.1},
            '哎': {'mouthStretchLeft': 0.3, 'mouthStretchRight': 0.3, 'mouthOpen': 0.4, 'jawOpen': 0.3, 'browInnerUp': 0.3, 'eyeSquintLeft': 0.1, 'eyeSquintRight': 0.1},
            '呃': {'mouthOpen': 0.3, 'jawOpen': 0.2, 'browInnerUp': 0.4, 'eyeSquintLeft': 0.2, 'eyeSquintRight': 0.2, 'mouthStretchLeft': 0.2, 'mouthStretchRight': 0.2},
            '哼': {'mouthPucker': 0.4, 'jawOpen': 0.1, 'eyeSquintLeft': 0.4, 'eyeSquintRight': 0.4, 'browDownLeft': 0.3, 'browDownRight': 0.3, 'noseSneerLeft': 0.2, 'noseSneerRight': 0.2},
            '嘆': {'mouthOpen': 0.4, 'jawOpen': 0.3, 'browInnerUp': 0.5, 'eyeSquintLeft': 0.3, 'eyeSquintRight': 0.3, 'mouthFrownLeft': 0.2, 'mouthFrownRight': 0.2},
        }
        
        # 默認嘴型 - 適用於一般的中文發音
        default_morph = {
            'mouthOpen': 0.4, 
            'jawOpen': 0.3,
            'mouthStretchLeft': 0.2,
            'mouthStretchRight': 0.2
        }
        
        # 根據字元找出標點符號，用來調整表情
        punctuation_marks = ['！', '？', '。', '，', '.', ',', '!', '?']
        
        # 隨機化每個字符的帧數
        # 假設每個中文字符大約持續5-10帧
        chars = list(text.strip())
        min_frames_per_char = 5  # 每個字最少5幀
        max_frames_per_char = 10  # 最多10幀
        
        # 如果文本為空，產生一些基本的靜止帧
        if not chars:
            for _ in range(10):
                frames.append(mouth_morphs.copy())
            return frames
            
        # 為眨眼動作生成隨機時刻
        blink_frames = []
        if total_frames > 30:  # 只在較長的序列中添加眨眼
            num_blinks = random.randint(1, max(1, total_frames // 60))  # 每60幀眨約1次眼
            for _ in range(num_blinks):
                blink_frame = random.randint(15, total_frames - 15)  # 避免在開始和結束時眨眼
                blink_frames.append(blink_frame)
        
        # 生成每個字符的唇形幀
        current_frame = 0
        for i, char in enumerate(chars):
            # 獲取該字符的主要形態
            if char in cn_char_to_morph:
                morph = cn_char_to_morph[char].copy()
            elif char.lower() in char_to_morph:
                morph = char_to_morph[char.lower()].copy()
            else:
                morph = default_morph.copy()
                
            # 融合情緒表情 - 將情緒形態與字符形態結合
            # 只融合非口型的表情，避免影響發音
            for key, value in emotion_morphs.items():
                # 如果是非嘴部表情，且字符表情中未明確設置，加入情緒表情值
                if not key.startswith("mouth") and key != "jawOpen" and key != "jawForward" and key not in morph:
                    # 使用較輕的情緒值，避免表情過於強烈
                    morph[key] = value * 0.7
                # 如果是笑或皺眉等情緒表情，且原本就有一定值，加強該表情
                elif (key.startswith("mouthSmile") or key.startswith("mouthFrown")) and key in morph and value > 0.5:
                    morph[key] = max(morph[key], value * 0.8)  # 選擇較大值
                
            # 確定該字符的幀數
            if char in punctuation_marks:
                frames_for_char = min_frames_per_char
            else:
                frames_for_char = random.randint(min_frames_per_char, max_frames_per_char)
                
            # 為該字符生成幀
            for f in range(frames_for_char):
                # 複製基本形態
                frame_morph = mouth_morphs.copy()
                
                # 設定進度
                progress = f / frames_for_char
                
                # 應用形態值，考慮進度（給予一些淡入淡出效果）
                for key, value in morph.items():
                    # 進入時淡入，退出時淡出
                    if progress < 0.3:  # 淡入階段
                        factor = progress / 0.3
                    elif progress > 0.7:  # 淡出階段
                        factor = (1 - progress) / 0.3
                    else:  # 保持階段
                        factor = 1.0
                        
                    # 帶有一些隨機變化，但減小變化幅度以確保動畫更流暢
                    variation = random.uniform(-0.03, 0.03)
                    
                    frame_morph[key] = value * factor + variation
                    
                    # 確保值在有效範圍
                    frame_morph[key] = max(0, min(1, frame_morph[key]))
                
                # 檢查是否需要在此幀眨眼
                if current_frame in blink_frames:
                    frame_morph["eyeBlinkLeft"] = 0.9
                    frame_morph["eyeBlinkRight"] = 0.9
                # 在眨眼後的下一幀，恢復眼睛
                elif current_frame - 1 in blink_frames:
                    frame_morph["eyeBlinkLeft"] = 0.3
                    frame_morph["eyeBlinkRight"] = 0.3
                # 再下一幀，完全恢復
                elif current_frame - 2 in blink_frames:
                    frame_morph["eyeBlinkLeft"] = 0.0
                    frame_morph["eyeBlinkRight"] = 0.0
                
                # 添加幀到序列
                frames.append(frame_morph)
                current_frame += 1
                
                # 檢查是否超出總幀數
                if current_frame >= total_frames:
                    return frames
        
        # 如果沒有填滿所有幀，添加一些閉嘴的幀
        while current_frame < total_frames:
            # 使用情緒形態作為結束，但嘴部關閉
            neutral_morph = {k: 0.0 for k in mouth_morphs}
            
            # 保留一些情緒表情，使結束更自然
            for key, value in emotion_morphs.items():
                if not key.startswith("mouth") and key != "jawOpen":
                    neutral_morph[key] = value * 0.5  # 使用較輕的情緒值
            
            frames.append(neutral_morph)
            current_frame += 1
            
        return frames 