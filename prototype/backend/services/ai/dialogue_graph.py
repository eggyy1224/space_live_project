from __future__ import annotations
# --- This line must be the very first line of the file ---

"""
基於 LangGraph 的對話流程圖 - 增強版
提供更健壯的對話管理、輸入處理、與多層記憶架構
"""

import logging
import asyncio
import json
import os # 新增：導入 os 模塊
import time # <--- 導入 time 模組
from typing import Dict, List, Any, TypedDict, Optional, Tuple

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from google.generativeai.types import GenerationConfig

from langgraph.graph import StateGraph, END

from .memory_system import MemorySystem
from .prompts import DIALOGUE_STYLES, PROMPT_TEMPLATES
from .graph_nodes.input_processing import preprocess_input_node
from .graph_nodes.memory_handling import retrieve_memory_node, filter_memory_node, store_memory_node
from .graph_nodes.prompting import select_prompt_and_style_node, build_prompt_node, format_character_state
from .graph_nodes.llm_interaction import call_llm_node, handle_llm_error, post_process_node
from .graph_nodes.tool_processing import detect_tool_intent, parse_tool_parameters, execute_tool, format_tool_result_for_llm, integrate_tool_result
from .tools.web_tools import search_wikipedia
from .tools.space_tools import search_space_news
from .tools.space_tools import get_iss_info, get_moon_phase

# 配置基本日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 動態加載動畫配置 --- 
ALLOWED_ANIMATION_NAMES = []
ANIMATION_DESCRIPTIONS = {}
DEFAULT_ANIMATIONS = ["Idle"] # 最小化安全回退列表

try:
    # 計算共享配置文件的絕對路徑 (假設 dialogue_graph.py 在 services/ai/ 下)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 根據你的項目結構調整路徑層級: 從 services/ai/ 到 prototype/shared/config/
    shared_config_path = os.path.abspath(os.path.join(current_dir, '../../../shared/config/animations.json'))

    logging.info(f"嘗試從以下路徑加載動畫配置: {shared_config_path}")

    if os.path.exists(shared_config_path):
        with open(shared_config_path, 'r', encoding='utf-8') as f:
            animations_config = json.load(f)
        ALLOWED_ANIMATION_NAMES = list(animations_config.keys())
        # 加載描述，提供默認值
        ANIMATION_DESCRIPTIONS = {name: data.get('description', f'Animation: {name}')
                                  for name, data in animations_config.items()}
        logging.info(f"✅ 成功從 JSON 加載動畫配置。名稱: {ALLOWED_ANIMATION_NAMES}")

        # 確保列表非空且包含 Idle (如果原始文件有)
        if not ALLOWED_ANIMATION_NAMES:
             logging.warning("警告：加載的動畫列表為空！回退到默認值。")
             ALLOWED_ANIMATION_NAMES = DEFAULT_ANIMATIONS
             ANIMATION_DESCRIPTIONS["Idle"] = "Default Idle animation" # 確保描述也回退
        elif "Idle" not in ALLOWED_ANIMATION_NAMES:
             logging.warning("警告：加載的動畫名稱中不包含 'Idle'。回退到默認值。")
             # 如果 Idle 不存在，可能整個配置都有問題，回退到僅含 Idle 更安全
             ALLOWED_ANIMATION_NAMES = DEFAULT_ANIMATIONS
             ANIMATION_DESCRIPTIONS = {"Idle": "Default Idle animation"}

    else:
        logging.warning(f"❌ 動畫配置文件未找到: {shared_config_path}。使用默認回退值: {DEFAULT_ANIMATIONS}")
        ALLOWED_ANIMATION_NAMES = DEFAULT_ANIMATIONS
        ANIMATION_DESCRIPTIONS["Idle"] = "Default Idle animation"

except Exception as e:
    logging.error(f"❌ 加載動畫配置文件時出錯: {e}。使用默認回退值: {DEFAULT_ANIMATIONS}", exc_info=True)
    ALLOWED_ANIMATION_NAMES = DEFAULT_ANIMATIONS
    ANIMATION_DESCRIPTIONS["Idle"] = "Default Idle animation"
# --- 動態加載結束 ---

# --- Keyframe 相關定義 ---

# 允許的情緒標籤列表 (與前端 emotionMappings.ts 同步)
ALLOWED_EMOTION_TAGS = [
    "neutral", "listening", "thinking", "happy", "joyful", "content", "amused", 
    "excited", "interested", "affectionate", "proud", "relieved", "grateful", 
    "hopeful", "serene", "playful", "triumphant", "sad", "gloomy", "disappointed", 
    "worried", "angry", "irritated", "frustrated", "fearful", "nervous", 
    "disgusted", "contemptuous", "pain", "embarrassed", "jealous", "regretful", 
    "guilty", "ashamed", "despairing", "spiteful", "surprised", "confused", 
    "skeptical", "bored", "sleepy", "scheming", "determined", "impatient", 
    "shy", "bashful", "smug", "awe", "doubtful"
]

# 移除舊的硬編碼列表
# ALLOWED_ANIMATION_NAMES = ["Idle", "SwingToLand", "SneakWalk"]

# 默認動畫序列 (仍然使用 "Idle")
DEFAULT_ANIMATION_SEQUENCE = [
    {"name": "Idle", "proportion": 0.0},
    {"name": "Idle", "proportion": 1.0}
]

