# 選擇基礎鏡像
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt 並安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製剩餘的程式碼
COPY . .

# 設定環境變數 (容器中會使用這些變數，實際值由 Docker 執行時提供)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 暴露埠口
EXPOSE 8000

# 定義容器啟動指令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 