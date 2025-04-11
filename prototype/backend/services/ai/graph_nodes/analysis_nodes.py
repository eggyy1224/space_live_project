import time
from typing import Any, Dict, List, Optional

from loguru import logger
from services.ai.llm_client import create_llm_client


# 根據初步回應和對話歷史分析關鍵影格
async def analyze_keyframes(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes the initial response and dialogue history to identify keyframes
    for adding expressions, actions, or special tones.
    """
    start_time = time.perf_counter()
    logger.info("分析關鍵影格...")

    initial_response = state.get("initial_response", "")
    chat_history = state.get("chat_history", [])

    # 使用較輕量級的模型進行分析
    # client = create_llm_client(model_name="gemini-1.5-pro") # 原本使用的主模型
    client = create_llm_client(model_name="gemini-2.0-flash-lite") # 改用 flash-lite

    prompt = f"""
    分析以下對話歷史和初步回應，識別出適合添加角色表情、動作或特殊語氣的關鍵影格。
    請專注於尋找能夠增強表達效果的時刻。

    對話歷史:
    {chat_history}

    初步回應:
    {initial_response}

    請以 JSON 格式返回關鍵影格列表，每個關鍵影格包含：
    - "target_text": 初步回應中需要應用效果的具體文字片段。
    - "expression": 建議的表情 (例如：思考、微笑、驚訝)。
    - "action": 建議的動作 (例如：點頭、揮手、指著)。
    - "tone": 建議的語氣 (例如：興奮、嚴肅、疑問)。
    如果沒有合適的關鍵影格，請返回空列表 []。

    範例輸出:
    [
      {{
        "target_text": "真的嗎？",
        "expression": "驚訝",
        "action": null,
        "tone": "疑問"
      }},
      {{
        "target_text": "太棒了！",
        "expression": "微笑",
        "action": "拍手",
        "tone": "興奮"
      }}
    ]
    """

    keyframes = []
    try:
        response = await client.generate_text(prompt)
        logger.debug(f"關鍵影格分析 LLM 回應: {response}")
        # TODO: 更穩健地解析 JSON，處理潛在的格式錯誤
        import json
        keyframes = json.loads(response)
        if not isinstance(keyframes, list):
            logger.warning(f"關鍵影格分析未返回列表，而是：{type(keyframes)}")
            keyframes = []

    except Exception as e:
        logger.error(f"分析關鍵影格時發生錯誤: {e}")
        keyframes = [] # 發生錯誤時返回空列表

    finally:
        end_time = time.perf_counter()
        duration = end_time - start_time
        logger.info(f"分析關鍵影格完成，耗時: {duration:.2f}秒")
        state["perf_metrics"] = state.get("perf_metrics", {}) # 初始化 perf_metrics
        state["perf_metrics"]["analyze_keyframes"] = duration * 1000 # ms

    return {**state, "keyframes": keyframes} 