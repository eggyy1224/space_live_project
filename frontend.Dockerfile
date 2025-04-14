# 第一階段：建構 React 應用
FROM node:18-alpine as builder

# 設定工作目錄
WORKDIR /app

# 複製整個專案（包括腳本和前端代碼）
COPY . /app/

# 設置工作目錄到前端目錄
WORKDIR /app/prototype/frontend

# 安裝依賴
RUN npm install

# 直接執行vite構建跳過TypeScript檢查
RUN node ../../scripts/sync_animations.js && npx vite build --emptyOutDir

# 第二階段：使用 Nginx 提供靜態檔案服務
FROM nginx:alpine

# 複製 Nginx 配置
COPY prototype/frontend/nginx.conf /etc/nginx/conf.d/default.conf

# 從構建階段複製編譯好的檔案
COPY --from=builder /app/prototype/frontend/dist /usr/share/nginx/html

# 修正權限問題 - 確保 Nginx 可以訪問所有靜態資源
RUN find /usr/share/nginx/html -type d -exec chmod 755 {} \; && \
    find /usr/share/nginx/html -type f -exec chmod 644 {} \;

# 暴露 80 端口
EXPOSE 80

# 啟動 Nginx
CMD ["nginx", "-g", "daemon off;"] 