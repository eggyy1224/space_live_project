from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Optional, List
import os
import subprocess
import asyncio
from pathlib import Path
from utils.logger import logger

router = APIRouter()

# 腳本基礎路徑
SCRIPTS_DIR = Path(__file__).parent.parent.parent / "experiment_scripts"

# 已註冊的腳本列表（安全性考量，只允許執行預定義的腳本）
REGISTERED_SCRIPTS = [
    "meta_self.sh",
    "remix_scene.sh",
    "space_story_script.sh",
    "news_broadcast.sh",
    "space_yoga2.sh",
    # 新增：瑜伽教學基線腳本（位於子目錄 yoga_sessions）
    "yoga_sessions/space_yoga_teacher_baseline.sh",
    # 新增：瑜伽教學基線腳本第二幕（位於子目錄 yoga_sessions）
    "yoga_sessions/space_yoga_teacher_baseline_scene2.sh",
]

class ScriptExecutionRequest(BaseModel):
    script_name: str
    background: bool = True  # 預設在背景執行

class ScriptExecutionResponse(BaseModel):
    success: bool
    message: str
    script_name: str
    execution_mode: str

# 儲存正在執行的腳本狀態
running_scripts: Dict[str, subprocess.Popen] = {}

@router.get("/scripts/list")
async def list_registered_scripts():
    """
    列出所有已註冊可執行的腳本
    """
    scripts_info = []
    
    for script_name in REGISTERED_SCRIPTS:
        script_path = SCRIPTS_DIR / script_name
        if script_path.exists():
            # 讀取腳本前幾行來獲取描述
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:10]  # 讀取前10行
                    description = ""
                    for line in lines:
                        if line.strip().startswith('#') and '---' in line:
                            description = line.strip().replace('#', '').replace('-', '').strip()
                            break
                
                scripts_info.append({
                    "name": script_name,
                    "description": description or "無描述",
                    "exists": True,
                    "is_running": script_name in running_scripts
                })
            except Exception as e:
                scripts_info.append({
                    "name": script_name,
                    "description": f"讀取錯誤: {str(e)}",
                    "exists": True,
                    "is_running": script_name in running_scripts
                })
        else:
            scripts_info.append({
                "name": script_name,
                "description": "腳本檔案不存在",
                "exists": False,
                "is_running": False
            })
    
    return {
        "registered_scripts": scripts_info,
        "total_count": len(REGISTERED_SCRIPTS),
        "running_count": len(running_scripts)
    }

@router.post("/scripts/execute", response_model=ScriptExecutionResponse)
async def execute_script(request: ScriptExecutionRequest, background_tasks: BackgroundTasks):
    """
    執行指定的腳本
    """
    script_name = request.script_name
    
    # 安全性檢查：只允許執行已註冊的腳本
    if script_name not in REGISTERED_SCRIPTS:
        raise HTTPException(
            status_code=400,
            detail=f"腳本 '{script_name}' 未註冊。請使用 /scripts/list 查看可用腳本。"
        )
    
    script_path = SCRIPTS_DIR / script_name
    
    # 檢查腳本是否存在
    if not script_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"腳本檔案 '{script_name}' 不存在於 {SCRIPTS_DIR}"
        )
    
    # 檢查腳本是否已在執行
    if script_name in running_scripts:
        raise HTTPException(
            status_code=409,
            detail=f"腳本 '{script_name}' 目前正在執行中"
        )
    
    logger.info(f"準備執行腳本: {script_name}")
    
    try:
        if request.background:
            # 背景執行
            background_tasks.add_task(run_script_background, script_path, script_name)
            return ScriptExecutionResponse(
                success=True,
                message=f"腳本 '{script_name}' 已開始在背景執行",
                script_name=script_name,
                execution_mode="background"
            )
        else:
            # 同步執行（等待完成）
            result = await run_script_sync(script_path, script_name)
            return ScriptExecutionResponse(
                success=result["success"],
                message=result["message"],
                script_name=script_name,
                execution_mode="synchronous"
            )
            
    except Exception as e:
        logger.error(f"執行腳本時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"執行腳本時發生錯誤: {str(e)}"
        )