# 用於第二次 LLM 調用的 JSON Schema (期望 LLM 只返回 keyframes 列表)
keyframes_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "tag": {
                "type": "string",
                "enum": ALLOWED_EMOTION_TAGS, # 限制標籤
                "description": "預定義的情緒標籤"
            },
            "proportion": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "情緒發生的相對時間比例 (0.0 到 1.0)"
            }
        },
        "required": ["tag", "proportion"]
    }
}

# 身體動畫序列的 JSON Schema (使用動態加載的名稱)
animation_sequence_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "enum": ALLOWED_ANIMATION_NAMES, # 使用動態加載的列表
                "description": "預設動作名稱"
            },
            "proportion": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "動作發生的相對時間比例 (0.0 到 1.0)"
            }
        },
        "required": ["name", "proportion"]
    }
}

# 默認的中性關鍵幀 (用於回退)
DEFAULT_NEUTRAL_KEYFRAMES = [{"tag": "neutral", "proportion": 0.0}, {"tag": "neutral", "proportion": 1.0}]

def validate_and_fix_keyframes(raw_keyframes: Optional[List[Dict]]) -> List[Dict]:
    """
    驗證、排序並修正從 LLM 獲取的 keyframes 列表。
    確保格式正確、標籤有效、比例在範圍內，並包含首尾幀。
    如果驗證失敗，返回默認的中性關鍵幀。
    """
    if not isinstance(raw_keyframes, list) or not raw_keyframes:
        logging.warning("收到的 keyframes 不是列表或為空，返回默認值。")
        return DEFAULT_NEUTRAL_KEYFRAMES.copy()

    valid_keyframes = []
    seen_proportions = set()

    for kf in raw_keyframes:
        if not isinstance(kf, dict):
            logging.warning(f"Keyframe 不是字典格式: {kf}，已跳過。")
            continue

        tag = kf.get("tag")
        proportion = kf.get("proportion")

        # 驗證類型和內容
        if not isinstance(tag, str) or tag not in ALLOWED_EMOTION_TAGS:
            logging.warning(f"無效或不允許的情緒標籤: {tag}，已跳過 keyframe: {kf}")
            continue
        if not isinstance(proportion, (int, float)) or not (0.0 <= proportion <= 1.0):
            logging.warning(f"無效的時間比例: {proportion}，必須在 0.0 到 1.0 之間。已跳過 keyframe: {kf}")
            continue
        
        # 避免重複的 proportion
        if proportion in seen_proportions:
            logging.warning(f"發現重複的時間比例: {proportion}，已跳過 keyframe: {kf}")
            continue
            
        valid_keyframes.append({"tag": tag, "proportion": proportion})
        seen_proportions.add(proportion)

    if not valid_keyframes:
        logging.warning("沒有有效的 keyframes 被解析，返回默認值。")
        return DEFAULT_NEUTRAL_KEYFRAMES.copy()

    # 按 proportion 排序
    valid_keyframes.sort(key=lambda x: x["proportion"])

    # 確保首幀 proportion 為 0.0
    if valid_keyframes[0]["proportion"] != 0.0:
        logging.info("Keyframes 缺少 0.0 比例的幀，自動添加 neutral 首幀。")
        # 使用第一個有效幀的 tag 或 neutral
        start_tag = valid_keyframes[0].get("tag", "neutral") 
        valid_keyframes.insert(0, {"tag": start_tag, "proportion": 0.0})


    # 確保尾幀 proportion 為 1.0
    if valid_keyframes[-1]["proportion"] < 1.0:
        logging.info("Keyframes 缺少 1.0 比例的幀，自動添加 neutral 尾幀。")
         # 使用最後一個有效幀的 tag 或 neutral
        end_tag = valid_keyframes[-1].get("tag", "neutral")
        valid_keyframes.append({"tag": end_tag, "proportion": 1.0})
    elif valid_keyframes[-1]["proportion"] > 1.0: # 理論上 schema 會限制，但做個防禦
        logging.warning("最後一個 keyframe 的 proportion 超過 1.0，強制設為 1.0。")
        valid_keyframes[-1]["proportion"] = 1.0


    logging.info(f"Keyframes 驗證和修正完成，共 {len(valid_keyframes)} 幀。")
    return valid_keyframes

