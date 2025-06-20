# Cursor API Control Response Guidelines v2.0
## 太空直播系統終極操作指南

### 🎯 核心理念：從API呼叫到藝術表演
這不只是技術文檔，而是將API組合成震撼表演的藝術指南。每個API呼叫都是樂器，組合技就是交響樂。

## 🚨 黃金法則：語音+情緒=生命力
**THE UNBREAKABLE RULE**: `send-message` 和 `emotion-trajectory` 必須成對使用，這是所有表演的基礎。
```bash
# ✅ 正確：生動的角色
curl -X POST .../send-message -d '{"content": "大家好！"}' && \
curl -X POST .../emotion-trajectory -d '{"duration": 3.0, "keyframes": [{"tag": "excited", "proportion": 1.0}]}'

# ❌ 錯誤：沒有生命力的機器人
curl -X POST .../send-message -d '{"content": "大家好！"}'  # 只有聲音沒有情感
```

## 📁 快速導航：資源在哪裡找？
**不要死記硬背！學會探索！**

| 資源類型 | 探索指令 | URL前綴 | 使用場景 |
|---------|---------|---------|---------|
| BGM音樂 | `ls prototype/frontend/public/audio/BGM/` | `/audio/BGM/` | 背景氛圍 |
| 音效 | `ls prototype/frontend/public/audio/effects/` | `/audio/effects/` | 特殊效果 |
| 歌曲 | `ls prototype/backend/songs/` | `/songs-file/` | play-audio |
| 影片 | `ls prototype/frontend/public/videos/` | `/videos/` | Monitor螢幕 |
| 動畫 | `cat prototype/shared/config/animations.json` | 直接使用名稱 | 角色動作 |
| 生成圖片 | `ls prototype/backend/generated_images/` | 檔案名稱 | 重複使用 |

## 🎪 連續技系統：從基礎到終極

### Level 1: 基礎連續技 (3連擊)
**模式**: 語音+情緒 → 動作 → 鏡頭
```bash
curl -X POST .../send-message -d '{"content": "開始表演！"}' && \
curl -X POST .../emotion-trajectory -d '{"duration": 3.0, "keyframes": [{"tag": "excited", "proportion": 1.0}]}' && \
curl -X POST .../character/animation -d '{"animation": "舞步1", "speed": 2.0}' && \
curl -X POST .../camera/set-frontend-preset -d '{"name": "center_orbit_default", "duration": 2.0}'
```

### Level 2: 進階連續技 (5連擊)
**模式**: BGM → 語音+情緒 → 動作 → 頭部特效 → 鏡頭運動
```bash
curl -X POST .../background-audio -d '{"bgmUrl": "/audio/BGM/heavy_metal_bgm_01.mp3"}' && \
curl -X POST .../send-message -d '{"content": "準備震撼！"}' && \
curl -X POST .../emotion-trajectory -d '{"duration": 4.0, "keyframes": [{"tag": "excited", "proportion": 0.0}, {"tag": "amazed", "proportion": 1.0}]}' && \
curl -X POST .../character/animation -d '{"animation": "舞步2", "speed": 3.0}' && \
curl -X POST .../head-size -d '{"scaleFactor": 4.0}' && \
curl -X POST .../camera/set-frontend-preset -d '{"name": "dramatic_angle_1", "duration": 1.5}'
```

