# Character Animation Mix API

## 📋 功能概述

角色動畫混合 API 允許同時播放多個動畫並控制它們的權重，實現平滑的動畫混合效果。這是對原有單一動畫系統的擴展，完全兼容現有的操控介面。

## 🚀 API 端點

### 單一動畫控制（現有功能）
```http
POST /api/control/character/animation
Content-Type: application/json

{
  "animation": "運動1",
  "loop": true,
  "speed": 1.0
}
```

### 動畫混合控制（新功能）
```http
POST /api/control/character/animation-mix
Content-Type: application/json

{
  "animations": [
    {
      "name": "運動1",
      "weight": 0.7,
      "loop": true,
      "speed": 1.0
    },
    {
      "name": "舞步1", 
      "weight": 0.3,
      "loop": true,
      "speed": 1.2
    }
  ],
  "transitionDuration": 0.5,
  "blendMode": "normal"
}
```

## 📋 參數說明

### 動畫配置對象
| 參數 | 類型 | 必需 | 說明 |
|------|------|------|------|
| `name` | string | ✅ | 動畫名稱（必須是有效的角色動畫） |
| `weight` | number | ✅ | 動畫權重 (0.0-1.0) |
| `loop` | boolean | ❌ | 是否循環播放，預設 `true` |
| `speed` | number | ❌ | 播放速度倍率，預設 `1.0` |

### 混合配置
| 參數 | 類型 | 必需 | 說明 |
|------|------|------|------|
| `animations` | array | ✅ | 動畫配置對象陣列 |
| `transitionDuration` | number | ❌ | 切換到混合模式的過渡時間，預設 `0.5` 秒 |
| `blendMode` | string | ❌ | 混合模式：`normal`/`additive`/`override`，預設 `normal` |

## 🎭 使用範例

### 1. 基本動畫混合
```bash
curl -X POST http://localhost:8000/api/control/character/animation-mix \
  -H 'Content-Type: application/json' \
  -d '{
    "animations": [
      {"name": "運動1", "weight": 0.6},
      {"name": "漂浮", "weight": 0.4}
    ]
  }'
```

### 2. 舞蹈組合混合
```bash
curl -X POST http://localhost:8000/api/control/character/animation-mix \
  -H 'Content-Type: application/json' \
  -d '{
    "animations": [
      {"name": "舞步1", "weight": 0.5, "speed": 1.2},
      {"name": "舞步2", "weight": 0.3, "speed": 0.8},
      {"name": "舞步3", "weight": 0.2, "speed": 1.0}
    ],
    "blendMode": "normal",
    "transitionDuration": 1.0
  }'
```

### 3. 情緒表達混合
```bash
curl -X POST http://localhost:8000/api/control/character/animation-mix \
  -H 'Content-Type: application/json' \
  -d '{
    "animations": [
      {"name": "Tpose", "weight": 0.8},
      {"name": "不穩", "weight": 0.2}
    ]
  }'
```

## 💡 最佳實踐

### 權重分配建議
- **主動畫**：權重 0.6-0.8，提供主要動作
- **輔助動畫**：權重 0.2-0.4，增加細節變化
- **總權重**：建議保持在 1.0 左右，避免超過 1.1

### 混合組合推薦
1. **運動 + 漂浮**：模擬太空中的運動效果
2. **舞步組合**：創造複雜的舞蹈動作
3. **基礎姿勢 + 微動作**：增加角色的生動性

### 性能考量
- 同時播放的動畫建議不超過 3-4 個
- 使用適當的 `transitionDuration` 避免突兀的切換
- 定期清理不需要的動畫混合

## 🔄 前端集成

前端會自動處理動畫混合，並提供實時權重調整功能：

```javascript
// 透過 CharacterService 使用
const { playAnimationMix, stopAnimationMix, adjustAnimationWeight } = useCharacterService();

// 播放混合
playAnimationMix([
  { name: "運動1", weight: 0.7 },
  { name: "舞步1", weight: 0.3 }
]);

// 動態調整權重
adjustAnimationWeight("運動1", 0.5);

// 停止混合
stopAnimationMix();
```

## 🔧 故障排除

### 常見問題
1. **動畫不存在**：確保動畫名稱在可用列表中
2. **權重總和過大**：檢查所有權重之和是否合理
3. **效果不明顯**：調整權重比例，確保有主次之分

### 調試建議
- 使用前端控制面板的動畫混合界面進行測試
- 檢查瀏覽器控制台的日誌輸出
- 從簡單的兩個動畫混合開始測試

## 📈 擴展功能（計劃中）

1. **動態權重變化**：支援權重隨時間自動變化
2. **層級混合**：支援多層次的動畫混合
3. **預設混合組合**：提供常用的動畫混合預設 