# 添加動畫序列驗證函數 (檢查名稱是否在動態列表中)
def validate_and_fix_animation_sequence(raw_sequence: Optional[List[Dict]]) -> List[Dict]:
    """
    驗證、排序並修正從 LLM 獲取的身體動畫序列。
    確保格式正確、名稱有效、比例在範圍內，並包含首尾幀。
    同時確保至少有兩個不同的動作。
    """
    # 使用全局的 ALLOWED_ANIMATION_NAMES
    global ALLOWED_ANIMATION_NAMES, DEFAULT_ANIMATION_SEQUENCE

    if not isinstance(raw_sequence, list) or not raw_sequence:
        logging.warning("收到的動畫序列不是列表或為空，返回默認值。")
        return DEFAULT_ANIMATION_SEQUENCE.copy()

    valid_sequence = []
    seen_proportions = set()

    for anim in raw_sequence:
        if not isinstance(anim, dict):
            logging.warning(f"動畫關鍵幀不是字典格式: {anim}，已跳過。")
            continue

        name = anim.get("name")
        proportion = anim.get("proportion")

        # 驗證類型和內容 (使用動態加載的 ALLOWED_ANIMATION_NAMES)
        if not isinstance(name, str) or name not in ALLOWED_ANIMATION_NAMES:
            # 如果名稱無效，嘗試回退到 Idle，如果 Idle 可用
            if "Idle" in ALLOWED_ANIMATION_NAMES:
                 logging.warning(f"無效或不允許的動作名稱: {name}。嘗試回退到 'Idle'。原始關鍵幀: {anim}")
                 name = "Idle"
            else:
                 logging.warning(f"無效或不允許的動作名稱: {name}，且 'Idle' 不可用。已跳過動畫關鍵幀: {anim}")
                 continue # 跳過這個無效的幀
        
        if not isinstance(proportion, (int, float)) or not (0.0 <= proportion <= 1.0):
            logging.warning(f"無效的時間比例: {proportion}，必須在 0.0 到 1.0 之間。已跳過動畫關鍵幀: {anim}")
            continue
        
        # 避免重複的 proportion
        if proportion in seen_proportions:
            logging.warning(f"發現重複的時間比例: {proportion}，已跳過動畫關鍵幀: {anim}")
            continue
            
        valid_sequence.append({"name": name, "proportion": proportion})
        seen_proportions.add(proportion)

    if not valid_sequence:
        logging.warning("沒有有效的動畫關鍵幀被解析，返回默認值。")
        return DEFAULT_ANIMATION_SEQUENCE.copy()

    # 按 proportion 排序
    valid_sequence.sort(key=lambda x: x["proportion"])

    # 確保首幀 proportion 為 0.0 (優先使用 Idle)
    idle_name = "Idle" if "Idle" in ALLOWED_ANIMATION_NAMES else (ALLOWED_ANIMATION_NAMES[0] if ALLOWED_ANIMATION_NAMES else None)
    if not idle_name:
        logging.error("無法確定用於填充首尾幀的動畫名稱！")
        return DEFAULT_ANIMATION_SEQUENCE.copy() # 或者拋出錯誤
        
    if valid_sequence[0]["proportion"] != 0.0:
        logging.info(f"動畫序列缺少 0.0 比例的幀，自動添加 {idle_name} 首幀。")
        valid_sequence.insert(0, {"name": idle_name, "proportion": 0.0})

    # 確保尾幀 proportion 為 1.0 (優先使用 Idle)
    if valid_sequence[-1]["proportion"] < 1.0:
        logging.info(f"動畫序列缺少 1.0 比例的幀，自動添加 {idle_name} 尾幀。")
        # 如果最後一幀是 Idle，可以稍微智能一點，避免連續兩個 Idle
        last_valid_name = valid_sequence[-1]["name"]
        name_to_append = idle_name if last_valid_name != idle_name else last_valid_name
        valid_sequence.append({"name": name_to_append, "proportion": 1.0})
    elif valid_sequence[-1]["proportion"] > 1.0:
        logging.warning("最後一個動畫關鍵幀的 proportion 超過 1.0，強制設為 1.0。")
        valid_sequence[-1]["proportion"] = 1.0

    # 檢查是否至少有兩個不同的動作
    unique_animations = set(frame["name"] for frame in valid_sequence)
    
    if len(unique_animations) < 2:
        logging.info("動畫序列只包含一種動作，添加另一種動作...")
        
        # 獲取當前唯一的動作名稱
        current_animation = next(iter(unique_animations))
        
        # 從允許的動畫中選擇一個不同的動作
        alternative_animations = [name for name in ALLOWED_ANIMATION_NAMES if name != current_animation]
        
        if alternative_animations:
            # 選擇第一個可用的替代動畫
            alt_animation = alternative_animations[0]
            
            # 中間位置 (proportion = 0.5)
            valid_sequence.append({"name": alt_animation, "proportion": 0.5})
            
            # 重新排序
            valid_sequence.sort(key=lambda x: x["proportion"])
            
            logging.info(f"已添加 {alt_animation} 作為中間動畫幀，確保至少有兩種不同動作")
        else:
            logging.warning("沒有可用的替代動畫名稱，無法添加第二種動作")

    logging.info(f"動畫序列驗證和修正完成，共 {len(valid_sequence)} 幀，包含 {len(set(frame['name'] for frame in valid_sequence))} 種不同動作。")
    return valid_sequence


# --- 重新添加/確保 Keyframe 分析節點定義在頂層 ---

