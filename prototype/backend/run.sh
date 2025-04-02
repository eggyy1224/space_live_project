#!/bin/bash
# 確保使用正確的 Python 解釋器

# 進入虛擬環境
source venv/bin/activate

python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload 