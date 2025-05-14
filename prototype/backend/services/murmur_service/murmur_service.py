"""
MurmurService class for managing self-talk functionality.

This service handles:
- Murmur triggering based on idle time
- Murmur generation with context memory
- Configuration options for enabling/disabling features
"""

import random
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Any

from . import config
from . import utils
from utils.logger import logger
from services.ai import AIService
from services.text_to_speech import TextToSpeechService
from services.ai.prompts import PROMPT_TEMPLATES


class MurmurService:
    """Service for managing and generating murmurs (self-talk)."""
    
    def __init__(self, ai_service: AIService = None, tts_service: TextToSpeechService = None, user_config: Dict[str, Any] = None):
        """
        Initialize the MurmurService.
        
        Args:
            ai_service: AIService instance for generating murmur content
            tts_service: TextToSpeechService instance for converting murmur to speech
            user_config: Configuration options for the murmur service
        """
        # 服務依賴
        self.ai_service = ai_service or AIService()
        self.tts_service = tts_service or TextToSpeechService()
        
        # 配置信息 - 增加默認連續思考次數
        self.config = {
            **config.DEFAULT_CONFIG, 
            "max_thread_continuity": 12,  # 從8增加到12，讓連續思考可以持續更長時間
            **(user_config or {})
        }
        self.enabled = self.config.get('enabled', True)
        self.context_memory_enabled = self.config.get('context_memory_enabled', True)
        
        # 狀態跟踪
        self.recent_murmurs: Set[str] = set()  
        self.last_murmur_timestamp: Optional[datetime] = None
        self.current_thinking_topic = random.choice(config.THINKING_THEMES)
        self.thinking_thread_continuity = 0
        self.last_murmur_content = ""
    
    def maybe_trigger_murmur(self, idle_duration: timedelta, speaking_state: str, 
                             last_speaking_reset_time: Optional[datetime] = None) -> bool:
        """
        判斷是否應該觸發murmur生成，基於閒置時間和當前狀態。
        
        Args:
            idle_duration: 閒置時間長度
            speaking_state: 當前語音狀態
            last_speaking_reset_time: 最後一次說話重置的時間
            
        Returns:
            bool: 是否應該觸發murmur
        """
        if not self.enabled:
            return False
            
        # 檢查是否在語音狀態完成後需要等待
        should_wait_after_speaking = False
        if last_speaking_reset_time:
            time_since_last_reset_seconds = (datetime.utcnow() - last_speaking_reset_time).total_seconds()
            should_wait_after_speaking = time_since_last_reset_seconds < 1.0  # 減少等待時間
        
        # 決定是否滿足murmur條件
        return (
            idle_duration > timedelta(seconds=self.config.get('idle_timeout_seconds', config.IDLE_TIMEOUT_SECONDS)) and
            (self.last_murmur_timestamp is None or 
             datetime.utcnow() - self.last_murmur_timestamp > timedelta(seconds=self.config.get('min_interval_seconds', config.MURMUR_MIN_INTERVAL_SECONDS))) and
            speaking_state == config.SpeakingState.IDLE and
            not should_wait_after_speaking
        )
    
    async def generate_murmur(self, conversation_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        生成一條murmur，並獲取需要的信息。
        
        Args:
            conversation_history: 對話歷史，用於生成上下文相關的murmur
            
        Returns:
            Dict包含生成的murmur文本、音頻、時長等信息
        """
        # 如果服務未啟用，則直接返回空結果
        if not self.enabled:
            return {}
        
        # --- 決定是否要更換思考主題
        if self.thinking_thread_continuity >= self.config.get('max_thread_continuity', 4):
            # 隨機選擇新主題，但避免選到當前主題
            available_themes = [t for t in self.config.get('thinking_themes', config.THINKING_THEMES) 
                               if t != self.current_thinking_topic]
            self.current_thinking_topic = random.choice(available_themes)
            self.thinking_thread_continuity = 0
            logger.info(f"切換思考主題至: {self.current_thinking_topic}")
        else:
            self.thinking_thread_continuity += 1
            logger.info(f"連續第 {self.thinking_thread_continuity} 次思考主題: {self.current_thinking_topic}")
        
        # --- 構建思考上下文提示
        context_prompt = ""
        thinking_thread = ""
        
        # 決定是否使用先前murmur作為思考線索
        if self.context_memory_enabled and self.recent_murmurs:
            recent_murmurs_list = list(self.recent_murmurs)
            if len(recent_murmurs_list) > 0:
                # 最近的 murmur 作為直接延續的基礎
                self.last_murmur_content = recent_murmurs_list[-1]
                thinking_thread = f"你上一次的想法是：「{self.last_murmur_content}」，請直接且明確地延續這個想法。"
                logger.info(f"使用上一次思考作為連續性基礎: {self.last_murmur_content[:30]}...")
        
        # --- 根據連續程度選擇不同的提示模板
        prompt_template = "murmur_continuous" if self.thinking_thread_continuity > 0 else "murmur"
        logger.info(f"使用模板: {prompt_template}，連續性指數: {self.thinking_thread_continuity}")
        
        # 獲取對應的 murmur 提示模板並填充變量
        template = PROMPT_TEMPLATES.get(prompt_template, PROMPT_TEMPLATES["murmur"])
        
        # --- 新增：準備 optional seeds ---
        # 您可以在此處加入更複雜的邏輯來生成這些 seeds，
        # 例如從預設列表隨機選取，或根據對話歷史分析等。
        # 目前，我們先使用空字串作為預設值。
        optional_emotional_seed_value = "" 
        optional_situational_seed_value = ""
        # --- 結束新增 ---

        # 格式化提示模板
        if prompt_template == "murmur_continuous":
            murmur_prompt = template.format(
                optional_emotional_seed=optional_emotional_seed_value,
                optional_situational_seed=optional_situational_seed_value,
                context_prompt=context_prompt,
                current_topic=self.current_thinking_topic,
                thinking_thread=thinking_thread
            )
        else:
            murmur_prompt = template.format(
                optional_emotional_seed=optional_emotional_seed_value,
                optional_situational_seed=optional_situational_seed_value,
                context_prompt=context_prompt
            )
        
        try:
            # 確保至少有一條初始化消息在歷史中，避免出現"至少需要提供一條消息"的錯誤
            temp_history = conversation_history.copy() if conversation_history else []
            
            # 如果對話歷史為空，添加一個初始消息以保證API調用成功
            if not temp_history:
                temp_history = [{"role": "bot", "content": "你好！我是星宅妹。", "is_murmur": False}]
                logger.info("對話歷史為空，添加初始化消息")
            
            # 生成murmur
            ai_result = await self.ai_service.generate_response(
                system_prompt=murmur_prompt,
                history=temp_history
            )
            
            if not ai_result or "final_response" not in ai_result:
                logger.error("AIService failed to generate murmur or returned invalid format.")
                return {}
                
            ai_murmur_text = ai_result.get("final_response")
            ai_murmur_text = utils.clean_murmur_prefix(ai_murmur_text)
            
            # --- 根據連續思考模式調整相似度判斷
            has_continuity_marker = utils.has_continuity_marker(ai_murmur_text)
            similarity_threshold = utils.calculate_similarity_threshold(
                self.thinking_thread_continuity, 
                has_continuity_marker
            )
            
            # 專門用於連續思考的相似度調整
            if self.thinking_thread_continuity > 0 and has_continuity_marker:
                # 進一步降低連續思考的相似度閾值，確保思考流能繼續
                similarity_threshold *= 0.8
                logger.info(f"連續思考模式: 降低相似度閾值至 {similarity_threshold}")
            
            # 檢查是否與現有murmur太相似
            if self.recent_murmurs and utils.is_murmur_too_similar(
                ai_murmur_text, 
                self.recent_murmurs, 
                similarity_threshold
            ):
                logger.warning(f"Generated murmur is too similar to existing ones, skipping: '{ai_murmur_text}'")
                return {}
            
            # 將內容添加到最近murmurs
            self.last_murmur_content = ai_murmur_text
            self.recent_murmurs.add(ai_murmur_text)
            
            # 控制記憶容量
            max_stored = self.config.get('max_stored_murmurs', 10)
            if len(self.recent_murmurs) > max_stored:
                # 移除最舊的murmur
                oldest = next(iter(self.recent_murmurs))
                self.recent_murmurs.remove(oldest)
                logger.info(f"Removed oldest murmur from set: '{oldest}'")
            
            # 轉換為音頻
            tts_result = await self.tts_service.synthesize_speech(ai_murmur_text)
            audio_base64 = tts_result.get("audio") if tts_result else None
            audio_duration = tts_result.get("duration", len(ai_murmur_text) * 0.15)
            
            # 更新最近murmur時間戳
            self.last_murmur_timestamp = datetime.utcnow()
            
            # 返回最終結果
            return {
                "text": ai_murmur_text,
                "audio": audio_base64,
                "duration": audio_duration,
                "emotion": ai_result.get("emotion", "neutral"),
                "bodyAnimationSequence": ai_result.get("body_animation_sequence"),
                "emotionalKeyframes": ai_result.get("emotional_keyframes"),
                "is_murmur": True,
                "is_continuous": self.thinking_thread_continuity > 0,
                "thinking_topic": self.current_thinking_topic
            }
        except Exception as e:
            logger.error(f"Error generating murmur: {e}", exc_info=True)
            return {}
    
    def reset_murmur_timestamp(self):
        """重置最近murmur的時間戳，用於在回應用戶後重新設定計時器"""
        self.last_murmur_timestamp = datetime.utcnow()
    
    def get_recent_murmurs(self) -> Set[str]:
        """獲取最近的murmur集合"""
        return self.recent_murmurs.copy()
    
    def clear_murmur_memory(self):
        """清除所有記憶的murmur，通常在對話重置時使用"""
        self.recent_murmurs.clear()
        self.last_murmur_content = ""
        self.thinking_thread_continuity = 0
    
    def toggle_enabled(self, enabled: bool = None):
        """開啟或關閉murmur功能"""
        if enabled is not None:
            self.enabled = enabled
        else:
            self.enabled = not self.enabled
        return self.enabled
    
    def toggle_context_memory(self, enabled: bool = None):
        """開啟或關閉murmur上下文記憶功能"""
        if enabled is not None:
            self.context_memory_enabled = enabled
        else:
            self.context_memory_enabled = not self.context_memory_enabled
        return self.context_memory_enabled
    
    def update_config(self, new_config: Dict[str, Any]):
        """更新服務配置"""
        self.config.update(new_config)
        # 更新快捷訪問的設定
        self.enabled = self.config.get('enabled', True)
        self.context_memory_enabled = self.config.get('context_memory_enabled', True) 