import logging
import random
from typing import Dict, Tuple, List

# 設置日誌
logger = logging.getLogger(__name__)

class EmotionAnalyzer:
    """情緒分析服務"""
    
    def __init__(self):
        # 各情緒的關鍵詞和權重
        self.emotion_keywords = {
            "angry": [
                ("生氣", 0.9), ("憤怒", 0.9), ("煩", 0.7), ("討厭", 0.8), 
                ("厭惡", 0.8), ("恨", 0.9), ("氣死", 0.9), ("不爽", 0.7),
                ("滾", 0.8), ("笨蛋", 0.7), ("白痴", 0.8), ("蠢", 0.7)
            ],
            "happy": [
                ("高興", 0.8), ("開心", 0.8), ("快樂", 0.8), ("喜歡", 0.7), 
                ("愛", 0.7), ("爽", 0.6), ("棒", 0.7), ("讚", 0.7), 
                ("謝謝", 0.6), ("感謝", 0.6), ("太好了", 0.8), ("哈哈", 0.7)
            ],
            "sad": [
                ("悲傷", 0.9), ("傷心", 0.9), ("難過", 0.9), ("哭", 0.8), 
                ("嘆", 0.7), ("可憐", 0.7), ("遺憾", 0.7), ("抱歉", 0.5), 
                ("對不起", 0.5), ("失望", 0.8), ("痛苦", 0.9), ("絕望", 0.9)
            ],
            "surprised": [
                ("驚訝", 0.9), ("驚嚇", 0.9), ("驚喜", 0.8), ("嚇", 0.7), 
                ("天啊", 0.7), ("哇", 0.5), ("不會吧", 0.7), ("真的嗎", 0.6), 
                ("是嗎", 0.5), ("什麼", 0.3), ("為什麼", 0.3), ("怎麼會", 0.6),
                ("竟然", 0.8), ("居然", 0.8)
            ],
            "question": [
                ("誰", 0.6), ("什麼", 0.6), ("怎麼", 0.6), ("為什麼", 0.6),
                ("如何", 0.6), ("哪裡", 0.6), ("多少", 0.6), ("幾", 0.5),
                ("嗎", 0.4), ("呢", 0.3), ("?", 0.5), ("？", 0.5)
            ],
            "neutral": [
                ("是的", 0.5), ("對", 0.5), ("好", 0.4), ("嗯", 0.4),
                ("了解", 0.5), ("知道了", 0.5), ("明白", 0.5)
            ]
        }
        
        # 預設表情配置 - 各種情緒下的面部表情設置
        self.emotion_morphs = self._create_emotion_morphs()

    def _get_all_morph_keys(self) -> List[str]:
        """獲取所有可用的變形目標鍵名"""
        # 直接返回所有可能的變形目標鍵名，而不是從self.emotion_morphs中提取
        return [
            "browDownLeft", "browDownRight", "browInnerUp", "browOuterUpLeft", "browOuterUpRight",
            "cheekPuff", "cheekSquintLeft", "cheekSquintRight",
            "eyeBlinkLeft", "eyeBlinkRight", "eyeLookDownLeft", "eyeLookDownRight",
            "eyeLookInLeft", "eyeLookInRight", "eyeLookOutLeft", "eyeLookOutRight",
            "eyeLookUpLeft", "eyeLookUpRight", "eyeSquintLeft", "eyeSquintRight",
            "eyeWideLeft", "eyeWideRight",
            "jawForward", "jawLeft", "jawOpen", "jawRight",
            "mouthClose", "mouthDimpleLeft", "mouthDimpleRight",
            "mouthFrownLeft", "mouthFrownRight", "mouthFunnel",
            "mouthLeft", "mouthLowerDownLeft", "mouthLowerDownRight",
            "mouthPressLeft", "mouthPressRight", "mouthPucker", "mouthRight",
            "mouthRollLower", "mouthRollUpper", "mouthShrugLower", "mouthShrugUpper",
            "mouthSmileLeft", "mouthSmileRight", "mouthStretchLeft", "mouthStretchRight",
            "mouthUpperUpLeft", "mouthUpperUpRight",
            "noseSneerLeft", "noseSneerRight", "headLeftRight"
        ]

    def _create_emotion_morphs(self) -> Dict[str, Dict[str, float]]:
        """
        創建情緒到表情變形的映射
        
        Returns:
            情緒-表情變形映射
        """
        morphs = {}
        
        # 開心表情
        morphs["happy"] = {
            "browInnerUp": 0.5,
            "mouthSmileLeft": 1.0,
            "mouthSmileRight": 1.0,
            "eyeSquintLeft": 0.6,
            "eyeSquintRight": 0.6,
            "cheekSquintLeft": 0.7,
            "cheekSquintRight": 0.7,
            "mouthDimpleLeft": 0.5,
            "mouthDimpleRight": 0.5,
            "mouthStretchLeft": 0.2,
            "mouthStretchRight": 0.2,
            "mouthUpperUpLeft": 0.3,
            "mouthUpperUpRight": 0.3,
        }
        
        # 悲傷表情
        morphs["sad"] = {
            "browInnerUp": 0.9,
            "browOuterUpLeft": 0.2,
            "browOuterUpRight": 0.2,
            "mouthFrownLeft": 0.9,
            "mouthFrownRight": 0.9,
            "mouthLowerDownLeft": 0.6,
            "mouthLowerDownRight": 0.6,
            "eyeLookDownLeft": 0.5,
            "eyeLookDownRight": 0.5,
            "eyeBlinkLeft": 0.2,
            "eyeBlinkRight": 0.2,
            "cheekSquintLeft": 0.3,
            "cheekSquintRight": 0.3,
        }
        
        # 生氣表情
        morphs["angry"] = {
            "browDownLeft": 0.9,
            "browDownRight": 0.9,
            "eyeSquintLeft": 0.7,
            "eyeSquintRight": 0.7,
            "jawForward": 0.4,
            "mouthStretchLeft": 0.3,
            "mouthStretchRight": 0.3,
            "mouthFrownLeft": 0.6,
            "mouthFrownRight": 0.6,
            "noseSneerLeft": 0.5,
            "noseSneerRight": 0.5,
        }
        
        # 驚訝表情
        morphs["surprised"] = {
            "browInnerUp": 1.0,
            "browOuterUpLeft": 0.9,
            "browOuterUpRight": 0.9,
            "eyeWideLeft": 1.0,
            "eyeWideRight": 1.0,
            "jawOpen": 0.7,
            "mouthOpen": 0.8,
            "eyeLookUpLeft": 0.4,
            "eyeLookUpRight": 0.4,
        }
        
        # 問題表情 (好奇)
        morphs["question"] = {
            "browInnerUp": 0.7,
            "browOuterUpLeft": 0.4,
            "browOuterUpRight": 0.1,  # 不對稱，增加表現力
            "eyeWideLeft": 0.3,
            "eyeWideRight": 0.3,
            "jawOpen": 0.3,
            "mouthOpen": 0.2,
            "headLeftRight": 0.2,  # 輕微側頭
        }
        
        # 中性表情 - 所有值重置為0
        morphs["neutral"] = {key: 0.0 for key in self._get_all_morph_keys()}
        
        return morphs
    
    def analyze(self, text: str) -> Tuple[str, float]:
        """
        分析文本情緒
        
        Args:
            text: 輸入文本
            
        Returns:
            情緒類型和置信度的元組
        """
        if not text:
            return "neutral", 0.5
            
        text = text.lower()
        
        # 計算每種情緒的分數
        emotion_scores = {emotion: 0.0 for emotion in self.emotion_keywords}
        max_score = 0.0
        detected_emotion = "neutral"
        
        # 檢查文本中是否存在情緒關鍵詞
        for emotion, keywords in self.emotion_keywords.items():
            for keyword, weight in keywords:
                if keyword in text:
                    emotion_scores[emotion] += weight
                    
                    # 根據關鍵詞出現的位置和頻率調整權重
                    if text.startswith(keyword):  # 句首出現權重更高
                        emotion_scores[emotion] += 0.2
                        
                    count = text.count(keyword)
                    if count > 1:  # 多次出現同一關鍵詞
                        emotion_scores[emotion] += 0.1 * (count - 1)
        
        # 文本長度調整係數
        length_factor = min(1.0, len(text) / 50.0)  # 較長文本更可信
        
        # 找出最高分的情緒
        for emotion, score in emotion_scores.items():
            # 應用長度調整係數
            adjusted_score = score * (0.5 + 0.5 * length_factor)
            
            if adjusted_score > max_score:
                max_score = adjusted_score
                detected_emotion = emotion
        
        # 混合情緒處理: 如果是問題，但又帶有明顯情緒
        if detected_emotion == "question":
            # 檢查是否有其他高分情緒
            second_emotion = None
            second_score = 0
            
            for emotion, score in emotion_scores.items():
                if emotion != "question" and score > second_score:
                    second_emotion = emotion
                    second_score = score
            
            # 如果存在明顯的次要情緒，且分數接近問題分數的一半以上
            if second_emotion and second_score > max_score * 0.5:
                detected_emotion = second_emotion
                max_score = second_score
        
        # 正常化信心分數到0-1範圍
        confidence = min(1.0, max_score / 2.0)
        
        # 如果沒有明顯情緒，默認為中性
        if confidence < 0.3:
            return "neutral", 0.5
            
        logger.info(f"情緒分析結果: {detected_emotion}, 置信度: {confidence:.2f}")
        return detected_emotion, confidence
    
    def get_morphs(self, emotion: str, add_randomness: bool = True) -> Dict[str, float]:
        """
        獲取指定情緒的變形目標
        
        Args:
            emotion: 情緒類型
            add_randomness: 是否添加隨機性
            
        Returns:
            變形目標字典
        """
        # 獲取基本變形
        base_morphs = self.emotion_morphs.get(emotion, self.emotion_morphs["neutral"]).copy()
        
        # 添加隨機性
        if add_randomness:
            for key in base_morphs:
                if base_morphs[key] > 0:
                    # 添加±5%的隨機變化
                    variance = base_morphs[key] * 0.05
                    base_morphs[key] += random.uniform(-variance, variance)
                    # 確保值在有效範圍
                    base_morphs[key] = max(0, min(1, base_morphs[key]))
        
        return base_morphs 