async def analyze_keyframes_node(state: DialogueState) -> Dict[str, Any]:
    """
    分析 LLM 生成的純文本回應，調用第二次 LLM (使用 JSON 模式) 來提取情緒關鍵幀和身體動畫序列。
    """
    # 使用全局的 ALLOWED_ANIMATION_NAMES 和 ANIMATION_DESCRIPTIONS
    global ALLOWED_ANIMATION_NAMES, ANIMATION_DESCRIPTIONS, keyframes_schema, animation_sequence_schema
    
    llm_response_raw = state.get("llm_response_raw", "")
    llm = state.get("_context", {}).get("llm")

    if not llm_response_raw:
        logging.warning("analyze_keyframes_node: 原始回應為空，無法分析 keyframes。返回默認值。")
        return {
            "emotional_keyframes": DEFAULT_NEUTRAL_KEYFRAMES.copy(),
            "body_animation_sequence": DEFAULT_ANIMATION_SEQUENCE.copy()
        }
    if not llm:
        logging.error("analyze_keyframes_node: LLM 實例未在上下文中提供。返回默認值。")
        return {
            "emotional_keyframes": DEFAULT_NEUTRAL_KEYFRAMES.copy(),
            "body_animation_sequence": DEFAULT_ANIMATION_SEQUENCE.copy()
        }

    # 使用動態加載的動畫名稱和描述更新 Prompt
    available_actions_desc = ', '.join([f"{name}({ANIMATION_DESCRIPTIONS.get(name, '')})" 
                                        for name in ALLOWED_ANIMATION_NAMES])

    analysis_prompt = f"""
請分析以下這段文本，同時完成兩個任務：

1. 識別文本中表達的情感變化，並生成情緒關鍵幀列表 (emotional_keyframes)。
每個情緒關鍵幀包含 'tag' (情緒標籤) 和 'proportion' (相對時間比例 0.0 到 1.0)。
允許的情緒標籤為: {', '.join(ALLOWED_EMOTION_TAGS)}。

2. 選擇適合文本內容的身體動畫序列 (body_animation_sequence)。
每個動畫關鍵幀包含 'name' (動作名稱) 和 'proportion' (相對時間比例 0.0 到 1.0)。
可用的動作僅限於 (名稱(描述)): {available_actions_desc}。

選擇動畫時，請考慮：
- 文本的語義內容和表達的活動
- 情緒變化與身體動作的協調
- 自然的過渡順序
- 必須使用至少兩種不同的動作 (非常重要)
- 為不同的情緒變化選擇不同的動畫類型

文本內容：
"{llm_response_raw}"

請嚴格按照以下 JSON 格式輸出結果：
{{
  "emotional_keyframes": [...情緒關鍵幀陣列...],
  "body_animation_sequence": [...身體動畫序列陣列...]
}}

情緒關鍵幀格式：{json.dumps(keyframes_schema, indent=2)}
身體動畫序列格式：{json.dumps(animation_sequence_schema, indent=2)}

確保：
1. 兩個序列的第一個關鍵幀 proportion 都為 0.0
2. 動畫選擇符合文本的內容邏輯，且名稱在可用動作列表中。
3. 結果僅包含指定的 JSON 格式
4. body_animation_sequence 必須包含至少兩種不同的動作名稱 (強制要求)
"""

    generation_config = GenerationConfig(
        response_mime_type='application/json',
    )

    try:
        logging.info("analyze_keyframes_node: 開始調用 LLM 進行情緒關鍵幀和動畫序列分析...")
        analysis_response = await llm.ainvoke(
            analysis_prompt,
            config={"generation_config": generation_config}
        )

        raw_analysis_data = analysis_response.content
        parsed_data = None

        if isinstance(raw_analysis_data, str):
            # --- 新增：清理 Markdown 標記 ---
            cleaned_data = raw_analysis_data.strip()
            if cleaned_data.startswith("```json"):
                cleaned_data = cleaned_data[7:] # 移除 ```json
            if cleaned_data.endswith("```"):
                cleaned_data = cleaned_data[:-3] # 移除 ```
            cleaned_data = cleaned_data.strip() # 再次去除可能的空白
            # --- 清理結束 ---
            try:
                # 使用清理後的數據進行解析
                parsed_data = json.loads(cleaned_data) 
                logging.info(f"analyze_keyframes_node: LLM 返回 JSON 字符串，已成功解析。")
            except json.JSONDecodeError as e:
                # 記錄原始數據和清理後的數據以供調試
                logging.error(f"analyze_keyframes_node: 無法解析 LLM 返回的 JSON 字符串: {e}\n原始字符串: '{raw_analysis_data}'\n清理後: '{cleaned_data}'")
        elif isinstance(raw_analysis_data, dict):
            parsed_data = raw_analysis_data
            logging.info(f"analyze_keyframes_node: LLM 直接返回字典對象。")
        else:
            logging.error(f"analyze_keyframes_node: LLM 返回了非預期類型: {type(raw_analysis_data)}")
        
        # 提取並驗證數據
        result = {}
        
        # 提取情緒關鍵幀
        if parsed_data and "emotional_keyframes" in parsed_data:
            raw_keyframes = parsed_data["emotional_keyframes"]
            validated_keyframes = validate_and_fix_keyframes(raw_keyframes)
            result["emotional_keyframes"] = validated_keyframes
            logging.info(f"提取到有效的情緒關鍵幀：{len(validated_keyframes)} 幀")
        else:
            logging.warning("未找到有效的 emotional_keyframes，使用默認值")
            result["emotional_keyframes"] = DEFAULT_NEUTRAL_KEYFRAMES.copy()
            
        # 提取身體動畫序列
        if parsed_data and "body_animation_sequence" in parsed_data:
            raw_animation_sequence = parsed_data["body_animation_sequence"]
            validated_animation_sequence = validate_and_fix_animation_sequence(raw_animation_sequence)
            result["body_animation_sequence"] = validated_animation_sequence
            logging.info(f"提取到有效的身體動畫序列：{len(validated_animation_sequence)} 幀")
        else:
            logging.warning("未找到有效的 body_animation_sequence，使用默認值")
            result["body_animation_sequence"] = DEFAULT_ANIMATION_SEQUENCE.copy()
            
        return result
        
    except Exception as e:
        logging.error(f"analyze_keyframes_node 發生錯誤: {e}", exc_info=True)
        return {
            "emotional_keyframes": DEFAULT_NEUTRAL_KEYFRAMES.copy(),
            "body_animation_sequence": DEFAULT_ANIMATION_SEQUENCE.copy()
        }

