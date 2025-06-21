#!/bin/bash

# --- 自動化展演腳本：測試今日新增的所有外部 API 功能 ---

# 設定後端服務的基礎 URL
BASE_URL="http://localhost:8000/api"
IMAGE_API_URL="$BASE_URL"
NEWS_API_URL="$BASE_URL/news"
CONTROL_API_URL="$BASE_URL/control"

# 函數：發送訊息讓角色說話
speak() {
  CONTENT=$1
  echo "--- 角色說話: $CONTENT ---"
  curl -X POST "$CONTROL_API_URL/send-message" \
       -H "Content-Type: application/json" \
       -d "{\"content\": \"$CONTENT\"}"
  echo ""
}

# 函數：呼叫圖片 API
call_image_api() {
  ENDPOINT=$1
  PAYLOAD=$2
  DESCRIPTION=$3
  echo "--- 測試: $DESCRIPTION ---"
  echo "呼叫: $IMAGE_API_URL/$ENDPOINT"
  echo "內容: $PAYLOAD"
  curl -X POST "$IMAGE_API_URL/$ENDPOINT" \
       -H "Content-Type: application/json" \
       -d "$PAYLOAD"
  echo -e "\n"
}

# 函數：呼叫新聞 API
call_news_api() {
  PAYLOAD=$1
  DESCRIPTION=$2
  echo "--- 測試: $DESCRIPTION ---"
  echo "呼叫: $NEWS_API_URL/speak-latest-news"
  echo "內容: $PAYLOAD"
  curl -X POST "$NEWS_API_URL/speak-latest-news" \
       -H "Content-Type: application/json" \
       -d "$PAYLOAD"
  echo -e "\n"
}

# --- 展演開始 ---

speak "大家好，現在開始為您展示今天新增的外部資訊整合功能。"
sleep 5

# 1. 太空新聞播報
call_news_api '{}' "太空新聞播報 (預設)"
sleep 15 # 等待播報結束

speak "接下來，是地理資訊系統展示。"
sleep 3

# 2. Google 地圖功能展示
call_image_api "generate-map-image" '{"latitude": 25.0330, "longitude": 121.5654, "zoom": 15, "caption": "台北 101"}' "Google 地圖：台北 101 (預設中間)"
sleep 10

call_image_api "generate-map-image" '{"latitude": 23.9739, "longitude": 120.9820, "zoom": 8, "caption": "台灣全島衛星圖", "position": "top-left", "size": "medium"}' "Google 地圖：台灣全島 (左上角)"
sleep 10

speak "現在讓我們來探索宇宙。"
sleep 3

# 3. NASA 圖片搜尋功能展示
call_image_api "search-nasa-image" '{"query": "Pillars of Creation", "caption": "創生之柱", "position": "top-right", "size": "medium"}' "NASA 搜尋：創生之柱 (右上角)"
sleep 10

# 4. NASA EPIC 地球全圖功能展示
call_image_api "get-epic-image" '{"caption": "我們的地球", "position": "center", "size": "large"}' "NASA EPIC：最新地球全圖 (中間大圖)"
sleep 10

speak "最後，我們將所有影像整合在一起。"
sleep 3

# 5. 組合技：同時顯示多張圖片
call_image_api "generate-map-image" '{"latitude": 24.325, "longitude": 120.667, "zoom": 14, "caption": "台中市外埔區", "position": "bottom-left", "size": "small"}' "組合顯示：地圖 (左下角)"
sleep 1
call_image_api "search-nasa-image" '{"query": "Mars Rover", "caption": "火星探測車", "position": "bottom-right", "size": "small"}' "組合顯示：NASA 搜尋 (右下角)"
sleep 10

speak "所有功能展示完畢，感謝您的收看！"

# --- 展演結束 --- 