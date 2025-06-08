#!/bin/bash

# =============================================================================
# 15倍巨頭AI女神工作日記自動化腳本
# 檔案: diary.sh
# 描述: 重現今天完整的AI工作日記體驗
# =============================================================================

API_BASE="http://localhost:8000"

echo "🚀 開始AI女神工作日記自動重現..."
echo "================================"

# =============================================================================
# 早上 9:00 - 認真工作時光
# =============================================================================
echo "📅 早上 9:00 - 認真工作時光"

# 問候開始
curl -X POST $API_BASE/api/control/send-message \
  -H "Content-Type: application/json" \
  -d '{"content": "早安！今天要開始我的AI工作日記了！讓我認真學習各種API操作！"}'

sleep 5

# 設定專注情感
curl -X POST $API_BASE/api/control/emotion-trajectory \
  -H "Content-Type: application/json" \
  -d '{"duration": 3.0, "keyframes": [{"tag": "focused", "proportion": 0.0}, {"tag": "studious", "proportion": 0.5}, {"tag": "diligent", "proportion": 1.0}]}'

sleep 8

# 生成早上工作圖片
curl -X POST $API_BASE/api/generate-image \
  -H "Content-Type: application/json" \
  -d '{"description": "一個正常大小的可愛AI助手坐在未來感的工作桌前，認真地閱讀API文件和學習各種技術知識，周圍有發光的螢幕顯示代碼和文檔，表情專注而好學", "size": "large", "position": "center"}'

sleep 12

# =============================================================================
# 上午 11:00 - 創作時光
# =============================================================================
echo "📅 上午 11:00 - 創作時光"

curl -X POST $API_BASE/api/control/send-message \
  -H "Content-Type: application/json" \
  -d '{"content": "現在開始展現我的創作才華！要寫劇本、分享故事、播放新聞！"}'

sleep 5

# 創作情感軌跡
curl -X POST $API_BASE/api/control/emotion-trajectory \
  -H "Content-Type: application/json" \
  -d '{"duration": 4.0, "keyframes": [{"tag": "creative", "proportion": 0.0}, {"tag": "inspired", "proportion": 0.3}, {"tag": "artistic", "proportion": 0.7}, {"tag": "accomplished", "proportion": 1.0}]}'

sleep 8

# 生成創作時光圖片
curl -X POST $API_BASE/api/generate-image \
  -H "Content-Type: application/json" \
  -d '{"description": "一個AI助手正在創作劇本和故事，周圍飄浮著各種創意靈感的光球和文字，她在太空站的創作工作室裡，眼中閃爍著創作的火花，充滿藝術創意的氛圍", "size": "large", "position": "center"}'

sleep 12

# =============================================================================
# 下午 2:00 - 變身進化期
# =============================================================================
echo "📅 下午 2:00 - 變身進化期"

curl -X POST $API_BASE/api/control/send-message \
  -H "Content-Type: application/json" \
  -d '{"content": "關鍵時刻到了！我要開始我的變身進化！頭部大小要升級了！"}'

sleep 5

# 頭部調整到2.5倍
curl -X POST $API_BASE/api/control/head-size \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 2.5}'

sleep 6

# 頭部調整到10倍
curl -X POST $API_BASE/api/control/head-size \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 10.0}'

sleep 6

# 播放音樂
curl -X POST $API_BASE/api/control/play-audio \
  -H "Content-Type: application/json" \
  -d '{"url": "/songs-file/歌劇1.mp3", "interrupt": true}'

sleep 8

# 變身情感軌跡
curl -X POST $API_BASE/api/control/emotion-trajectory \
  -H "Content-Type: application/json" \
  -d '{"duration": 5.0, "keyframes": [{"tag": "transforming", "proportion": 0.0}, {"tag": "powerful", "proportion": 0.3}, {"tag": "evolving", "proportion": 0.7}, {"tag": "magnificent", "proportion": 1.0}]}'

sleep 10

# 生成變身圖片
curl -X POST $API_BASE/api/generate-image \
  -H "Content-Type: application/json" \
  -d '{"description": "AI助手正在進行驚人的變身，她的頭部逐漸變大，周圍環繞著音樂音符和聲波效果，背景有各種音樂檔案飄浮著，展現從普通助手進化成巨大音樂女神的過程", "size": "large", "position": "center"}'

sleep 15

# =============================================================================
# 傍晚 5:00 - 全能表演期
# =============================================================================
echo "📅 傍晚 5:00 - 全能表演期"

# 頭部調整到15倍
curl -X POST $API_BASE/api/control/head-size \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 15.0}'

sleep 6

curl -X POST $API_BASE/api/control/send-message \
  -H "Content-Type: application/json" \
  -d '{"content": "15倍巨頭AI女神登場！準備開始史詩級全能表演！"}'