# --- 添加結束 ---

# 定義對話圖的狀態結構
class DialogueState(TypedDict):
    # --- 輸入與上下文 ---
    raw_user_input: str           # 原始用戶輸入
    processed_user_input: str     # 經過初步處理/淨化的用戶輸入
    input_classification: Dict[str, Any]  # 輸入分類結果 (e.g., {'type': 'normal'/'repetitive'/'gibberish'/'question', 'sentiment': 'positive'})
    messages: List[BaseMessage]   # 完整對話歷史
    
    # --- 記憶 ---
    retrieved_memories: List[Any] # 原始檢索到的記憶
    filtered_memories: str        # 經過篩選和格式化的記憶 (用於提示)
    persona_info: str             # 檢索到的角色資訊
    
    # --- 意圖與任務 ---
    current_intent: Optional[str] # 識別出的使用者意圖
    current_task: Optional[str]   # 當前任務 (若有)
    tasks_history: List[Dict]     # 任務歷史
    
    # --- 工具呼叫 ---
    has_tool_intent: Optional[bool]         # 是否需要使用工具
    potential_tool: Optional[str]           # 可能要使用的工具
    tool_confidence: Optional[float]        # 工具意圖識別的信心度
    tool_parameters: Optional[Dict[str, Any]]  # 工具參數
    tool_execution_result: Optional[str]    # 工具執行結果
    tool_execution_status: Optional[str]    # 工具執行狀態
    tool_used: Optional[str]                # 實際使用的工具
    formatted_tool_result: Optional[str]    # 格式化後的工具結果 (中間步驟)
    tool_result: Optional[str]              # 最終給模板使用的工具結果
    tool_error: Optional[str]               # 最終給模板使用的工具錯誤
    
    # --- 生成控制 ---
    prompt_template_key: str      # 選用的提示模板名稱 (e.g., 'standard', 'clarification', 'error')
    prompt_inputs: Dict[str, Any] # 最終構建的提示輸入
    dialogue_style: str           # 選定的對話風格
    character_state_prompt: str   # 格式化的角色狀態
    
    # --- 角色狀態 ---
    character_state: Dict[str, Any] # 角色狀態
    
    # --- 回應與狀態 ---
    llm_response_raw: str         # LLM原始回應 (純文本)
    emotional_keyframes: Optional[List[Dict]] = None # 用於存儲分析出的情緒關鍵幀
    body_animation_sequence: Optional[List[Dict]] = None # 新增：用於存儲分析出的身體動畫序列
    final_response: str           # 最終處理後的回應
    error_count: int              # 連續錯誤計數
    system_alert: Optional[str]   # 系統內部的警告或標註 (e.g., 'high_repetition_detected')
    should_store_memory: bool     # 是否應該儲存這輪對話到長期記憶
    
    # --- 上下文與依賴 ---
    _context: Dict[str, Any]      # 儲存上下文依賴 (memory_system, llm 等)

