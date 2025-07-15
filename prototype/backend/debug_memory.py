#!/usr/bin/env python3
"""
記憶系統調試腳本
用於檢查 ChromaDB 的實際內容
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.memory_system import MemorySystem
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from core.config import settings

def debug_memory_system():
    """調試記憶系統"""
    print("🔍 開始調試記憶系統...")
    
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
        memory_system = MemorySystem(
            embeddings=embeddings,
            persona_name="太空直播AI",
            llm=llm
        )
        
        print("✅ 記憶系統初始化成功")
        
        # 檢查各種記憶類型
        stores = {
            "conversation": memory_system.conversation_store,
            "persona": memory_system.persona_store,
            "summary": memory_system.summary_store
        }
        
        for store_name, store in stores.items():
            print(f"\n📋 檢查 {store_name} 記憶:")
            
            try:
                # 獲取所有記憶
                all_data = store.get_all(limit=100)
                print(f"   原始資料: {all_data}")
                
                if all_data:
                    documents = all_data.get("documents", [])
                    metadatas = all_data.get("metadatas", [])
                    ids = all_data.get("ids", [])
                    
                    print(f"   文檔數量: {len(documents)}")
                    print(f"   元數據數量: {len(metadatas)}")
                    print(f"   ID數量: {len(ids)}")
                    
                    if documents:
                        print(f"   前3個文檔:")
                        for i, doc in enumerate(documents[:3]):
                            print(f"     {i+1}. {doc}")
                            if i < len(metadatas):
                                print(f"        元數據: {metadatas[i]}")
                else:
                    print("   ❌ 無法獲取資料或資料為空")
                    
            except Exception as e:
                print(f"   ❌ 檢查 {store_name} 時發生錯誤: {e}")
        
        # 檢查短期記憶
        print(f"\n⚡ 短期記憶:")
        short_term_memories = getattr(memory_system.short_term_store, 'memories', [])
        print(f"   短期記憶數量: {len(short_term_memories)}")
        
    except Exception as e:
        print(f"❌ 調試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_memory_system() 