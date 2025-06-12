# 角色控制整合測試

這個目錄包含了角色控制功能的完整整合測試，測試通過 WebSocket 和 REST API 來控制前端角色的各種屬性。

## 📋 測試文件說明

### `test_character_control_endpoints.py`
**全面的角色控制 API 端點測試**

測試功能包括：
- 🔍 **角色縮放控制** - 測試 0.1-15.0 範圍的縮放
- 📍 **位置控制** - 3D 座標移動 (X/Y/Z 軸)
- 🔄 **旋轉控制** - 3軸旋轉 (弧度制)
- 👗 **服裝控制** - outfit_shoes030_1 morph targets
- 🎭 **動畫控制** - 角色動畫播放
- 👁️ **可見性控制** - 角色顯示/隱藏
- 🔄 **變換重置** - 重置所有變換
- 📊 **狀態查詢** - 獲取角色當前狀態
- ❌ **錯誤處理** - 測試無效輸入的處理

### `test_outfit_morphtargets.py`
**outfit_shoes030_1 服裝變形專項測試**

專門測試服裝相關的 morph targets：
- 👗 **個別控制** - 測試 "鍵 1"、"錯置"、"錯置.001" 各自控制
- 🎨 **組合控制** - 測試多個 morph target 同時設置
- 📈 **漸進變形** - 展示平滑的變形過渡效果
- 🌊 **波浪變形** - 使用數學函數創建動態效果
- ⚡ **快速變化** - 測試系統響應性能
- 🎯 **預設組合** - 經典服裝配置組合
- 🔍 **極值測試** - 邊界值和錯誤處理

### `run_all_tests.py`
**測試套件運行器**

自動運行所有測試並生成報告：
- 🚀 **自動化執行** - 依序運行所有測試腳本
- 📊 **結果統計** - 統計通過/失敗數量
- 📝 **報告生成** - 自動生成 Markdown 測試報告
- ⏱️ **超時控制** - 防止測試無限等待
- 🔧 **錯誤處理** - 捕獲和報告運行錯誤

## 🚀 使用方法

### 前置要求

1. **啟動後端服務**：
   ```bash
   cd prototype/backend
   python main.py
   ```

2. **啟動前端服務**：
   ```bash
   cd prototype/frontend
   npm start
   ```

3. **確保 WebSocket 連接**：
   - 前端應該自動連接到 `ws://localhost:8000/ws`
   - 檢查瀏覽器控制台確認連接成功

### 運行測試

#### 運行所有測試（推薦）
```bash
cd integration_tests/character
python run_all_tests.py
```

#### 運行單個測試
```bash
# 基本功能測試
python test_character_control_endpoints.py

# 服裝專項測試
python test_outfit_morphtargets.py
```

### 查看測試結果

測試完成後會自動生成 `test_report.md` 文件，包含：
- 測試時間和總覽
- 每個測試的通過/失敗狀態
- 成功率統計
- 詳細的功能說明

## 📊 API 端點測試覆蓋

### 角色控制端點
| 端點 | 功能 | 測試覆蓋 |
|------|------|----------|
| `POST /api/control/character/scale` | 角色縮放 | ✅ 正常值、邊界值、無效值 |
| `POST /api/control/character/position` | 角色位置 | ✅ 6個方向移動、無效座標 |
| `POST /api/control/character/rotation` | 角色旋轉 | ✅ 3軸旋轉、複合旋轉、無效值 |
| `POST /api/control/character/outfit` | 服裝控制 | ✅ 單個/組合 morph、無效值 |
| `POST /api/control/character/animation` | 動畫控制 | ✅ 多種動畫、播放速度 |
| `POST /api/control/character/visibility` | 可見性 | ✅ 顯示/隱藏切換 |
| `POST /api/control/character/reset-transform` | 重置變換 | ✅ 各種重置組合 |
| `GET /api/control/character/status` | 狀態查詢 | ✅ 狀態信息返回 |

### WebSocket 消息測試
- ✅ `character-control` 消息類型
- ✅ 所有 action 類型 (scale, position, rotation, outfit, animation, visibility, reset-transform, get-status)
- ✅ payload 數據完整性驗證
- ✅ 響應時間測試

## 🔧 故障排除

### 常見問題

1. **連接失敗**
   ```
   ❌ 無法連接到後端，請確保後端服務正在運行
   ```
   **解決方案**：檢查後端服務是否在 `http://localhost:8000` 運行

2. **WebSocket 連接失敗**
   ```
   ConnectionRefusedError: [Errno 61] Connection refused
   ```
   **解決方案**：確保前端已啟動並連接到 WebSocket

3. **測試超時**
   ```
   ⏰ test_xxx.py 測試超時
   ```
   **解決方案**：檢查網絡連接或增加超時時間

4. **沒有活動連接**
   ```
   ⚠️ 警告: 沒有活動的前端連接
   ```
   **解決方案**：刷新前端頁面重新建立 WebSocket 連接

### 調試技巧

1. **查看詳細輸出**：
   ```bash
   python test_character_control_endpoints.py 2>&1 | tee test_output.log
   ```

2. **檢查後端狀態**：
   ```bash
   curl http://localhost:8000/api/control/status
   ```

3. **檢查 WebSocket 連接**：
   打開瀏覽器開發者工具，查看 Network > WS 標籤

## 🎯 測試重點

### 功能驗證
- ✅ API 端點響應正確
- ✅ 參數驗證有效
- ✅ WebSocket 消息格式正確
- ✅ 前端狀態更新及時

### 性能測試
- ✅ 快速連續請求處理
- ✅ WebSocket 響應時間
- ✅ 大量數據處理能力

### 錯誤處理
- ✅ 無效參數拒絕
- ✅ 範圍外數值處理
- ✅ 網絡異常恢復

## 📝 新增測試

要新增測試用例，請參考現有的測試結構：

1. **創建測試函數**：
   ```python
   async def test_new_feature(ws: websockets.WebSocketClientProtocol):
       # 測試邏輯
       pass
   ```

2. **在 main() 中調用**：
   ```python
   await test_new_feature(ws)
   ```

3. **更新 run_all_tests.py**：
   添加新的測試腳本到 `test_scripts` 列表

## 📞 支援

如果遇到問題或需要新增功能，請查看：
- 後端 API 文檔：`docs/backend/cursor_api_control_response_guidelines.md`
- 前端服務：`prototype/frontend/src/services/`
- WebSocket 處理：`prototype/frontend/src/services/WebSocketService.ts` 