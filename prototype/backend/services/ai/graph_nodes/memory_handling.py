"""
記憶檢索、過濾和儲存的相關節點邏輯。
處理與 MemorySystem 的交互，並格式化記憶內容。
"""

import logging
import asyncio
import json
from typing import Dict, List, Any, TypedDict, Optional

from langchain_core.messages import BaseMessage, AIMessage

# 配置基本日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def retrieve_memory_node(state: TypedDict) -> Dict[str, Any]:
    """檢索記憶節點 - 從記憶系統獲取相關記憶和角色信息"""
    user_text = state["processed_user_input"]
    messages = state["messages"]
    input_classification = state["input_classification"]
    memory_system = state.get("_context", {}).get("memory_system")
    
    if not memory_system:
        logging.error("記憶系統未在上下文中提供")
        return {
            "retrieved_memories": ["無法檢索記憶"],
            "persona_info": "無法獲取角色信息",
            "system_alert": "memory_system_not_found"
        }
    
    # 檢索相關記憶 (最近N條消息用於構建上下文)
    history_for_retrieval = messages[-5:] if len(messages) >= 5 else messages
    
    try:
        # 根據輸入分類調整檢索策略
        if input_classification["type"] in ["gibberish", "highly_repetitive"]:
            # 對於亂碼或高度重複的輸入，減少檢索範圍，主要依賴最近對話歷史
            logging.info("檢測到問題輸入，使用保守記憶檢索策略")
            relevant_memories, persona_info = await memory_system.retrieve_context(
                "",  # 使用空字符串作為查詢，只基於最近對話
                history_for_retrieval,
                k=1  # 減少返回的記憶數量
            )
        else:
            # 對於正常輸入，使用標準檢索
            relevant_memories, persona_info = await memory_system.retrieve_context(
                user_text,
                history_for_retrieval
            )
        
        logging.info(f"記憶檢索成功: {len(relevant_memories)} 字符的相關記憶")
        
        # 將記憶轉換為列表形式以便後續處理
        try:
            retrieved_docs = memory_system.conversation_store.get_all()
            retrieved_memories = retrieved_docs["documents"][:5]  # 獲取前5條記憶
        except Exception as e:
            logging.error(f"獲取原始記憶失敗: {e}", exc_info=True)
            retrieved_memories = [relevant_memories]
        
        return {
            "retrieved_memories": retrieved_memories,
            "persona_info": persona_info
        }
    except Exception as e:
        logging.error(f"記憶檢索失敗: {e}", exc_info=True)
        return {
            "retrieved_memories": ["無法檢索記憶"],
            "persona_info": f"我是一位太空網紅。",
            "system_alert": "memory_retrieval_error"
        }

def filter_memory_node(state: TypedDict) -> Dict[str, Any]:
    """記憶過濾節點 - 篩選和驗證檢索到的記憶"""
    retrieved_memories = state["retrieved_memories"]
    user_text = state["processed_user_input"]
    input_classification = state["input_classification"]
    
    filtered_content = []
    
    # 基於輸入分類調整過濾策略
    if input_classification["type"] in ["gibberish", "highly_repetitive"]:
        # 對於問題輸入，採用最保守的過濾
        logging.info("檢測到問題輸入，採用嚴格記憶過濾")
        # 只保留最基本的記憶，避免無效內容
        if len(retrieved_memories) > 0:
            filtered_content = ["先前對話記憶已模糊"]
    else:
        # 正常過濾邏輯
        unique_contents = set()
        
        for memory in retrieved_memories:
            if isinstance(memory, str):
                content = memory.strip()
            else:
                content = str(memory).strip()
            
            # 避免空內容
            if not content:
                continue
            
            # 簡單去重
            normalized_content = "".join(content.split())
            if normalized_content not in unique_contents:
                # 檢查記憶是否包含用戶的怪異輸入 (可能來自先前對話)
                if any(weird_input in content for weird_input in ["DevOps", "j8 dl4", "dl4"]) and \
                   not ("討論DevOps" in content or "開發運維" in content):  # 排除正常語境中的DevOps
                    logging.info(f"過濾掉包含怪異輸入的記憶: {content[:30]}...")
                    continue
                
                filtered_content.append(content)
                unique_contents.add(normalized_content)
    
    # 格式化過濾後的記憶
    filtered_memories = "\n---\n".join(filtered_content[:3])  # 限制到3條記憶
    
    logging.info(f"記憶過濾完成: 從 {len(retrieved_memories)} 條到 {len(filtered_content)} 條")
    
    return {
        "filtered_memories": filtered_memories
    }

async def store_memory_node(state: TypedDict) -> Dict[str, Any]:
    """儲存記憶節點 - 將完成的對話輪次儲存到記憶系統"""
    user_text = state["processed_user_input"]
    final_response = state["final_response"]
    should_store_memory = state["should_store_memory"]
    memory_system = state.get("_context", {}).get("memory_system")
    
    # 更新消息列表
    new_messages = state["messages"].copy()
    new_messages.append(AIMessage(content=final_response))
    
    if should_store_memory and memory_system:
        try:
            # 儲存對話到記憶系統
            memory_system.store_conversation_turn(user_text, final_response)
            logging.info("對話成功儲存到記憶系統")
            
            # 觸發記憶整合
            asyncio.create_task(memory_system.async_consolidate_memories())
        except Exception as e:
            logging.error(f"儲存對話到記憶系統失敗: {e}", exc_info=True)
    else:
        if not memory_system:
            logging.error("記憶系統未在上下文中提供，無法儲存對話")
        else:
            logging.info("基於系統判斷，此輪對話不儲存到長期記憶")
    
    return {
        "messages": new_messages
    } 