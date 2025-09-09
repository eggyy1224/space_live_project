from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Optional, List
import os
import subprocess
import asyncio
from pathlib import Path
from utils.logger import logger
import threading
from services.physical_light_control import PhysicalLightControlService

router = APIRouter()

"""
限制白名單：僅允許執行 `experiment_scripts/yoga_sessions/` 目錄下的腳本。
會在啟動時掃描該資料夾下的 .sh 檔案形成白名單。
"""

# 腳本基礎路徑
SCRIPTS_DIR = Path(__file__).parent.parent.parent / "experiment_scripts"
YOGA_DIR = SCRIPTS_DIR / "yoga_sessions"

def _scan_yoga_scripts() -> list[str]:
    try:
        if not YOGA_DIR.exists():
            return []
        scripts = []
        for p in sorted(YOGA_DIR.glob("*.sh")):
            if p.is_file():
                # 轉為相對於 experiment_scripts 的路徑字串
                scripts.append(str(p.relative_to(SCRIPTS_DIR)))
        return scripts
    except Exception:
        return []

# 已註冊的腳本列表（僅 yoga_sessions 內檔案）
REGISTERED_SCRIPTS = _scan_yoga_scripts()

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

# 物理燈條控制：只控制通道 1-3（透過 set_brightness 同步套用），不處理招牌燈（channel 0）
_light_service = PhysicalLightControlService()
_active_scripts_count = 0
_active_scripts_lock = threading.Lock()

def _on_script_start_light():
    global _active_scripts_count
    try:
        with _active_scripts_lock:
            was_zero = (_active_scripts_count == 0)
            _active_scripts_count += 1
        if was_zero:
            logger.info("開啟物理燈條（腳本開始）")
            # 全亮（僅 1-3 通道）
            _light_service.set_brightness(65535)
    except Exception as e:
        logger.error(f"開啟燈條時發生錯誤: {e}")

def _on_script_end_light():
    global _active_scripts_count
    try:
        should_turn_off = False
        with _active_scripts_lock:
            if _active_scripts_count > 0:
                _active_scripts_count -= 1
            if _active_scripts_count == 0:
                should_turn_off = True
        if should_turn_off:
            logger.info("關閉物理燈條（所有腳本結束）")
            _light_service.set_brightness(0)
    except Exception as e:
        logger.error(f"關閉燈條時發生錯誤: {e}")

@router.get("/scripts/list")
async def list_registered_scripts():
    """
    列出所有已註冊可執行的腳本
    """
    scripts_info = []
    
    # 重新掃描以確保清單最新（避免重啟前後清單不同步）
    global REGISTERED_SCRIPTS
    REGISTERED_SCRIPTS = _scan_yoga_scripts()

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
            # 腳本開始：開燈；腳本結束：關燈（僅在所有腳本都結束時）
            _on_script_start_light()
            try:
                result = await run_script_sync(script_path, script_name)
            finally:
                _on_script_end_light()
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

@router.post("/scripts/execute/random-yoga", response_model=ScriptExecutionResponse)
async def execute_random_yoga_script(background_tasks: BackgroundTasks):
    """
    隨機執行 yoga_sessions 目錄中的任一已註冊腳本（背景執行）。
    若所有腳本都在執行中，將返回 409。
    """
    global REGISTERED_SCRIPTS
    if not REGISTERED_SCRIPTS:
        REGISTERED_SCRIPTS = _scan_yoga_scripts()
    if not REGISTERED_SCRIPTS:
        raise HTTPException(status_code=404, detail="找不到可用的瑜伽腳本")

    # 過濾尚未在執行的腳本
    available = [s for s in REGISTERED_SCRIPTS if s not in running_scripts]
    if not available:
        raise HTTPException(status_code=409, detail="所有瑜伽腳本目前都在執行中")

    import random
    script_name = random.choice(available)
    script_path = SCRIPTS_DIR / script_name

    if not script_path.exists():
        raise HTTPException(status_code=404, detail=f"腳本檔案不存在: {script_name}")

    # 背景執行
    background_tasks.add_task(run_script_background, script_path, script_name)
    return ScriptExecutionResponse(
        success=True,
        message=f"腳本 '{script_name}' 已開始在背景執行",
        script_name=script_name,
        execution_mode="background"
    )

@router.post("/scripts/stop/{script_name:path}")
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
        # 腳本開始：開燈
        _on_script_start_light()

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
    finally:
        # 腳本結束：關燈（僅在所有腳本都結束時）
        _on_script_end_light()
