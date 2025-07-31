import os
import subprocess
import sys
import time
import math
import random
from fastapi import APIRouter, HTTPException, Query
from typing import Literal
from pathlib import Path

router = APIRouter(prefix="/api", tags=["ShowImages"])

# 支援的分類白名單
ALLOWED_CATEGORIES = {"backgrounds", "images", "photos", "screenshots", "selfies"}
# 圖片副檔名
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".heic")
# 圖片根目錄
BASE_IMAGE_DIR = Path(__file__).parent.parent.parent / "space_live_images"


def get_screen_resolution():
    try:
        cmd = "system_profiler SPDisplaysDataType | grep Resolution | awk '{print $2, $4}'"
        result = subprocess.check_output(cmd, shell=True, text=True).strip()
        if 'x' in result:
            parts = result.split('x')
        else:
            parts = result.split()
        width = int(parts[0].strip())
        height = int(parts[1].strip())
        return width, height
    except Exception:
        return 1920, 1080


def find_images(image_dir: Path):
    if not image_dir.is_dir():
        return []
    return [str(image_dir / f) for f in os.listdir(image_dir)
            if f.lower().endswith(IMAGE_EXTENSIONS)]


def show_images_by_preview(image_dir: Path, max_images=50, display_time=8):
    all_images = find_images(image_dir)
    if not all_images:
        raise RuntimeError("No images found in the specified directory.")
    if len(all_images) > max_images:
        images_to_show = random.sample(all_images, max_images)
    else:
        images_to_show = all_images
    for img_path in images_to_show:
        subprocess.run(["open", "-a", "Preview", img_path], check=True)
        time.sleep(0.1)
    time.sleep(1.0)
    try:
        screen_width, screen_height = get_screen_resolution()
        menu_bar_height = 23
        num_windows = len(images_to_show)
        if num_windows > 0:
            cols = int(math.ceil(math.sqrt(num_windows)))
            rows = int(math.ceil(num_windows / cols))
            cell_width = screen_width // cols
            cell_height = (screen_height - menu_bar_height) // rows
            script = f'''
            tell application "Preview"
                activate
                set window_list to every window
                set i to 0
                repeat with a_window in window_list
                    try
                        set row_num to (i div {cols})
                        set col_num to (i mod {cols})
                        set cell_x to col_num * {cell_width}
                        set cell_y to (row_num * {cell_height}) + {menu_bar_height}
                        if {cell_width} < {cell_height} then
                            set square_size to {cell_width}
                        else
                            set square_size to {cell_height}
                        end if
                        set new_x to cell_x + ({cell_width} - square_size) / 2
                        set new_y to cell_y + ({cell_height} - square_size) / 2
                        set bounds of a_window to {new_x, new_y, new_x + square_size, new_y + square_size}
                        set i to i + 1
                    end try
                end repeat
            end tell
            '''
            subprocess.run(["osascript", "-e", script], check=True, capture_output=True, text=True)
    except Exception:
        pass
    time.sleep(display_time)
    try:
        subprocess.run(["osascript", "-e", 'tell application "Preview" to quit'], check=True)
    except Exception:
        pass


@router.post("/show_images_by_preview")
async def show_images_by_preview_api(
    category: Literal["backgrounds", "images", "photos", "screenshots", "selfies"] = Query(..., description="圖片分類")
):
    """
    用 Mac Preview 展示指定分類資料夾下的所有圖片
    """
    if category not in ALLOWED_CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category.")
    image_dir = BASE_IMAGE_DIR / category
    try:
        show_images_by_preview(image_dir)
        return {"status": "success", "message": f"已展示 {category} 分類的圖片"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"展示圖片失敗: {e}")