### Level 3: 終極連續技 (7+連擊)
**模式**: 背景 → BGM → 語音+情緒 → 動作 → 頭部特效 → Monitor牆 → 圖片生成
```bash
curl -X POST .../generate-background-image -d '{"description": "太空演唱會舞台", "aspect_ratio": "16:9"}' && \
curl -X POST .../background-audio -d '{"bgmUrl": "/audio/BGM/spacelive_theme_bgm_04.mp3"}' && \
curl -X POST .../send-message -d '{"content": "史上最強演唱會開始！"}' && \
curl -X POST .../emotion-trajectory -d '{"duration": 8.0, "keyframes": [{"tag": "excited", "proportion": 0.0}, {"tag": "amazed", "proportion": 0.5}, {"tag": "confident", "proportion": 1.0}]}' && \
curl -X POST .../character/animation -d '{"animation": "舞步3", "speed": 4.0}' && \
curl -X POST .../head-size -d '{"scaleFactor": 6.0}' && \
curl -X PUT .../monitors/screen1 -d '{"content": "/videos/太空辣妹跳舞.mp4", "volume": 0.8, "visible": true, "playing": true}' && \
curl -X PUT .../monitors/screen2 -d '{"content": "/videos/太空史萊姆.mp4", "volume": 0.7, "visible": true, "playing": true}' && \
curl -X PUT .../monitors/screen3 -d '{"content": "/videos/太空打卡.mp4", "volume": 0.6, "visible": true, "playing": true}' && \
curl -X POST .../generate-image -d '{"description": "璀璨舞台煙火", "position": "center-left", "size": "large", "duration": 60.0}'
```

## 🎨 高級技巧

### 圖片位置戰略
**永遠不要擋住角色！**
- ✅ 安全位置: `center-left`, `center-right`, `top-left`, `top-right`, `bottom-left`, `bottom-right`
- ❌ 危險位置: `center` (會擋住角色)

### Monitor音量階層
**創造聲音層次感**
- 主要內容: `volume: 1.0`
- 次要內容: `volume: 0.8`
- 背景環境: `volume: 0.6`

### 頭部特效進化
**戲劇性漸進式放大**
```bash
# 建立張力
curl -X POST .../head-size -d '{"scaleFactor": 2.0}' && sleep 1 && \
curl -X POST .../head-size -d '{"scaleFactor": 4.0}' && sleep 1 && \
curl -X POST .../head-size -d '{"scaleFactor": 8.0}' && sleep 2 && \
# 回歸正常
curl -X POST .../head-size -d '{"scaleFactor": 1.5}'
```

### 攝影機編舞
**引導觀眾視線**
```bash
curl -X POST .../camera/set-frontend-preset -d '{"name": "center_orbit_default", "duration": 2.0}' && sleep 2 && \
curl -X POST .../camera/set-frontend-preset -d '{"name": "fly_by_left", "duration": 1.0}' && sleep 1 && \
curl -X POST .../camera/set-frontend-preset -d '{"name": "dramatic_angle_1", "duration": 1.5}'
```

## 🔥 特殊組合技

### 創意循環技
**AI圖片連續進化**
```bash
# 第一階段：基礎自拍
curl -X POST .../take-selfie -d '{"description": "太空DJ", "position": "center-left", "duration": 45.0}' && \
# 第二階段：風格進化 (自動使用前一張作為參考)
curl -X POST .../continue-selfie -d '{"modification": "變成賽博朋克風格", "position": "center-right", "duration": 50.0}' && \
# 第三階段：背景呼應
curl -X POST .../generate-background-image -d '{"description": "賽博朋克太空夜店", "aspect_ratio": "16:9"}'
```

### 多圖同時展示技
**四角同時爆發**
```bash
curl -X POST .../show-existing-image -d '{"filename": "image_xxx.png", "position": "top-left", "size": "medium", "duration": 30.0}' && \
curl -X POST .../show-existing-image -d '{"filename": "selfie_yyy.png", "position": "top-right", "size": "medium", "duration": 35.0}' && \
curl -X POST .../show-existing-image -d '{"filename": "background_zzz.png", "position": "bottom-left", "size": "medium", "duration": 40.0}' && \
curl -X POST .../show-existing-image -d '{"filename": "image_aaa.png", "position": "bottom-right", "size": "medium", "duration": 45.0}'
```

## 📋 完整API參考

### 核心控制端點
| 方法 | 路徑 | 用途 | 關鍵參數 |
|-----|------|------|---------|
| POST | `/api/control/send-message` | 角色說話 | `content` (必須) |
| POST | `/api/control/emotion-trajectory` | 表情控制 | `duration`, `keyframes` (必須) |
| POST | `/api/control/character/animation` | 角色動作 | `animation`, `speed`, `loop` |
| POST | `/api/control/head-size` | 頭部縮放 | `scaleFactor` (0.1-20.0) |
| POST | `/api/control/background-audio` | 背景音樂 | `bgmUrl` |
| POST | `/api/control/camera/set-frontend-preset` | 鏡頭預設 | `name`, `duration` |

