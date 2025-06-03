#!/bin/bash

# 實驗腳本 4: 今日銀河焦點 (新聞播報)
# 展示包含起承轉合的敘事流程，並整合多種特效

BASE_URL="http://localhost:8000/api"

echo "--- 今日銀河焦點：開始播報 ---"

# --- 起：開場 ---
echo ">>> 開場：節目開始"

# 1. 開場問候與設定初始情緒
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "觀眾朋友們晚安，歡迎收看今晚的【今日銀河焦點】。", "message_type": "chat-message"}' | jq .

curl -X POST "$BASE_URL/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{"duration": 2.0, "keyframes": [{"tag": "neutral", "proportion": 0.0}, {"tag": "interested", "proportion": 1.0}]}' | jq .

# 2. 設置開場 BGM 和太空船環境音
curl -X POST "$BASE_URL/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{"bgmUrl": "/audio/BGM/spacelive_theme.mp3", "sfxUrl": "/audio/effects/spaceship_ambience_01.mp3", "bgmVolume": 0.6, "sfxVolume": 0.3}' | jq .

# 3. 設定標準主播鏡位
curl -X POST "$BASE_URL/control/camera/set-angle" \
  -H "Content-Type: application/json" \
  -d '{"pitch": 0, "yaw": 0, "roll": 0}' | jq .

# 4. 螢幕1顯示節目 Logo 或片頭 (使用太空直播中示意)
curl -X PUT "$BASE_URL/monitors/screen1" \
  -H "Content-Type: application/json" \
  -d '{"content": "/videos/太空直播中.mp4", "visible": true, "volume": 0}' | jq .

sleep 5 # 等待開場完成

# --- 承：發展第一則新聞 ---
echo ">>> 發展：報導第一則新聞 - 新星系探索任務"

# 5. 主播播報第一則新聞
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "首先帶您關註，銀河聯邦最近成功發射了『探索者七號』探測器，目標是鄰近的三角座星系，預計將帶回該星系前所未有的高清圖像與生命跡象數據。", "message_type": "chat-message"}' | jq .

# 6. 情緒轉為專注思考
curl -X POST "$BASE_URL/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{"duration": 3.0, "keyframes": [{"tag": "interested", "proportion": 0.0}, {"tag": "thinking", "proportion": 1.0}]}' | jq .

# 7. 螢幕2顯示火箭發射畫面
curl -X PUT "$BASE_URL/monitors/screen2" \
  -H "Content-Type: application/json" \
  -d '{"content": "/videos/火箭發射.mp4", "visible": true, "volume": 0.7}' | jq .

# 8. 播放鍵盤/資料處理音效
curl -X POST "$BASE_URL/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{"url": "/audio/effects/Ambient_keyboard_cli_2.mp3", "volume": 0.5, "interrupt": false}' | jq .

sleep 8 # 新聞播報時間

# 9. 主播過渡語句
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "這次任務被譽為本世紀最重要的深空探索之一，科學家們對此充滿期待。", "message_type": "chat-message"}' | jq .

# 10. 關閉螢幕2的火箭影片
curl -X PUT "$BASE_URL/monitors/screen2" \
  -H "Content-Type: application/json" \
  -d '{"visible": false}' | jq .

sleep 3

# --- 轉：突發新聞 ---
echo ">>> 轉折：插播突發新聞 - 偵測到神秘宇宙訊號"

# 11. 播放突發新聞音效/片頭 (台灣綜藝音效示意)
curl -X POST "$BASE_URL/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{"url": "/audio/effects/taiwan_variety_sfx_01.mp3", "volume": 0.8, "interrupt": true}' | jq .

# 12. 主播插播突發新聞，情緒轉為驚訝
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "好的觀眾朋友們，我們剛剛收到一則突發消息！天文監測站偵測到一組來自獵戶座懸臂深處的神秘重複訊號，目前來源與意圖不明！", "message_type": "chat-message"}' | jq .