class DialogueGraph:
    """基於 LangGraph 的對話圖 - 實現更複雜的有狀態對話流程"""
    
    def __init__(self, memory_system: MemorySystem, llm: ChatGoogleGenerativeAI, persona_name: str = "星際小可愛"):
        self.memory_system = memory_system
        self.llm = llm
        self.persona_name = persona_name
        
        # 保存初始角色狀態
        self.initial_character_state = {
            "health": 100,
            "mood": 70,
            "energy": 80,
            "task_success": 0,
            "days_in_space": 1
        }
        
        # 初始化提示模板
        self.prompt_templates = {
            key: PromptTemplate(
                template=template,
                input_variables=[
                    "conversation_history", "filtered_memories", "persona_info",
                    "user_message", "character_state", "current_task",
                    "dialogue_style", "persona_name", "tool_result", "tool_error"
                ] if "tool" in key else [
                    "conversation_history", "filtered_memories", "persona_info",
                    "user_message", "character_state", "current_task",
                    "dialogue_style", "persona_name"
                ]
            ) for key, template in PROMPT_TEMPLATES.items()
        }
        
        # 註冊可用的工具
        self.available_tools = {
            "search_wikipedia": {
                "function": search_wikipedia,
                "description": "當用戶詢問關於特定人物、地點、事件或概念的定義或一般知識時，使用此工具從維基百科查找信息。",
                "parameters": [
                    {"name": "query", "type": "string", "description": "要查詢的主題或關鍵字"}
                ]
            },
            "search_space_news": {
                "function": search_space_news,
                "description": "獲取太空探索、天文發現或航天工業相關的新聞標題和摘要，支持關鍵字搜索和時間範圍篩選（包括特定年份如'2020年'）。",
                "parameters": [
                    {"name": "keywords", "type": "string", "description": "要搜索的關鍵詞或主題，例如 'NASA', 'SpaceX', '火星'", "required": False},
                    {"name": "time_period", "type": "string", "description": "指定的時間範圍，可以是'今天'、'昨天'、'本週'、'本月'、'今年'，或特定年份如'2020年'", "required": False}
                ]
            },
            "get_iss_info": {
                "function": get_iss_info,
                "description": "查詢國際太空站 (ISS) 的即時位置（經緯度）以及當前在太空中的總人數和在 ISS 上的人數。",
                "parameters": [] # 無需參數
            },
            "get_moon_phase": {
                "function": get_moon_phase,
                "description": "查詢指定日期的月相。如果用戶沒有指定日期，則默認查詢今天。",
                "parameters": [
                    {"name": "date_str", "type": "string", "description": "要查詢的日期，格式可以是 YYYY-MM-DD，或者是 '今天'、'明天'、'昨天'。如果省略，則為今天。", "required": False}
                ]
            }
        }
        
        # 構建對話圖
        self.graph = self._build_graph()
        
        # 編譯圖
        self.app = self.graph.compile()
        
        logging.info("增強版 DialogueGraph 初始化完成，已註冊工具")
        
    def _build_graph(self) -> StateGraph:
        """構建對話圖"""
        
        # 創建狀態圖
        workflow = StateGraph(DialogueState)
        
        # 添加節點 - 輸入處理和記憶檢索
        workflow.add_node("preprocess_input", self._preprocess_input_node_wrapper)
        workflow.add_node("retrieve_memory", self._retrieve_memory_node_wrapper)
        workflow.add_node("filter_memory", filter_memory_node)
        
        # 添加節點 - 工具處理
        workflow.add_node("detect_tool_intent", self._detect_tool_intent_wrapper)
        workflow.add_node("parse_tool_parameters", self._parse_tool_parameters_wrapper)
        workflow.add_node("execute_tool", self._execute_tool_wrapper)
        workflow.add_node("format_tool_result", format_tool_result_for_llm)
        workflow.add_node("integrate_tool_result", integrate_tool_result)
        
        # 添加節點 - 提示構建和 LLM 生成
        workflow.add_node("select_prompt_and_style", select_prompt_and_style_node)
        workflow.add_node("build_prompt", self._build_prompt_node_wrapper)
        workflow.add_node("call_llm", self._call_llm_node_wrapper)
        workflow.add_node("analyze_keyframes", self._analyze_keyframes_node_wrapper)
        workflow.add_node("post_process", post_process_node)
        workflow.add_node("store_memory", self._store_memory_node_wrapper)
        
        # 定義基本流程
        workflow.set_entry_point("preprocess_input")
        workflow.add_edge("preprocess_input", "retrieve_memory")
        workflow.add_edge("retrieve_memory", "filter_memory")
        workflow.add_edge("filter_memory", "detect_tool_intent")
        
        # 分支流程 - 工具處理
        workflow.add_conditional_edges(
            "detect_tool_intent",
            lambda state: "tool_path" if state.get("has_tool_intent") else "normal_path",
            {
                "tool_path": "parse_tool_parameters",
                "normal_path": "select_prompt_and_style"
            }
        )
        
        # 工具處理流程
        workflow.add_edge("parse_tool_parameters", "execute_tool")
        workflow.add_edge("execute_tool", "format_tool_result")
        workflow.add_edge("format_tool_result", "integrate_tool_result")
        workflow.add_edge("integrate_tool_result", "select_prompt_and_style")
        
        # 正常處理流程
        workflow.add_edge("select_prompt_and_style", "build_prompt")
        workflow.add_edge("build_prompt", "call_llm")
        
        # LLM 調用後處理
        workflow.add_conditional_edges(
            "call_llm",
            handle_llm_error,
            {
                "retry": "select_prompt_and_style",
                "continue": "analyze_keyframes"
            }
        )
        
        workflow.add_edge("analyze_keyframes", "post_process")
        workflow.add_edge("post_process", "store_memory")
        workflow.add_edge("store_memory", END)
        
        return workflow
    
    # 節點包裝器 - 負責將依賴注入到節點的 state 中
    async def _preprocess_input_node_wrapper(self, state: DialogueState) -> Dict[str, Any]:
        """包裝輸入預處理節點，注入上下文"""
        start_time = time.monotonic()
        if "_context" not in state:
            state["_context"] = {}
        result_state = await preprocess_input_node(state)
        end_time = time.monotonic()
        duration = (end_time - start_time) * 1000
        logging.info(f"[Perf][DialogueGraph] Node preprocess_input duration: {duration:.2f} ms", extra={"log_category": "PERFORMANCE"})
        return result_state
    
    async def _retrieve_memory_node_wrapper(self, state: DialogueState) -> Dict[str, Any]:
        """包裝記憶檢索節點，注入記憶系統"""
        start_time = time.monotonic()
        if "_context" not in state:
            state["_context"] = {}
        state["_context"]["memory_system"] = self.memory_system
        result_state = await retrieve_memory_node(state)
        end_time = time.monotonic()
        duration = (end_time - start_time) * 1000
        logging.info(f"[Perf][DialogueGraph] Node retrieve_memory duration: {duration:.2f} ms", extra={"log_category": "PERFORMANCE"})
        return result_state
    
    async def _detect_tool_intent_wrapper(self, state: DialogueState) -> Dict[str, Any]:
        """包裝工具意圖檢測節點，注入可用工具列表"""
        start_time = time.monotonic()
        if "_context" not in state:
            state["_context"] = {}
        state["_context"]["available_tools"] = self.available_tools
        state["_context"]["llm"] = self.llm
        result_state = await detect_tool_intent(state)
        end_time = time.monotonic()
        duration = (end_time - start_time) * 1000
        logging.info(f"[Perf][DialogueGraph] Node detect_tool_intent duration: {duration:.2f} ms", extra={"log_category": "PERFORMANCE"})
        return result_state
    
    async def _parse_tool_parameters_wrapper(self, state: DialogueState) -> Dict[str, Any]:
        """包裝工具參數解析節點，注入可用工具列表"""
        start_time = time.monotonic()
        if "_context" not in state:
            state["_context"] = {}
        state["_context"]["available_tools"] = self.available_tools
        state["_context"]["llm"] = self.llm
        result_state = await parse_tool_parameters(state)
        end_time = time.monotonic()
        duration = (end_time - start_time) * 1000
        logging.info(f"[Perf][DialogueGraph] Node parse_tool_parameters duration: {duration:.2f} ms", extra={"log_category": "PERFORMANCE"})
        return result_state
    
    async def _execute_tool_wrapper(self, state: DialogueState) -> Dict[str, Any]:
        """包裝工具執行節點，注入可用工具列表"""
        start_time = time.monotonic()
        if "_context" not in state:
            state["_context"] = {}
        state["_context"]["available_tools"] = self.available_tools
        result_state = await execute_tool(state)
        end_time = time.monotonic()
        duration = (end_time - start_time) * 1000
        logging.info(f"[Perf][DialogueGraph] Node execute_tool duration: {duration:.2f} ms (Tool: {state.get('potential_tool')})", extra={"log_category": "PERFORMANCE"})
        return result_state
    
    def _build_prompt_node_wrapper(self, state: DialogueState) -> Dict[str, Any]:
        """包裝提示構建節點，注入角色名稱"""
        start_time = time.monotonic()
        if "_context" not in state:
            state["_context"] = {}
        state["_context"]["persona_name"] = self.persona_name
        result_state = build_prompt_node(state)
        end_time = time.monotonic()
        duration = (end_time - start_time) * 1000
        logging.info(f"[Perf][DialogueGraph] Node build_prompt duration: {duration:.2f} ms", extra={"log_category": "PERFORMANCE"})
        return result_state
    
    async def _call_llm_node_wrapper(self, state: DialogueState) -> Dict[str, Any]:
        """包裝 LLM 調用節點，注入 LLM 和提示模板"""
        start_time = time.monotonic()
        if "_context" not in state:
            state["_context"] = {}
        state["_context"]["llm"] = self.llm
        state["_context"]["prompt_templates"] = self.prompt_templates
        result_state = await call_llm_node(state)
        end_time = time.monotonic()
        duration = (end_time - start_time) * 1000
        logging.info(f"[Perf][DialogueGraph] Node call_llm duration: {duration:.2f} ms", extra={"log_category": "PERFORMANCE"})
        return result_state
    
    async def _analyze_keyframes_node_wrapper(self, state: DialogueState) -> Dict[str, Any]:
        """包裝 Keyframe 分析節點，注入 LLM 實例"""
        start_time = time.monotonic()
        if "_context" not in state:
            state["_context"] = {}
        if "llm" not in state["_context"]:
            state["_context"]["llm"] = self.llm
        result_state = await analyze_keyframes_node(state)
        end_time = time.monotonic()
        duration = (end_time - start_time) * 1000
        logging.info(f"[Perf][DialogueGraph] Node analyze_keyframes duration: {duration:.2f} ms", extra={"log_category": "PERFORMANCE"})
        return result_state
    
    async def _store_memory_node_wrapper(self, state: DialogueState) -> Dict[str, Any]:
        """包裝記憶儲存節點，注入記憶系統"""
        start_time = time.monotonic()
        if "_context" not in state:
            state["_context"] = {}
        state["_context"]["memory_system"] = self.memory_system
        result_state = await store_memory_node(state)
        end_time = time.monotonic()
        duration = (end_time - start_time) * 1000
        logging.info(f"[Perf][DialogueGraph] Node store_memory duration: {duration:.2f} ms", extra={"log_category": "PERFORMANCE"})
        return result_state
    
    async def generate_response(
        self,
        messages: List[BaseMessage],
        character_state: Dict[str, Any],
        user_text: Optional[str] = None,
        system_prompt: Optional[str] = None,
        current_task: Optional[str] = None,
        tasks_history: Optional[List[Dict]] = None,
        current_intent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        異步生成回應 - 調用 LangGraph 圖。
        接收 user_text 或 system_prompt 其中之一作為輸入。

        Args:
            messages: 當前的對話歷史。
            character_state: 當前的角色狀態。
            user_text: 使用者輸入文本。
            system_prompt: 系統觸發的提示 (例如用於 murmur)。
            current_task: 當前任務。
            tasks_history: 任務歷史。
            current_intent: (可選) 外部傳入的意圖。

        Returns:
            包含回應和狀態更新的字典。
        """
        if user_text is not None and system_prompt is not None:
            logging.error("DialogueGraph.generate_response 不能同時接收 user_text 和 system_prompt")
            return {
                "error": "不能同時提供 user_text 和 system_prompt",
                "final_response": "內部處理錯誤，請稍後再試。",
                "emotion": "confused",
                "emotional_keyframes": DEFAULT_NEUTRAL_KEYFRAMES.copy(),
                "body_animation_sequence": DEFAULT_ANIMATION_SEQUENCE.copy(),
                "updated_messages": messages
            }
        if user_text is None and system_prompt is None:
             logging.error("DialogueGraph.generate_response 需要提供 user_text 或 system_prompt")
             return {
                "error": "缺少 user_text 或 system_prompt",
                "final_response": "內部系統似乎沒有收到任何指令。",
                "emotion": "confused",
                "emotional_keyframes": DEFAULT_NEUTRAL_KEYFRAMES.copy(),
                "body_animation_sequence": DEFAULT_ANIMATION_SEQUENCE.copy(),
                "updated_messages": messages
             }

        start_time = time.time()
        logging.info(f"DialogueGraph: 開始處理輸入。 User Text: '{user_text}', System Prompt: '{system_prompt}'")

        graph_input_text = user_text if user_text is not None else system_prompt

        initial_state: DialogueState = {
            "raw_user_input": graph_input_text,
            "processed_user_input": "",
            "input_classification": {},
            "messages": messages,
            "retrieved_memories": [],
            "filtered_memories": "",
            "persona_info": "",
            "current_intent": current_intent,
            "current_task": current_task,
            "tasks_history": tasks_history if tasks_history is not None else [],
            "has_tool_intent": None,
            "potential_tool": None,
            "tool_confidence": None,
            "tool_parameters": None,
            "tool_execution_result": None,
            "tool_execution_status": None,
            "tool_used": None,
            "formatted_tool_result": None,
            "tool_result": None,
            "tool_error": None,
            "prompt_template_key": "standard",
            "prompt_inputs": {},
            "dialogue_style": "standard",
            "character_state_prompt": "",
            "character_state": character_state,
            "llm_response_raw": "",
            "emotional_keyframes": None,
            "body_animation_sequence": None,
            "final_response": "",
            "error_count": 0,
            "system_alert": None,
            "should_store_memory": True,
            "_context": {
                "memory_system": self.memory_system,
                "llm": self.llm,
                "persona_name": self.persona_name,
                "available_tools": self.available_tools,
                "keyframes_schema": keyframes_schema,
                "animation_sequence_schema": animation_sequence_schema,
                "dialogue_styles": DIALOGUE_STYLES,
                "prompt_templates": PROMPT_TEMPLATES
            }
        }

        try:
            final_state = await self.app.ainvoke(
                initial_state,
                config={"recursion_limit": 15}
            )

            end_time = time.time()
            processing_time = (end_time - start_time) * 1000
            logging.info(f"DialogueGraph: 處理完成。總耗時: {processing_time:.2f} ms")

            return {
                "final_response": final_state.get("final_response", "出了點問題，我不知道該說什麼。"),
                "emotion": final_state.get("character_state", {}).get("current_emotion", "neutral"),
                "emotional_keyframes": final_state.get("emotional_keyframes"),
                "body_animation_sequence": final_state.get("body_animation_sequence"),
                "updated_messages": final_state.get("messages", messages)
            }

        except Exception as e:
            end_time = time.time()
            processing_time = (end_time - start_time) * 1000
            logging.error(f"DialogueGraph: 調用圖時發生錯誤: {e}。耗時: {processing_time:.2f} ms", exc_info=True)
            return {
                "error": str(e),
                "final_response": "哎呀，處理你的請求時我的內部線路好像纏繞在一起了！",
                "emotion": "confused",
                "emotional_keyframes": DEFAULT_NEUTRAL_KEYFRAMES.copy(),
                "body_animation_sequence": DEFAULT_ANIMATION_SEQUENCE.copy(),
                "updated_messages": messages
            }

    def update_character_state(self, character_state: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        updated_state = character_state.copy()
        changed = False
        
        for key, value in updates.items():
            if key in updated_state:
                old_value = updated_state[key]
                current_value = old_value
                try:
                    if isinstance(value, str) and value.startswith(('+', '-')):
                        delta = int(value)
                        if isinstance(current_value, (int, float)):
                            current_value += delta
                        else:
                            logging.warning(f"無法對非數值狀態 '{key}' 進行增量更新: {value}")
                            continue
                    else:
                        try:
                            num_value = int(value) if isinstance(updated_state[key], int) else float(value)
                            current_value = num_value
                        except (ValueError, TypeError):
                            current_value = value
                    
                    if current_value != old_value:
                        updated_state[key] = current_value
                        changed = True
                        
                        if isinstance(current_value, (int, float)) and key in ["health", "mood", "energy"]:
                            updated_state[key] = max(0, min(100, current_value))
                        
                        logging.info(f"角色狀態更新: {key} 從 {old_value} 變為 {updated_state[key]}")
                
                except Exception as e:
                    logging.warning(f"處理狀態更新時出錯: {key}={value}, 錯誤: {e}")
        
        if changed:
            state_text = format_character_state(updated_state)
            logging.info(f"更新後角色狀態: {state_text}")
        
        return updated_state
    
    def reset(self) -> Dict[str, Any]:
        return self.initial_character_state.copy() 