### 圖片生成端點
| 方法 | 路徑 | 用途 | 位置選項 |
|-----|------|------|---------|
| POST | `/api/generate-image` | 生成新圖片 | 7種位置預設 |
| POST | `/api/take-selfie` | 角色自拍 | 可指定風格描述 |
| POST | `/api/continue-selfie` | 自拍進化 | 自動使用最新自拍 |
| POST | `/api/show-existing-image` | 顯示舊圖片 | 重複利用已生成 |
| POST | `/api/generate-background-image` | 背景圖片 | 16:9 最佳 |

### Monitor控制
| 方法 | 路徑 | 用途 | 支援格式 |
|-----|------|------|---------|
| PUT | `/api/monitors/{screen1/screen2/screen3}` | 影片控制 | MP4影片檔 |
| GET | `/api/monitors` | 查看狀態 | 三螢幕同步 |

## ⚡ 實戰最佳實踐

### 1. 表演前檢查
```bash
# 確認連線狀態
curl -X GET http://localhost:8000/api/control/status
```

### 2. 資源探索習慣
```bash
# 每次表演前都先探索可用資源
ls prototype/frontend/public/audio/BGM/     # 音樂選擇
ls prototype/frontend/public/videos/        # 影片選擇  
ls prototype/backend/generated_images/      # 圖片重用
```

### 3. 組合技執行順序
1. **建立基礎** - 語音+情緒 (核心)
2. **加入層次** - 音樂、動作、視覺
3. **創造高潮** - 特效、多重刺激
4. **優雅收尾** - 復原設定、感謝觀眾

### 4. 錯誤處理策略
- API失敗時檢查 `detail` 欄位
- 路徑錯誤時參考上方資源表格
- 連線問題時重新檢查 WebSocket 狀態
- 效果不如預期時拆解測試各個組件

### 5. 創意發展原則
- **不要重複** - 每次都探索新資源組合
- **建立節奏** - 用 sleep 控制時間感
- **層次堆疊** - 從簡單到複雜逐步建構
- **觀眾導向** - 考慮視覺衝擊和情感反應

## 🎭 高級應用場景

### 場景1: 太空夜店模式
```bash
# 環境建立
curl -X POST .../generate-background-image -d '{"description": "霓虹閃爍的太空夜店", "aspect_ratio": "16:9"}' && \
curl -X POST .../background-audio -d '{"bgmUrl": "/audio/BGM/heavy_metal_bgm_02.mp3"}' && \
# 角色表演
curl -X POST .../send-message -d '{"content": "歡迎來到太空夜店！今晚我們徹夜狂歡！"}' && \
curl -X POST .../emotion-trajectory -d '{"duration": 6.0, "keyframes": [{"tag": "excited", "proportion": 0.0}, {"tag": "happy", "proportion": 1.0}]}' && \
curl -X POST .../character/animation -d '{"animation": "舞步2", "speed": 3.5}' && \
curl -X POST .../head-size -d '{"scaleFactor": 5.0}'
```

### 場景2: 太空瑜伽教學
```bash
# 寧靜環境
curl -X POST .../control/environment/preset -d '{"preset": "dawn"}' && \
curl -X POST .../background-audio -d '{"bgmUrl": "/audio/BGM/spacelive_theme_bgm_01.mp3"}' && \
# 教學開始
curl -X POST .../send-message -d '{"content": "讓我們在太空中找到內心的平靜，開始瑜伽練習"}' && \
curl -X POST .../emotion-trajectory -d '{"duration": 8.0, "keyframes": [{"tag": "serene", "proportion": 1.0}]}' && \
curl -X POST .../character/animation -d '{"animation": "運動1", "speed": 0.8}' && \
curl -X POST .../camera/set-frontend-preset -d '{"name": "overview", "duration": 3.0}'
```

