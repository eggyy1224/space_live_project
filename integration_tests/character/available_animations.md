# 角色控制可用選項參考

## 📋 可用動畫列表

根據 `docs/model_data/character0611.glb_analysis.json` 分析，以下是角色模型中實際可用的動畫：

### 🎭 動畫名稱 (共13個)
1. **運動1** - 運動動畫1
2. **運動2** - 運動動畫2  
3. **漂浮** - 漂浮動畫
4. **漂浮2** - 漂浮動畫2
5. **Tpose** - T-pose 待機姿勢
6. **不穩** - 不穩定動畫
7. **划手機** - 划手機動畫
8. **臥躺** - 臥躺動畫
9. **舞步1** - 舞蹈動畫1
10. **舞步2** - 舞蹈動畫2
11. **舞步3** - 舞蹈動畫3
12. **飛1** - 飛行動畫1
13. **飛2** - 飛行動畫2

## 👗 服裝 Morph Targets

### outfit_shoes030_1 相關的變形目標
這些是實際可用於服裝控制的 morph targets：

1. **鍵 1** - 主要服裝變形
2. **錯置** - 服裝錯置效果
3. **錯置.001** - 服裝錯置效果變體

### 使用範例

#### 動畫控制 API 請求
```json
{
  "animation": "舞步1",
  "loop": true,
  "speed": 1.0
}
```

#### 服裝控制 API 請求
```json
{
  "outfit_morphs": {
    "鍵 1": 0.8,
    "錯置": 0.5,
    "錯置.001": 0.3
  }
}
```

## 📊 其他 Morph Targets

模型還包含126個 morph targets，主要用於面部表情控制：

### 面部表情相關
- 眉毛控制：`browDownLeft`, `browDownRight`, `browInnerUp`, `browOuterUpLeft`, `browOuterUpRight`
- 眼部控制：`eyeBlinkLeft`, `eyeBlinkRight`, `eyeLookDownLeft`, `eyeLookDownRight`, 等
- 嘴部控制：`mouthClose`, `mouthSmileLeft`, `mouthSmileRight`, `mouthFunnel`, 等
- 面頰控制：`cheekPuff`, `cheekSquintLeft`, `cheekSquintRight`

### 語音同步相關
- 音素：`CH`, `DD`, `E`, `FF`, `PP`, `RR`, `SS`, `TH`, `aa`, `ih`, `kk`, `nn`, `oh`, `ou`, `sil`

### 其他
- 頭髮：`hair01`
- 鼻子：`noseSneerLeft`, `noseSneerRight`
- 下巴：`jawForward`, `jawLeft`, `jawOpen`, `jawRight`

## 🎯 測試建議

### 推薦的動畫測試組合
1. **基礎動畫**：`Tpose` → `運動1` → `漂浮`
2. **舞蹈序列**：`舞步1` → `舞步2` → `舞步3`
3. **特殊動畫**：`划手機` → `臥躺` → `不穩`
4. **飛行動畫**：`飛1` → `飛2`

### 推薦的服裝測試組合
1. **經典款**：`{"鍵 1": 1.0, "錯置": 0.0, "錯置.001": 0.0}`
2. **混搭款**：`{"鍵 1": 0.6, "錯置": 0.4, "錯置.001": 0.2}`
3. **前衛款**：`{"鍵 1": 0.2, "錯置": 0.8, "錯置.001": 0.9}`
4. **平衡款**：`{"鍵 1": 0.5, "錯置": 0.5, "錯置.001": 0.5}`

## ⚠️ 注意事項

1. **動畫名稱**：必須使用確切的中文名稱（如 "舞步1"），不是英文翻譯
2. **服裝控制**：morph target 值範圍為 0.0 到 1.0
3. **縮放控制**：縮放值範圍為 0.1 到 15.0
4. **API 端點**：使用 `/api/control/character/animation` 和 `/api/control/character/outfit`
5. **WebSocket**：所有變更都會通過 WebSocket 即時推送到前端

## 🔗 相關文件

- 模型分析：`docs/model_data/character0611.glb_analysis.json`
- API 文檔：`docs/backend/cursor_api_control_response_guidelines.md`
- 測試文件：`integration_tests/character/`
- 前端組件：`prototype/frontend/src/components/CharacterControlPanel.tsx` 