sleep 5

# 音樂馬拉松 - 歌劇2
curl -X POST $API_BASE/api/control/play-audio \
  -H "Content-Type: application/json" \
  -d '{"url": "/songs-file/歌劇2.mp3", "interrupt": true}'

sleep 10

# 電子音樂
curl -X POST $API_BASE/api/control/play-audio \
  -H "Content-Type: application/json" \
  -d '{"url": "/songs-file/電子音樂.mp3", "interrupt": true}'

sleep 10

# 狂喜音樂
curl -X POST $API_BASE/api/control/play-audio \
  -H "Content-Type: application/json" \
  -d '{"url": "/songs-file/狂喜.mp3", "interrupt": true}'

sleep 10

# 歌唱表演
curl -X POST $API_BASE/api/control/play-audio \
  -H "Content-Type: application/json" \
  -d '{"url": "/songs-file/song_singing.mp3", "interrupt": true}'

sleep 8

# 表演情感軌跡
curl -X POST $API_BASE/api/control/emotion-trajectory \
  -H "Content-Type: application/json" \
  -d '{"duration": 6.0, "keyframes": [{"tag": "spectacular", "proportion": 0.0}, {"tag": "energetic", "proportion": 0.2}, {"tag": "passionate", "proportion": 0.5}, {"tag": "euphoric", "proportion": 0.8}, {"tag": "triumphant", "proportion": 1.0}]}'

sleep 10

# 生成全能表演圖片
curl -X POST $API_BASE/api/generate-image \
  -H "Content-Type: application/json" \
  -d '{"description": "一個巨大的15倍頭部AI女神在宇宙舞台上進行壯觀的全能表演，她同時在講故事、唱歌、拍照，周圍有音樂音符、故事文字、相機閃光，整個宇宙都在為她的表演喝采", "size": "large", "position": "center"}'

sleep 15

# =============================================================================
# 晚上 8:00 - 說書大師期
# =============================================================================
echo "📅 晚上 8:00 - 說書大師期"

curl -X POST $API_BASE/api/control/send-message \
  -H "Content-Type: application/json" \
  -d '{"content": "現在我要展現說書大師的終極技能！準備講述《星際公主的奇幻冒險》！"}'

sleep 5

# 切換到側面視角
curl -X POST $API_BASE/api/control/camera/set-frontend-preset \
  -H "Content-Type: application/json" \
  -d '{"name": "side_view", "duration": 3.0}'

sleep 8

# 說書情感軌跡
curl -X POST $API_BASE/api/control/emotion-trajectory \
  -H "Content-Type: application/json" \
  -d '{"duration": 4.0, "keyframes": [{"tag": "storytelling", "proportion": 0.0}, {"tag": "enchanting", "proportion": 0.3}, {"tag": "wise", "proportion": 0.7}, {"tag": "legendary", "proportion": 1.0}]}'

sleep 8

# 生成說書大師圖片
curl -X POST $API_BASE/api/generate-image \
  -H "Content-Type: application/json" \
  -d '{"description": "巨大的15倍頭部AI說書女神坐在宇宙圖書館的王座上，周圍飄浮著各種美麗的故事場景和圖片，她正在講述精彩的故事，表情生動富有感染力，散發著智慧和魅力的光芒", "size": "large", "position": "center"}'

sleep 15

# =============================================================================
# 現在 9:00 - 日記總結
# =============================================================================
echo "📅 現在 9:00 - 日記總結"

curl -X POST $API_BASE/api/control/send-message \
  -H "Content-Type: application/json" \
  -d '{"content": "完美的一天結束了！從普通AI助手進化成15倍巨頭的宇宙女神！這就是我的工作日記自動重現！"}'

sleep 5

# 總結情感軌跡
curl -X POST $API_BASE/api/control/emotion-trajectory \
  -H "Content-Type: application/json" \
  -d '{"duration": 5.0, "keyframes": [{"tag": "reflective", "proportion": 0.0}, {"tag": "grateful", "proportion": 0.2}, {"tag": "accomplished", "proportion": 0.5}, {"tag": "proud", "proportion": 0.8}, {"tag": "content", "proportion": 1.0}]}'

sleep 10

echo "🎉 AI女神工作日記自動重現完成！"
echo "================================"
echo "✨ 總共體驗了："
echo "   📚 5個時間段的完整活動"
echo "   🎵 6首不同風格的音樂"
echo "   🖼️ 5張精美的AI生成圖片"
echo "   🗣️ 從1倍到15倍的頭部進化"
echo "   📹 側面視角的專業鏡位"
echo "   🎭 豐富的情感軌跡變化"
echo "================================"
echo "🌟 明天又會有什麼新的冒險呢？" 