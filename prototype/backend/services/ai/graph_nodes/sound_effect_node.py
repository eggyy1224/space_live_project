import logging
import asyncio
import re
import traceback
from typing import Dict, Any, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor

from services.sound_effect.sound_effect_service import SoundEffectService

logger = logging.getLogger(__name__)


class SoundEffectNode:
    """
    音效節點類 - 根據對話內容生成適合的Tone.js音效信號
    設計為非同步處理，不影響主對話節點回應速度
    """
    
    def __init__(self):
        """初始化音效節點"""
        logger.info("【音效節點】初始化SoundEffectNode")
        self.sound_effect_service = SoundEffectService()
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._patterns = self._compile_patterns()
        logger.info("【音效節點】SoundEffectNode初始化完成，正則表達式模式已編譯")
        
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """編譯用於識別文本特徵的正則表達式模式"""
        try:
            logger.info("【音效節點】開始編譯正則表達式模式")
            patterns = {
                # 高音調模式
                "high_pitch": re.compile(r'(!{2,}|？{2,}|?{2,}|哇{1,}|啊{2,}|驚訝|驚喜|不敢相信|天啊|真的嗎|驚奇|好奇|為什麼)', re.IGNORECASE),
                
                # 低音調模式
                "low_pitch": re.compile(r'(唉{1,}|哎{1,}|嘆息|沮喪|失望|可惜|無奈|遺憾|抱歉|對不起|難過|傷心)', re.IGNORECASE),
                
                # 問句模式
                "question": re.compile(r'(嗎?|呢?|為什麼|什麼時候|怎樣|如何|誰|何時|何地|哪裡|是否|能不能|可以嗎|?$|？$)', re.IGNORECASE),
                
                # 思考模式
                "thinking": re.compile(r'(思考|考慮|分析|讓我想想|或許|可能|也許|應該|我認為|按理說|理論上|建議|推測)', re.IGNORECASE),
                
                # 成功模式
                "success": re.compile(r'(成功|太好了|完成|做到了|解決|搞定|好耶|耶|棒|優秀|做得好)', re.IGNORECASE),
                
                # 重要信息模式
                "important": re.compile(r'(重要|必須|一定|必要|關鍵|特別注意|警告|提醒|注意|記住|謹記)', re.IGNORECASE),
                
                # 科技相關模式
                "tech": re.compile(r'(技術|科技|系統|程序|代碼|軟件|硬件|數據|信息|網絡|設備|編程|電腦|AI|人工智能|機器學習)', re.IGNORECASE),
                
                # 太空相關模式
                "space": re.compile(r'(太空|宇宙|星球|衛星|行星|火箭|飛船|星際|銀河|宇航員|太陽系|月球|軌道|星雲)', re.IGNORECASE),
                
                # --- 新增綜藝模式 ---
                "funny": re.compile(r'(哈哈|XD|笑死|有趣|好笑|幽默|梗|滑稽|噗嗤|逗)', re.IGNORECASE),
                "fail": re.compile(r'(失敗|搞砸了|完蛋|糟糕|錯誤|不行|壞了|GG|糗)', re.IGNORECASE),
                "surprise": re.compile(r'(哇塞|竟然|居然|沒想到|什麼|真的假的|我的天)', re.IGNORECASE),
                # 增加感嘆號的匹配，用於提升強度
                "exclamation": re.compile(r'[!！]+')
            }
            
            # 記錄每個模式的樣例
            for pattern_name, pattern in patterns.items():
                logger.debug(f"【音效節點】編譯模式: {pattern_name}, 樣式: {pattern.pattern}")
            
            logger.info(f"【音效節點】正則表達式模式編譯完成，共 {len(patterns)} 個模式")
            return patterns
            
        except Exception as e:
            logger.error(f"【音效節點】編譯正則表達式模式時出錯: {str(e)}")
            logger.error(f"【音效節點】錯誤堆疊: {traceback.format_exc()}")
            # 返回一個空字典作為備用
            return {}
    
    async def process_dialogue(self, dialogue_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        非同步處理對話結果，生成適合的音效
        
        Args:
            dialogue_result: 對話節點的結果，包含response等信息
            
        Returns:
            格式化的Tone.js音效命令，或None
        """
        logger.info("【音效節點】=== 開始處理對話結果以生成音效 ===")
        
        if not dialogue_result:
            logger.warning("【音效節點】接收到空的對話結果，無法處理")
            return None
            
        # 記錄接收到的對話結果結構
        logger.info(f"【音效節點】接收到對話結果: keys={list(dialogue_result.keys())}")
        if 'response' in dialogue_result:
            response_keys = list(dialogue_result['response'].keys()) if isinstance(dialogue_result['response'], dict) else "非字典"
            logger.info(f"【音效節點】對話回應結構: keys={response_keys}")
            
            # 記錄文本內容的前30個字符，幫助診斷
            if isinstance(dialogue_result['response'], dict) and 'text' in dialogue_result['response']:
                text = dialogue_result['response']['text']
                logger.info(f"【音效節點】文本內容前30字符: '{text[:30]}'...")
        else:
            logger.warning("【音效節點】對話結果中沒有response字段")
        
        try:
            # 使用線程池執行文本分析，不阻塞主協程
            logger.info("【音效節點】開始非同步處理對話音效")
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, 
                self._analyze_and_generate_sound, 
                dialogue_result
            )
            
            if result:
                logger.info(f"【音效節點】成功生成音效命令: type={result.get('type')}")
                if 'payload' in result:
                    logger.info(f"【音效節點】音效命令payload: keys={list(result['payload'].keys())}")
                
                # 格式化並顯示部分音效內容以便調試
                if 'payload' in result and 'effects' in result['payload']:
                    effects = result['payload']['effects']
                    effect_count = len(effects)
                    logger.info(f"【音效節點】生成了{effect_count}個音效效果")
                    for i, effect in enumerate(effects[:2]):  # 只記錄前兩個效果
                        logger.info(f"【音效節點】效果{i+1}: type={effect.get('type')}, startTime={effect.get('startTime')}")
                    
                    # 添加完整音效命令的日誌，方便檢查
                    import json
                    logger.info(f"【音效節點】完整音效命令: {json.dumps(result)[:200]}...")
                
                logger.info("【音效節點】=== 完成音效處理，返回結果 ===")
                return result
            else:
                logger.warning("【音效節點】音效生成結果為空")
                return None
                
        except Exception as e:
            logger.error(f"【音效節點】處理對話時出錯: {str(e)}")
            logger.error(f"【音效節點】錯誤堆疊: {traceback.format_exc()}")
            return None
            
    def _analyze_and_generate_sound(self, dialogue_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        分析對話內容並生成對應的音效命令
        
        Args:
            dialogue_result: 對話節點的結果
            
        Returns:
            格式化的音效命令，或None
        """
        try:
            # 從對話結果中提取文本
            logger.debug("【音效節點】從對話結果中提取文本")
            response = dialogue_result.get("response", {})
            text = response.get("text", "")
            
            if not text:
                logger.warning("【音效節點】對話結果中沒有文本內容，無法生成音效")
                return None
                
            logger.info(f"【音效節點】開始分析文本: {text[:50]}{'...' if len(text) > 50 else ''}")
                
            # 新增：強度計算
            intensity = 1.0
            # 需要先檢查 self._patterns 是否存在以及 'exclamation' key 是否存在
            exclamation_pattern = self._patterns.get("exclamation")
            if exclamation_pattern:
                exclamation_matches = exclamation_pattern.findall(text)
                if exclamation_matches:
                     # 每個感嘆號增加一點強度，但有上限
                     intensity = min(1.5, 1.0 + len(exclamation_matches) * 0.1)
                     logger.debug(f"【音效節點】檢測到感嘆號，強度提升至: {intensity:.2f}")
            else:
                logger.warning("【音效節點】無法找到 'exclamation' 正則表達式模式")
            
            # 分析文本並確定音效特徵
            sound_profile = self._analyze_text_for_sound_profile(text)
            logger.info(f"【音效節點】分析結果: pattern={sound_profile['pattern']}, base_frequency={sound_profile['base_frequency']}")
            
            # 根據分析結果生成Tone.js音效
            logger.info(f"【音效節點】開始生成{sound_profile['pattern']}類型的音效")
            result = self._generate_tone_sound_effect(sound_profile)
            logger.info("【音效節點】音效生成完成")
            return result
        except Exception as e:
            logger.error(f"【音效節點】分析對話並生成音效時出錯: {str(e)}")
            logger.error(f"【音效節點】錯誤堆疊: {traceback.format_exc()}")
            return None
    
    def _analyze_text_for_sound_profile(self, text: str) -> Dict[str, Any]:
        """
        分析文本內容，提取適合音效生成的特徵
        
        Args:
            text: 對話文本
            
        Returns:
            音效特徵配置
        """
        logger.debug("【音效節點】開始分析文本特徵")
        # 初始化音效配置
        profile = {
            'base_frequency': 440,  # 基礎頻率 (A4)
            'duration': 0.1,        # 基礎持續時間
            'volume': 0.5,          # 基礎音量
            'wave_type': 'sine',    # 基礎波形
            'pattern': 'neutral',   # 預設模式
            'complexity': 1,        # 音效複雜度 (1-3)
            'urgency': 0,           # 緊急度 (0-1)
            'sentences': []         # 分句存儲
        }
        
        try:
            # 分句處理
            sentences = re.split(r'[。！？!?]', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                logger.warning("【音效節點】無法從文本中提取有效句子")
                return profile
            
            # 記錄分句，用於生成節奏
            profile['sentences'] = sentences
            logger.debug(f"【音效節點】提取了{len(sentences)}個句子: {sentences[:2]}...")
            
            # 根據句子數量調整複雜度
            profile['complexity'] = min(3, max(1, len(sentences) // 2))
            
            # 分析文本模式
            matched_patterns = []
            
            # 記錄未編譯的模式數量，幫助診斷
            if not self._patterns:
                logger.warning("【音效節點】沒有有效的正則表達式模式，將使用默認音效配置")
                return profile
                
            for pattern_name, pattern in self._patterns.items():
                try:
                    if pattern.search(text):
                        matched_patterns.append(pattern_name)
                        logger.debug(f"【音效節點】匹配到模式: {pattern_name}")
                except Exception as e:
                    logger.error(f"【音效節點】模式 {pattern_name} 匹配時出錯: {str(e)}")
            
            logger.info(f"【音效節點】匹配到的模式: {matched_patterns}")
            
            # --- 模式選擇邏輯 (優先級 & 結合情緒) ---
            final_pattern = 'neutral' # 預設模式
            # 修正：從 dialogue_result 中獲取 AI 情緒
            ai_emotion = dialogue_result.get("response", {}).get("emotion", "neutral") 
            logger.debug(f"【音效節點】獲取到 AI 情緒: {ai_emotion}")

            # 最高優先級：明確的綜藝反應
            if 'fail' in matched_patterns: final_pattern = 'fail'
            elif 'surprise' in matched_patterns: final_pattern = 'surprise'
            elif 'success' in matched_patterns: final_pattern = 'success'
            elif 'funny' in matched_patterns: final_pattern = 'funny'
            
            # 次級優先級：疑問、重要性、思考
            elif 'question' in matched_patterns: final_pattern = 'question'
            elif 'important' in matched_patterns: 
                final_pattern = 'important'
                intensity = max(intensity, 1.2) # 重要信息強度至少1.2
            elif 'thinking' in matched_patterns: final_pattern = 'thinking'
            
            # 情緒/語氣相關模式
            elif 'high_pitch' in matched_patterns or ai_emotion in ['joyful', 'excited']: 
                final_pattern = 'excited'
                intensity = max(intensity, 1.1) # 興奮情緒也增加一點強度
            elif 'low_pitch' in matched_patterns or ai_emotion in ['sad', 'worried']:
                final_pattern = 'serious'
                intensity = max(0.8, intensity * 0.9) # 悲傷/擔憂情緒稍微降低強度

            # 內容主題相關模式
            elif 'tech' in matched_patterns: final_pattern = 'tech'
            elif 'space' in matched_patterns: final_pattern = 'space'

            # 如果 AI 情緒強烈但無匹配模式，也賦予一個基礎模式
            elif ai_emotion in ['joyful', 'excited'] and final_pattern == 'neutral': 
                final_pattern = 'excited'
                intensity = max(intensity, 1.1)
            elif ai_emotion in ['sad', 'worried', 'angry'] and final_pattern == 'neutral': 
                final_pattern = 'serious'
                intensity = max(0.8, intensity * 0.9)
            
            profile['pattern'] = final_pattern
            profile['intensity'] = intensity # 將計算出的強度存入 profile
            logger.info(f"【音效節點】最終模式選擇: {final_pattern}, 強度: {intensity:.2f}")

            # --- 舊的模式調整邏輯 (保留部分影響基礎參數) ---
            # 根據匹配的模式調整音效特徵
            if 'high_pitch' in matched_patterns:
                profile['base_frequency'] = 520  # 較高的基礎頻率
                profile['volume'] = 0.6
                # logger.debug("【音效節點】應用高音調基礎參數") # 日誌已在上面記錄最終模式
                
            if 'low_pitch' in matched_patterns:
                profile['base_frequency'] = 380  # 較低的基礎頻率
                profile['duration'] = 0.15 # 這個 duration 可能會被 intensity 覆蓋
                # logger.debug("【音效節點】應用低音調基礎參數")
                
            # 根據最終模式微調基礎參數 (可選, 但要小心不要覆蓋 intensity 的效果)
            if final_pattern == 'question': profile['base_frequency'] = 460
            elif final_pattern == 'thinking': profile['volume'] = min(profile['volume'], 0.4) # 思考音量通常較低
            elif final_pattern == 'important': profile['volume'] = max(profile['volume'], 0.7) # 重要音量通常較高
            elif final_pattern == 'tech': profile['base_frequency'] = 480
            elif final_pattern == 'space': profile['base_frequency'] = 420; profile['wave_type'] = 'sine'
            
            # 計算文本長度，調整持續時間
            text_length = len(text)
            if text_length > 100:
                # profile['duration'] = 0.3 # 不再直接修改 duration，讓 intensity 控制
                profile['complexity'] = max(profile['complexity'], 2) # 長文本增加複雜度
                logger.debug(f"【音效節點】文本較長({text_length}字)，增加複雜度") # 修改日誌消息
            
            logger.info(f"【音效節點】最終音效配置: pattern={profile['pattern']}, freq={profile['base_frequency']}, vol={profile['volume']:.2f}, complex={profile['complexity']}, intensity={profile['intensity']:.2f}")
            return profile
            
        except Exception as e:
            logger.error(f"【音效節點】分析文本特徵出錯: {str(e)}")
            logger.error(f"【音效節點】錯誤堆疊: {traceback.format_exc()}")
            # 返回默認配置
            return profile
    
    def _generate_tone_sound_effect(self, sound_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        根據音效特徵生成Tone.js音效命令
        
        Args:
            sound_profile: 音效特徵配置
            
        Returns:
            格式化的Tone.js音效命令
        """
        pattern = sound_profile['pattern']
        base_frequency = sound_profile['base_frequency']
        volume = sound_profile['volume']
        complexity = sound_profile['complexity']
        
        intensity = sound_profile.get('intensity', 1.0) # 獲取強度
        
        logger.info(f"【音效節點】使用SoundEffectService.create_tone_sequence生成音效: pattern={pattern}, complexity={complexity}, intensity={intensity:.2f}")
        
        # 使用SoundEffectService的create_tone_sequence方法
        try:
            result = SoundEffectService.create_tone_sequence(
                base_frequency=base_frequency,
                pattern=pattern,
                volume=volume,
                complexity=complexity,
                intensity=intensity # 傳遞強度參數
            )
            logger.info("【音效節點】SoundEffectService.create_tone_sequence成功返回結果")
            
            # 輸出生成的命令結構
            import json
            if result and isinstance(result, dict):
                logger.info(f"【音效節點】返回的命令結構: {json.dumps(result, indent=2)[:200]}...")
            
            return result
        except Exception as e:
            logger.error(f"【音效節點】調用SoundEffectService.create_tone_sequence時出錯: {str(e)}")
            logger.error(f"【音效節點】錯誤堆疊: {traceback.format_exc()}")
            raise
    
    # 以下是各種音效序列生成方法 - 如果使用create_tone_sequence，這些方法可能不會被使用
    
    def _generate_neutral_sequence(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """生成中性音效序列"""
        logger.debug("【音效節點】生成中性音效序列")
        effects = [
            {
                "type": "beep",
                "options": {
                    "frequency": profile['base_frequency'],
                    "duration": profile['duration'],
                    "volume": profile['volume'],
                    "wavetype": profile['wave_type']
                },
                "startTime": 0
            }
        ]
        
        # 根據句子數量添加額外音效
        for i, sentence in enumerate(profile['sentences'][:3]):  # 最多處理前3個句子
            if i > 0:  # 跳過第一個句子，因為已經有基礎音效
                effects.append({
                    "type": "beep",
                    "options": {
                        "frequency": profile['base_frequency'] * (1 + i * 0.1),  # 逐漸提高頻率
                        "duration": profile['duration'],
                        "volume": max(0.1, profile['volume'] - i * 0.1),  # 逐漸降低音量
                        "wavetype": profile['wave_type']
                    },
                    "startTime": i * 300  # 每300毫秒一個音符
                })
        
        return self.sound_effect_service.create_synth_sound_command(effects)
    
    def _generate_excited_sequence(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """生成興奮的音效序列"""
        effects = [
            {
                "type": "beep",
                "options": {
                    "frequency": profile['base_frequency'],
                    "duration": 0.08,
                    "volume": 0.7,
                    "wavetype": "triangle"
                },
                "startTime": 0
            },
            {
                "type": "beep",
                "options": {
                    "frequency": profile['base_frequency'] * 1.5,
                    "duration": 0.1,
                    "volume": 0.8,
                    "wavetype": "triangle"
                },
                "startTime": 100
            },
            {
                "type": "beep",
                "options": {
                    "frequency": profile['base_frequency'] * 2,
                    "duration": 0.15,
                    "volume": 0.7,
                    "wavetype": "triangle"
                },
                "startTime": 200
            }
        ]
        
        return self.sound_effect_service.create_synth_sound_command(effects)
    
    def _generate_serious_sequence(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """生成嚴肅的音效序列"""
        effects = [
            {
                "type": "beep",
                "options": {
                    "frequency": profile['base_frequency'],
                    "duration": 0.2,
                    "volume": 0.6,
                    "wavetype": "sine"
                },
                "startTime": 0
            },
            {
                "type": "beep",
                "options": {
                    "frequency": profile['base_frequency'] * 0.8,
                    "duration": 0.3,
                    "volume": 0.5,
                    "wavetype": "sine"
                },
                "startTime": 250
            }
        ]
        
        return self.sound_effect_service.create_synth_sound_command(effects)
    
    def _generate_question_sequence(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """生成問題音效序列"""
        effects = [
            {
                "type": "beep",
                "options": {
                    "frequency": profile['base_frequency'],
                    "duration": 0.1,
                    "volume": 0.5,
                    "wavetype": "sine"
                },
                "startTime": 0
            },
            {
                "type": "beep",
                "options": {
                    "frequency": profile['base_frequency'] * 1.2,
                    "duration": 0.2,
                    "volume": 0.6,
                    "wavetype": "sine"
                },
                "startTime": 150
            }
        ]
        
        return self.sound_effect_service.create_synth_sound_command(effects)
    
    def _generate_thinking_sequence(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """生成思考音效序列"""
        effects = [
            {
                "type": "beep",
                "options": {
                    "frequency": profile['base_frequency'],
                    "duration": 0.1,
                    "volume": 0.4,
                    "wavetype": "sine"
                },
                "startTime": 0
            },
            {
                "type": "beep",
                "options": {
                    "frequency": profile['base_frequency'] * 1.1,
                    "duration": 0.1,
                    "volume": 0.4,
                    "wavetype": "sine"
                },
                "startTime": 400
            },
            {
                "type": "beep",
                "options": {
                    "frequency": profile['base_frequency'] * 1.2,
                    "duration": 0.1,
                    "volume": 0.4,
                    "wavetype": "sine"
                },
                "startTime": 800
            }
        ]
        
        return self.sound_effect_service.create_synth_sound_command(effects)
    
    def _generate_success_sequence(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """生成成功音效序列"""
        effects = [
            {
                "type": "beep",
                "options": {
                    "frequency": profile['base_frequency'],
                    "duration": 0.1,
                    "volume": 0.6,
                    "wavetype": "triangle"
                },
                "startTime": 0
            },
            {
                "type": "beep",
                "options": {
                    "frequency": profile['base_frequency'] * 1.25,
                    "duration": 0.1,
                    "volume": 0.6,
                    "wavetype": "triangle"
                },
                "startTime": 100
            },
            {
                "type": "beep",
                "options": {
                    "frequency": profile['base_frequency'] * 1.5,
                    "duration": 0.2,
                    "volume": 0.7,
                    "wavetype": "triangle"
                },
                "startTime": 200
            }
        ]
        
        return self.sound_effect_service.create_synth_sound_command(effects)
    
    def _generate_important_sequence(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """生成重要信息音效序列"""
        effects = [
            {
                "type": "beep",
                "options": {
                    "frequency": profile['base_frequency'],
                    "duration": 0.15,
                    "volume": 0.7,
                    "wavetype": "sawtooth"
                },
                "startTime": 0
            },
            {
                "type": "beep",
                "options": {
                    "frequency": profile['base_frequency'],
                    "duration": 0.15,
                    "volume": 0.7,
                    "wavetype": "sawtooth"
                },
                "startTime": 200
            }
        ]
        
        return self.sound_effect_service.create_synth_sound_command(effects)
    
    def _generate_tech_sequence(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """生成科技相關音效序列"""
        effects = [
            {
                "type": "beep",
                "options": {
                    "frequency": profile['base_frequency'],
                    "duration": 0.05,
                    "volume": 0.5,
                    "wavetype": "square"
                },
                "startTime": 0
            },
            {
                "type": "beep",
                "options": {
                    "frequency": profile['base_frequency'] * 2,
                    "duration": 0.03,
                    "volume": 0.4,
                    "wavetype": "square"
                },
                "startTime": 60
            },
            {
                "type": "beep",
                "options": {
                    "frequency": profile['base_frequency'] * 1.5,
                    "duration": 0.04,
                    "volume": 0.5,
                    "wavetype": "square"
                },
                "startTime": 120
            },
            {
                "type": "noise",
                "options": {
                    "noiseType": "white",
                    "volume": 0.1,
                    "duration": 0.1,
                    "filter": {
                        "type": "highpass",
                        "frequency": 3000,
                        "Q": 1
                    }
                },
                "startTime": 180
            }
        ]
        
        return self.sound_effect_service.create_synth_sound_command(effects)
    
    def _generate_space_sequence(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """生成太空相關音效序列"""
        effects = [
            {
                "type": "noise",
                "options": {
                    "noiseType": "pink",
                    "volume": 0.15,
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
                    "frequency": profile['base_frequency'],
                    "duration": 0.2,
                    "volume": 0.4,
                    "wavetype": "sine"
                },
                "startTime": 100
            },
            {
                "type": "beep",
                "options": {
                    "frequency": profile['base_frequency'] * 1.5,
                    "duration": 0.1,
                    "volume": 0.3,
                    "wavetype": "sine"
                },
                "startTime": 300
            }
        ]
        
        return self.sound_effect_service.create_synth_sound_command(effects) 
