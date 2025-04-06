from fastapi import APIRouter, HTTPException
from utils.constants import PRESET_EXPRESSIONS

router = APIRouter()

@router.get("/presets")
async def get_all_presets():
    """
    獲取所有預設表情列表
    """
    presets = list(PRESET_EXPRESSIONS.keys())
    return {"presets": presets}

@router.get("/preset-expressions/{expression}")
async def get_preset_expression(expression: str):
    """
    獲取預設表情配置
    """
    if expression in PRESET_EXPRESSIONS:
        # 返回表情字典並包裝為morphTargets結構
        return {"morphTargets": PRESET_EXPRESSIONS[expression]}
    
    # 表情不存在，返回404錯誤
    raise HTTPException(
        status_code=404, 
        detail=f"找不到表情 '{expression}'"
    ) 