curl -X POST "$BASE_URL/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{"duration": 2.0, "keyframes": [{"tag": "thinking", "proportion": 0.0}, {"tag": "surprised", "proportion": 0.7}, {"tag": "interested", "proportion": 1.0}]}' | jq .

# 13. 攝影機快速拉近，營造緊張感
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{"pitch": 5, "yaw": 0, "roll": 5, "fov": 45, "duration": 1.0}' | jq .

# 14. 螢幕3顯示黑洞/神秘現象 (黑洞影片示意)
curl -X PUT "$BASE_URL/monitors/screen3" \
  -H "Content-Type: application/json" \
  -d '{"content": "/videos/黑洞.mp4", "visible": true, "volume": 0.6}' | jq .

# 15. 觸發Murmur (模擬新聞編輯台的騷動與討論)
curl -X POST "$BASE_URL/control/trigger-murmur" \
  -H "Content-Type: application/json" \
  -d '{"topic": "warmup", "force": true}' | jq .

sleep 7 # 突發新聞播報時間

# 16. 主播持續報導
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "專家正在緊急分析這些訊號的模式與可能來源，我們將為您持續追蹤報導。", "message_type": "chat-message"}' | jq .

sleep 3

# --- 合：總結與展望 ---
echo ">>> 總結：分析與未來展望"

# 17. 主播進行分析與總結，情緒轉為思考與希望
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "無論這組訊號的來源為何，它再次提醒我們宇宙充滿未知與可能。每一次的探索與發現，都讓我們對自身在宇宙中的位置有更深的思考。", "message_type": "chat-message"}' | jq .

curl -X POST "$BASE_URL/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{"duration": 4.0, "keyframes": [{"tag": "interested", "proportion": 0.0}, {"tag": "thinking", "proportion": 0.5}, {"tag": "hopeful", "proportion": 1.0}]}' | jq .

# 18. 背景音樂轉為較為平靜或帶有希望的音樂
curl -X POST "$BASE_URL/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{"bgmUrl": "/audio/BGM/space_live_country_theme1.mp3", "sfxUrl": "/audio/effects/winds_blowing.mp3", "bgmVolume": 0.5, "sfxVolume": 0.2, "transitionDuration": 3.0}' | jq .

# 19. 攝影機緩慢拉遠，恢復正常鏡位
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{"pitch": 0, "yaw": 0, "roll": 0, "fov": 50, "duration": 3.0}' | jq .

# 20. 螢幕1、3更換為星雲圖或宇宙背景
curl -X PUT "$BASE_URL/monitors/screen1" \
  -H "Content-Type: application/json" \
  -d '{"content": "/videos/模擬星雲圖.mp4", "visible": true, "volume": 0.3}' | jq .
curl -X PUT "$BASE_URL/monitors/screen3" \
  -H "Content-Type: application/json" \
  -d '{"content": "/videos/space_live_video_1.mp4", "visible": true, "volume": 0.3}' | jq .


sleep 8 # 總結時間

# 21. 主播結語
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "感謝您收看今晚的【今日銀河焦點】，期待在宇宙的下一個驚奇中與您再會。晚安。", "message_type": "chat-message"}' | jq .

# 22. 播放結束音效或淡出 BGM
curl -X POST "$BASE_URL/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{"url": "/audio/effects/測試音效5.mp3", "volume": 0.6, "interrupt": false}' | jq . # 使用一個簡短音效示意結束

sleep 4

# 23. 清理螢幕
curl -X PUT "$BASE_URL/monitors/screen1" \
  -H "Content-Type: application/json" \
  -d '{"visible": false}' | jq .
curl -X PUT "$BASE_URL/monitors/screen3" \
  -H "Content-Type: application/json" \
  -d '{"visible": false}' | jq .

# 24. 重設情緒為 neutral
curl -X POST "$BASE_URL/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{"duration": 1.0, "keyframes": [{"tag": "neutral", "proportion": 1.0}]}' | jq .

echo "--- 今日銀河焦點：播報完畢 ---" 