@router.post("/scripts/stop/{script_name}")
async def stop_script(script_name: str):
    """
    停止正在執行的腳本
    """
    if script_name not in running_scripts:
        raise HTTPException(
            status_code=404,
            detail=f"腳本 '{script_name}' 目前未在執行中"
        )
    
    try:
        process = running_scripts[script_name]
        process.terminate()
        
        # 等待進程結束，超時後強制終止
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        
        del running_scripts[script_name]
        logger.info(f"腳本 {script_name} 已停止")
        
        return {
            "success": True,
            "message": f"腳本 '{script_name}' 已成功停止",
            "script_name": script_name
        }
        
    except Exception as e:
        logger.error(f"停止腳本時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"停止腳本時發生錯誤: {str(e)}"
        )

@router.post("/scripts/stop-all")
async def stop_all_scripts():
    """
    停止所有正在執行的腳本
    """
    if not running_scripts:
        return {
            "success": True,
            "message": "目前沒有正在執行的腳本",
            "stopped_scripts": []
        }
    
    stopped_scripts = []
    failed_scripts = []
    
    for script_name, process in list(running_scripts.items()):
        try:
            process.terminate()
            
            # 等待進程結束，超時後強制終止
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            
            del running_scripts[script_name]
            stopped_scripts.append(script_name)
            logger.info(f"腳本 {script_name} 已停止")
            
        except Exception as e:
            failed_scripts.append(f"{script_name}: {str(e)}")
            logger.error(f"停止腳本 {script_name} 時發生錯誤: {str(e)}")
    
    if failed_scripts:
        return {
            "success": False,
            "message": f"部分腳本停止失敗",
            "stopped_scripts": stopped_scripts,
            "failed_scripts": failed_scripts
        }
    else:
        return {
            "success": True,
            "message": f"成功停止 {len(stopped_scripts)} 個腳本",
            "stopped_scripts": stopped_scripts
        }

@router.get("/scripts/status")
async def get_scripts_status():
    """
    取得所有腳本的執行狀態
    """
    return {
        "running_scripts": list(running_scripts.keys()),
        "total_running": len(running_scripts)
    }

async def run_script_sync(script_path: Path, script_name: str) -> Dict:
    """
    同步執行腳本
    """
    try:
        # 使腳本可執行
        os.chmod(script_path, 0o755)
        
        # 執行腳本
        process = await asyncio.create_subprocess_exec(
            "bash", str(script_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=script_path.parent
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            logger.info(f"腳本 {script_name} 執行完成")
            return {
                "success": True,
                "message": f"腳本 '{script_name}' 執行完成",
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore')
            }
        else:
            logger.error(f"腳本 {script_name} 執行失敗，返回碼: {process.returncode}")
            return {
                "success": False,
                "message": f"腳本執行失敗，返回碼: {process.returncode}",
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore')
            }
            
    except Exception as e:
        logger.error(f"執行腳本時發生異常: {str(e)}")
        return {
            "success": False,
            "message": f"執行腳本時發生異常: {str(e)}"
        }

def run_script_background(script_path: Path, script_name: str):
    """
    背景執行腳本
    """
    try:
        # 使腳本可執行
        os.chmod(script_path, 0o755)
        
        logger.info(f"開始背景執行腳本: {script_name}")
        
        # 啟動進程
        process = subprocess.Popen(
            ["bash", str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=script_path.parent
        )
        
        # 記錄正在執行的腳本
        running_scripts[script_name] = process
        
        # 等待進程完成
        stdout, stderr = process.communicate()
        
        # 從執行列表中移除
        if script_name in running_scripts:
            del running_scripts[script_name]
        
        if process.returncode == 0:
            logger.info(f"背景腳本 {script_name} 執行完成")
        else:
            logger.error(f"背景腳本 {script_name} 執行失敗，返回碼: {process.returncode}")
            logger.error(f"錯誤輸出: {stderr.decode('utf-8', errors='ignore')}")
            
    except Exception as e:
        logger.error(f"背景執行腳本時發生異常: {str(e)}")
        # 確保從執行列表中移除
        if script_name in running_scripts:
            del running_scripts[script_name] 
