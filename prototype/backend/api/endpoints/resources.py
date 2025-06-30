"""
資源查詢 API 端點
提供系統中所有可用媒體資源的查詢功能
"""

import os
from typing import List, Dict, Optional, Any
from fastapi import APIRouter, HTTPException, Query
from pathlib import Path
import json

router = APIRouter(prefix="/api/resources", tags=["resources"])

# 基礎路徑配置
BASE_DIR = Path(__file__).parent.parent.parent.parent # 指向 prototype 目錄
FRONTEND_PUBLIC_DIR = BASE_DIR / "frontend" / "public"
BACKEND_SONGS_DIR = BASE_DIR / "backend" / "songs"

# 支援的檔案格式
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.m4a', '.flac'}
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
ANIMATION_EXTENSIONS = {'.glb', '.gltf', '.fbx'}
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}

def scan_directory(directory: Path, extensions: set) -> List[Dict[str, Any]]:
    """掃描目錄中的檔案"""
    files = []
    if not directory.exists():
        return files
    
    for file_path in directory.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in extensions:
            # 計算相對路徑
            rel_path = file_path.relative_to(directory)
            files.append({
                "name": file_path.name,
                "path": str(rel_path),
                "size": file_path.stat().st_size,
                "extension": file_path.suffix.lower(),
                "full_path": str(file_path)
            })
    
    return sorted(files, key=lambda x: x["name"])

@router.get("/songs", summary="取得所有歌曲檔案")
async def get_songs() -> Dict[str, Any]:
    """
    取得後端 songs 目錄中的所有音樂檔案
    """
    try:
        songs = scan_directory(BACKEND_SONGS_DIR, AUDIO_EXTENSIONS)
        return {
            "count": len(songs),
            "directory": str(BACKEND_SONGS_DIR),
            "files": songs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"無法讀取歌曲目錄: {str(e)}")

@router.get("/bgm", summary="取得所有背景音樂")
async def get_bgm() -> Dict[str, Any]:
    """
    取得前端 BGM 目錄中的所有背景音樂檔案
    """
    try:
        bgm_dir = FRONTEND_PUBLIC_DIR / "audio" / "BGM"
        bgm_files = scan_directory(bgm_dir, AUDIO_EXTENSIONS)
        return {
            "count": len(bgm_files),
            "directory": str(bgm_dir),
            "files": bgm_files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"無法讀取 BGM 目錄: {str(e)}")

@router.get("/effects", summary="取得所有音效檔案")
async def get_effects() -> Dict[str, Any]:
    """
    取得前端音效目錄中的所有音效檔案
    """
    try:
        effects_dir = FRONTEND_PUBLIC_DIR / "audio" / "effects"
        effect_files = scan_directory(effects_dir, AUDIO_EXTENSIONS)
        return {
            "count": len(effect_files),
            "directory": str(effects_dir),
            "files": effect_files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"無法讀取音效目錄: {str(e)}")

@router.get("/videos", summary="取得所有影片檔案")
async def get_videos() -> Dict[str, Any]:
    """
    取得前端影片目錄中的所有影片檔案
    """
    try:
        videos_dir = FRONTEND_PUBLIC_DIR / "videos"
        video_files = scan_directory(videos_dir, VIDEO_EXTENSIONS)
        return {
            "count": len(video_files),
            "directory": str(videos_dir),
            "files": video_files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"無法讀取影片目錄: {str(e)}")

@router.get("/animations", summary="取得所有動畫檔案")
async def get_animations() -> Dict[str, Any]:
    """
    取得前端動畫目錄中的所有動畫檔案
    """
    try:
        animations_dir = FRONTEND_PUBLIC_DIR / "animations"
        animation_files = scan_directory(animations_dir, ANIMATION_EXTENSIONS)
        return {
            "count": len(animation_files),
            "directory": str(animations_dir),
            "files": animation_files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"無法讀取動畫目錄: {str(e)}")

@router.get("/all", summary="取得所有媒體資源")
async def get_all_resources() -> Dict[str, Any]:
    """
    取得系統中所有可用的媒體資源
    """
    try:
        # 並行掃描所有目錄
        songs = scan_directory(BACKEND_SONGS_DIR, AUDIO_EXTENSIONS)
        bgm = scan_directory(FRONTEND_PUBLIC_DIR / "audio" / "BGM", AUDIO_EXTENSIONS)
        effects = scan_directory(FRONTEND_PUBLIC_DIR / "audio" / "effects", AUDIO_EXTENSIONS)
        videos = scan_directory(FRONTEND_PUBLIC_DIR / "videos", VIDEO_EXTENSIONS)
        animations = scan_directory(FRONTEND_PUBLIC_DIR / "animations", ANIMATION_EXTENSIONS)
        
        return {
            "summary": {
                "total_files": len(songs) + len(bgm) + len(effects) + len(videos) + len(animations),
                "songs_count": len(songs),
                "bgm_count": len(bgm),
                "effects_count": len(effects),
                "videos_count": len(videos),
                "animations_count": len(animations)
            },
            "resources": {
                "songs": songs,
                "bgm": bgm,
                "effects": effects,
                "videos": videos,
                "animations": animations
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"無法掃描資源目錄: {str(e)}")

@router.get("/search", summary="搜索媒體資源")
async def search_resources(
    query: str = Query(..., description="搜索關鍵字"),
    resource_type: Optional[str] = Query(None, description="資源類型: songs, bgm, effects, videos, animations"),
    limit: int = Query(20, ge=1, le=100, description="結果數量限制")
) -> Dict[str, Any]:
    """
    根據關鍵字搜索媒體資源
    """
    try:
        all_resources = await get_all_resources()
        results = []
        
        # 搜索邏輯
        for category, files in all_resources["resources"].items():
            if resource_type and resource_type != category:
                continue
                
            for file_info in files:
                if query.lower() in file_info["name"].lower():
                    file_info["category"] = category
                    results.append(file_info)
                    
                    if len(results) >= limit:
                        break
            
            if len(results) >= limit:
                break
        
        return {
            "query": query,
            "resource_type": resource_type,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失敗: {str(e)}")

@router.get("/config", summary="取得前端資源配置")
async def get_frontend_config() -> Dict[str, Any]:
    """
    讀取前端 resources.ts 配置檔案內容
    """
    try:
        config_path = BASE_DIR / "frontend" / "src" / "config" / "resources.ts"
        if not config_path.exists():
            raise HTTPException(status_code=404, detail="前端配置檔案不存在")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "config_path": str(config_path),
            "content": content,
            "size": len(content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"無法讀取配置檔案: {str(e)}") 