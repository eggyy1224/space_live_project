"""
記憶系統API端點
提供記憶的儲存、檢索和統計功能
"""

import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from services.memory_system import MemorySystem
from core.config import settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

# 配置日誌
logger = logging.getLogger(__name__)

# 創建路由器
router = APIRouter(prefix="/api/memory", tags=["memory"])

# 請求和回應模型
class SaveMemoryRequest(BaseModel):
    memory_type: str  # 'conversation', 'persona', 'summary'
    content: str
    metadata: Optional[Dict[str, Any]] = None

class GetMemoryRequest(BaseModel):
    memory_type: str  # 'conversation', 'persona', 'summary'
    query: Optional[str] = None  # 如果提供，進行語義搜尋
    limit: int = 10
    include_metadata: bool = True

class MemoryResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# 記憶系統實例 (懶加載)
_memory_system: Optional[MemorySystem] = None

def get_memory_system() -> MemorySystem:
    """獲取記憶系統實例"""
    global _memory_system
    if _memory_system is None:
        try:
            # 初始化嵌入模型
            embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=settings.GOOGLE_API_KEY
            )
            
            # 初始化LLM
            llm = ChatGoogleGenerativeAI(
                model="gemini-pro",
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0.7
            )
            
            # 創建記憶系統
            _memory_system = MemorySystem(
                embeddings=embeddings,
                persona_name="太空直播AI",
                llm=llm
            )
            
            logger.info("記憶系統初始化成功")
        except Exception as e:
            logger.error(f"記憶系統初始化失敗: {e}")
            raise HTTPException(status_code=500, detail=f"記憶系統初始化失敗: {e}")
    
    return _memory_system

@router.post("/save")
async def save_memory(request: SaveMemoryRequest) -> MemoryResponse:
    """儲存記憶到指定的記憶類型"""
    try:
        memory_system = get_memory_system()
        
        # 驗證記憶類型
        valid_types = ['conversation', 'persona', 'summary']
        if request.memory_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"無效的記憶類型: {request.memory_type}. 有效類型: {valid_types}"
            )
        
        # 根據記憶類型選擇對應的儲存器
        if request.memory_type == 'conversation':
            store = memory_system.conversation_store
        elif request.memory_type == 'persona':
            store = memory_system.persona_store
        elif request.memory_type == 'summary':
            store = memory_system.summary_store
        
        # 儲存記憶
        store.add(request.content, request.metadata or {})
        
        logger.info(f"成功儲存 {request.memory_type} 記憶")
        return MemoryResponse(
            success=True,
            message=f"成功儲存 {request.memory_type} 記憶",
            data={"memory_type": request.memory_type, "content_length": len(request.content)}
        )
        
    except Exception as e:
        logger.error(f"儲存記憶失敗: {e}")
        raise HTTPException(status_code=500, detail=f"儲存記憶失敗: {e}")

@router.post("/get")
async def get_memory(request: GetMemoryRequest) -> MemoryResponse:
    """從指定的記憶類型獲取記憶"""
    try:
        memory_system = get_memory_system()
        
        # 驗證記憶類型
        valid_types = ['conversation', 'persona', 'summary']
        if request.memory_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"無效的記憶類型: {request.memory_type}. 有效類型: {valid_types}"
            )
        
        # 根據記憶類型選擇對應的儲存器
        if request.memory_type == 'conversation':
            store = memory_system.conversation_store
        elif request.memory_type == 'persona':
            store = memory_system.persona_store
        elif request.memory_type == 'summary':
            store = memory_system.summary_store
        
        # 獲取記憶
        if request.query:
            # 進行語義搜尋
            results = await store.aretrieve(request.query, request.limit)
        else:
            # 獲取所有記憶
            all_data = store.get_all(limit=request.limit)
            results = []
            if all_data and "documents" in all_data:
                documents = all_data.get("documents", [])
                metadatas = all_data.get("metadatas", [])
                
                # 確保兩個列表長度一致
                min_length = min(len(documents), len(metadatas))
                for i in range(min_length):
                    if documents[i] is not None:  # 確保文檔不為空
                        results.append({
                            "page_content": documents[i],
                            "metadata": metadatas[i] if metadatas[i] is not None else {}
                        })
        
        # 格式化結果
        formatted_results = []
        for result in results:
            if result is not None:  # 確保結果不為空
                metadata = result.get("metadata", {}) or {}  # 處理 None 的情況
                memory_data = {
                    "content": result.get("page_content", ""),
                    "timestamp": metadata.get("timestamp", ""),
                }
                if request.include_metadata:
                    memory_data["metadata"] = metadata
                formatted_results.append(memory_data)
        
        logger.info(f"成功獲取 {len(formatted_results)} 條 {request.memory_type} 記憶")
        return MemoryResponse(
            success=True,
            message=f"成功獲取 {len(formatted_results)} 條 {request.memory_type} 記憶",
            data={
                "memory_type": request.memory_type,
                "memories": formatted_results,
                "total_count": len(formatted_results)
            }
        )
        
    except Exception as e:
        logger.error(f"獲取記憶失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取記憶失敗: {e}")

@router.get("/stats")
async def get_memory_stats() -> MemoryResponse:
    """獲取記憶系統統計資訊"""
    try:
        memory_system = get_memory_system()
        
        # 獲取各類記憶的統計資訊
        try:
            conversation_data = memory_system.conversation_store.get_all(limit=1000) or {}
            persona_data = memory_system.persona_store.get_all(limit=1000) or {}
            summary_data = memory_system.summary_store.get_all(limit=1000) or {}
            
            stats = {
                "conversation_count": len(conversation_data.get("documents", [])),
                "persona_count": len(persona_data.get("documents", [])),
                "summary_count": len(summary_data.get("documents", [])),
                "short_term_count": len(getattr(memory_system.short_term_store, 'memories', [])),
                "system_status": "active"
            }
        except Exception as e:
            logger.warning(f"獲取記憶統計時發生錯誤: {e}")
            stats = {
                "conversation_count": 0,
                "persona_count": 0,
                "summary_count": 0,
                "short_term_count": 0,
                "system_status": "error"
            }
        
        logger.info("成功獲取記憶系統統計資訊")
        return MemoryResponse(
            success=True,
            message="成功獲取記憶系統統計資訊",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"獲取記憶統計失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取記憶統計失敗: {e}") 