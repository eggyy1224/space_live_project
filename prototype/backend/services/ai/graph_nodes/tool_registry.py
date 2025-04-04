"""
工具註冊模塊 - 管理和提供工具函數的註冊表

此模塊負責管理所有可用的工具函數，提供工具註冊、查詢和列舉功能。
充當工具函數的中央註冊處，使其他模塊能夠通過名稱查找工具。
"""

import logging
from typing import Dict, Any, List, Callable, Optional

# 配置基本日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 工具註冊表
_TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {}

def register_tool(name: str, func: Callable, description: str, parameters: List[Dict[str, Any]] = None, 
                 keywords: List[str] = None, category: str = "general") -> None:
    """
    註冊一個新工具到系統
    
    參數:
    - name: 工具的唯一名稱
    - func: 工具的實際函數
    - description: 工具的功能描述
    - parameters: 工具接受的參數列表，每個參數是一個字典
    - keywords: 與工具相關的關鍵詞，用於意圖檢測
    - category: 工具的分類
    """
    if name in _TOOL_REGISTRY:
        logging.warning(f"覆蓋已存在的工具: {name}")
    
    _TOOL_REGISTRY[name] = {
        "name": name,
        "func": func,
        "description": description,
        "parameters": parameters or [],
        "keywords": keywords or [],
        "category": category
    }
    
    logging.info(f"工具已註冊: {name} ({category})")

def get_tool_by_name(name: str) -> Optional[Callable]:
    """
    通過名稱獲取工具函數
    
    參數:
    - name: 工具的名稱
    
    返回:
    工具函數或 None（如果找不到）
    """
    tool = _TOOL_REGISTRY.get(name)
    if not tool:
        return None
    return tool["func"]

def get_available_tools(category: str = None) -> List[Dict[str, Any]]:
    """
    獲取所有可用工具的信息
    
    參數:
    - category: 可選的分類過濾
    
    返回:
    工具信息列表，每個包含名稱、描述、參數等
    """
    tools = []
    
    for name, tool_info in _TOOL_REGISTRY.items():
        # 跳過函數本身，以便可以序列化返回
        tool_data = {k: v for k, v in tool_info.items() if k != "func"}
        
        if category is None or tool_info["category"] == category:
            tools.append(tool_data)
    
    return tools

def remove_tool(name: str) -> bool:
    """
    從註冊表中移除工具
    
    參數:
    - name: 工具的名稱
    
    返回:
    是否成功移除
    """
    if name in _TOOL_REGISTRY:
        del _TOOL_REGISTRY[name]
        logging.info(f"工具已移除: {name}")
        return True
    
    logging.warning(f"嘗試移除不存在的工具: {name}")
    return False

# 註冊默認工具示例
async def _example_space_object_query(object_name: str) -> Dict[str, Any]:
    """查詢太空物體的示例實現"""
    return {
        "content": f"關於 {object_name} 的資訊: 這是一個示例回應，實際查詢將連接到天文數據API。"
    }

async def _example_scene_analysis(analysis_type: str = None) -> Dict[str, Any]:
    """場景分析的示例實現"""
    return {
        "content": f"場景分析結果 ({analysis_type or '一般'}): 這是一個示例回應，實際分析將使用電腦視覺API。"
    }

# 註冊示例工具
register_tool(
    name="space_object_query",
    func=_example_space_object_query,
    description="查詢太空中的天體、衛星或其他物體的信息",
    parameters=[
        {
            "name": "object_name",
            "type": "string",
            "description": "要查詢的太空物體名稱",
            "required": True
        }
    ],
    keywords=["太空", "天體", "衛星", "星球", "軌道", "國際空間站", "ISS"],
    category="space"
)

register_tool(
    name="scene_analysis",
    func=_example_scene_analysis,
    description="分析當前場景中的物體、環境和可能的風險",
    parameters=[
        {
            "name": "analysis_type",
            "type": "string",
            "description": "分析類型 (safety, object_detection, etc.)",
            "required": False
        }
    ],
    keywords=["分析", "辨識", "識別", "檢測", "場景", "環境", "風險"],
    category="vision"
) 