### 場景3: 新聞播報模式
```bash
# 專業環境
curl -X POST .../control/environment/preset -d '{"preset": "studio"}' && \
curl -X POST .../camera/set-frontend-preset -d '{"name": "head_close_up", "duration": 2.0}' && \
# 播報開始
curl -X POST .../send-message -d '{"content": "這裡是太空新聞中心，我是您的主播，為您帶來最新的宇宙動態"}' && \
curl -X POST .../emotion-trajectory -d '{"duration": 10.0, "keyframes": [{"tag": "confident", "proportion": 0.0}, {"tag": "professional", "proportion": 1.0}]}' && \
curl -X POST .../character/animation -d '{"animation": "Idle", "speed": 1.0}'
```

## 🚀 終極連續技範例

### 史上最強10連擊
```bash
echo "🚀 史上最強連續技開始！" && \
# 1. 場景設定
curl -X POST .../generate-background-image -d '{"description": "史詩太空競技場", "aspect_ratio": "16:9"}' && \
# 2. 音樂啟動
curl -X POST .../background-audio -d '{"bgmUrl": "/audio/BGM/heavy_metal_bgm_03.mp3"}' && \
# 3. 開場白 (語音+情緒)
curl -X POST .../send-message -d '{"content": "準備迎接史上最震撼的太空表演！"}' && \
curl -X POST .../emotion-trajectory -d '{"duration": 5.0, "keyframes": [{"tag": "excited", "proportion": 0.0}, {"tag": "amazed", "proportion": 1.0}]}' && \
# 4. 動作表演
curl -X POST .../character/animation -d '{"animation": "舞步3", "speed": 4.0}' && \
# 5. 頭部特效
curl -X POST .../head-size -d '{"scaleFactor": 7.0}' && \
# 6-8. 三螢幕影片牆
curl -X PUT .../monitors/screen1 -d '{"content": "/videos/太空辣妹跳舞.mp4", "volume": 1.0, "visible": true, "playing": true}' && \
curl -X PUT .../monitors/screen2 -d '{"content": "/videos/太空史萊姆.mp4", "volume": 0.8, "visible": true, "playing": true}' && \
curl -X PUT .../monitors/screen3 -d '{"content": "/videos/space_live_video_1.mp4", "volume": 0.6, "visible": true, "playing": true}' && \
# 9. 圖片特效
curl -X POST .../generate-image -d '{"description": "爆炸性煙火特效", "position": "center-left", "size": "large", "duration": 60.0}' && \
# 10. 攝影機運動
curl -X POST .../camera/set-frontend-preset -d '{"name": "center_orbit_high_1", "duration": 2.0}' && \
echo "🎉 連續技完成！"
```

---

## 📝 快速備忘錄

### 必記口訣
1. **語音情緒不分離** - send-message + emotion-trajectory
2. **資源探索不死記** - 用 ls 指令找新內容  
3. **圖片位置避中央** - 不要擋住角色
4. **音量層次要分明** - 1.0 → 0.8 → 0.6
5. **頭部特效要漸進** - 建立戲劇張力
6. **表演結束要復原** - 回到預設狀態

### 常用指令速查
```bash
# 狀態檢查
curl -X GET http://localhost:8000/api/control/status

# 基礎表演 (語音+情緒)
curl -X POST .../send-message -d '{"content": "內容"}' && \
curl -X POST .../emotion-trajectory -d '{"duration": 3.0, "keyframes": [{"tag": "happy", "proportion": 1.0}]}'

# 資源探索
ls prototype/frontend/public/audio/BGM/
ls prototype/frontend/public/videos/
ls prototype/backend/generated_images/

# 重置狀態
curl -X POST .../head-size -d '{"scaleFactor": 1.0}'
curl -X POST .../camera/set-frontend-preset -d '{"name": "overview", "duration": 2.0}'
```

**記住：這不只是API文檔，這是創造震撼表演的藝術指南！每一次呼叫都是在創作，每一個組合都是在編舞。讓技術服務於藝術，讓API成為你的創意工具！** 🎭✨ 