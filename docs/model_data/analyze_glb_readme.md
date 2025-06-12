# GLB 模型分析工具使用說明

## 📋 概述

`analyze_glb_model.js` 是一個通用的 GLB 3D 模型分析工具，能夠詳細分析模型的結構、動畫、Morph Targets 等資訊，並輸出為 JSON 格式。

## 🚀 使用方法

### 基本語法
```bash
node analyze_glb_model.js <模型檔案路徑> [輸出檔案路徑]
```

### 使用範例

#### 1. 分析並保存到 JSON 檔案
```bash
node analyze_glb_model.js "./prototype/frontend/public/models/新頭.glb" "./docs/model_data/新頭.glb_analysis.json"
```

#### 2. 只分析不保存（輸出到控制台）
```bash
node analyze_glb_model.js "./prototype/frontend/public/models/character0611.glb"
```

#### 3. 批量分析多個模型
```bash
# 新頭模型
node analyze_glb_model.js "./prototype/frontend/public/models/新頭.glb" "./docs/model_data/新頭.glb_analysis.json"

# 全身角色模型
node analyze_glb_model.js "./prototype/frontend/public/models/character0611.glb" "./docs/model_data/character0611.glb_analysis.json"

# 其他模型...
node analyze_glb_model.js "./prototype/frontend/public/models/armature001_model.glb" "./docs/model_data/armature001_model.glb_analysis.json"
```

## 📊 輸出內容

### JSON 結構說明

```json
{
  "fileName": "模型檔案名稱",
  "totalMeshes": "網格總數",
  "totalSkinnedMeshes": "蒙皮網格總數",
  "totalBones": "骨骼總數",
  "totalAnimations": "動畫總數",
  "animationNames": ["動畫名稱列表"],
  "hasMorphTargets": "是否包含變形目標",
  "morphTargetCount": "變形目標總數",
  "morphTargetNames": ["所有變形目標名稱列表"],
  "meshDetails": [
    {
      "index": "網格索引",
      "name": "網格名稱",
      "primitiveCount": "基元數量",
      "totalMorphTargets": "該網格的變形目標總數",
      "morphTargetsByPrimitive": [
        {
          "index": "基元索引",
          "attributes": ["基元屬性列表"],
          "morphTargetCount": "該基元的變形目標數量",
          "morphTargetNames": ["該基元的變形目標名稱"]
        }
      ],
      "morphTargetNames": ["該網格所有變形目標名稱"]
    }
  ],
  "hierarchy": "場景層次結構字符串"
}
```

### 詳細分析資訊

腳本會提供以下詳細資訊：

1. **基本檔案資訊**
   - 檔案大小
   - 建立/修改時間
   - GLB 版本

2. **3D 模型結構**
   - 場景、節點、網格數量
   - 材質、貼圖數量
   - 皮膚系統資訊

3. **網格詳細分析**
   - 每個網格的基元資訊
   - 網格屬性（位置、法線、UV 等）
   - 詳細的 Morph Target 列表

4. **動畫資訊**
   - 動畫名稱列表
   - 每個動畫的通道數和採樣器數

5. **按網格分組的 Morph Targets**
   - 各網格包含的變形目標詳情
   - 適合用於 LipSync 和表情控制

## 🎯 實際應用

### 1. 臉部表情控制
根據分析結果，可以知道：
- **AvatarHead.003/005/007**: 主要臉部變形網格
- 包含眼部、嘴部、眉毛等表情控制
- LipSync 專用的語音形狀（CH, DD, E, FF 等）

### 2. 動畫系統
- 獲取所有可用動畫名稱
- 了解動畫複雜度（通道數、採樣器數）

### 3. 模型優化
- 檢查網格數量和複雜度
- 評估 Morph Target 使用情況
- 骨骼系統分析

## 🔧 腳本功能特色

- ✅ **通用性**: 可分析任何 GLB 檔案
- ✅ **詳細分析**: 包含完整的網格和 Morph Target 資訊
- ✅ **靈活輸出**: 可選擇保存到檔案或輸出到控制台
- ✅ **中文支援**: 完整支援中文檔案名和內容
- ✅ **錯誤處理**: 包含完善的錯誤檢查機制
- ✅ **可重複使用**: 一次建立，多次使用

## 📝 注意事項

1. 確保 Node.js 環境已安裝
2. 檔案路徑使用相對路徑或絕對路徑皆可
3. 輸出目錄不存在時會自動建立
4. 大型模型檔案可能需要較長分析時間

## 🚨 常見問題

### Q: 找不到檔案錯誤
**A**: 檢查檔案路徑是否正確，確保檔案存在

### Q: 無法寫入輸出檔案
**A**: 檢查輸出目錄權限，確保有寫入權限

### Q: 分析結果不完整
**A**: 確認 GLB 檔案格式正確且未損壞

---

**建立時間**: 2025年1月
**作者**: AI Assistant
**版本**: 1.0 