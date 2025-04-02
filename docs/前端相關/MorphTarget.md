# Three.js 與 Morph Target 技術研究

## Morph Target 基本概念

Morph Target（在Blender中稱為Shape Keys）是一種3D動畫技術，允許模型在不同形狀之間平滑過渡。對於虛擬太空人專案，這項技術將用於實現臉部表情變化。

### 工作原理

- 每個頂點在網格中，每個morph target儲存該頂點的新位置或相對於原始位置的偏移量
- "應用"morph target意味著Three.js將頂點從其基本位置移動到變形後的位置
- 可以同時應用多個morph target，並控制每個target的影響程度（0-1之間的值）

### 在Blender中創建與導出

1. 在Blender中創建基本模型
2. 添加Shape Keys（Blender中的Morph Target）
3. 修改模型創建不同的表情或形狀
4. 導出為glTF/GLB格式，確保包含Shape Keys

### 在Three.js中使用

```javascript
// 載入帶有morph targets的模型
const loader = new GLTFLoader();
loader.load('astronaut.glb', (gltf) => {
  const model = gltf.scene;
  
  // 找到包含morph targets的網格
  let morphMesh;
  model.traverse((object) => {
    if (object.isMesh && object.morphTargetInfluences) {
      morphMesh = object;
    }
  });
  
  if (morphMesh) {
    // 設置特定morph target的影響值（0-1）
    // 例如：設置"微笑"表情的影響值為0.5
    const smileIndex = morphMesh.morphTargetDictionary['smile'];
    if (smileIndex !== undefined) {
      morphMesh.morphTargetInfluences[smileIndex] = 0.5;
    }
    
    // 動畫過渡到另一個表情
    function animateToExpression(expressionName, targetValue, duration) {
      const index = morphMesh.morphTargetDictionary[expressionName];
      if (index !== undefined) {
        const startValue = morphMesh.morphTargetInfluences[index];
        const startTime = Date.now();
        
        function animate() {
          const elapsed = Date.now() - startTime;
          const progress = Math.min(elapsed / duration, 1);
          
          // 使用緩動函數使過渡更自然
          const easeProgress = progress * (2 - progress);
          morphMesh.morphTargetInfluences[index] = startValue + (targetValue - startValue) * easeProgress;
          
          if (progress < 1) {
            requestAnimationFrame(animate);
          }
        }
        
        animate();
      }
    }
    
    // 使用範例：將"驚訝"表情從0過渡到1，持續1秒
    animateToExpression('surprised', 1.0, 1000);
  }
});
```

## 與語音同步的表情動畫

為了實現虛擬太空人說話時的嘴型同步，可以結合語音分析和Morph Target：

```javascript
// 假設我們有語音API提供的音素時間軸
function syncLipWithSpeech(audioData, morphMesh) {
  // 音素到morph target的映射
  const phonemeToMorph = {
    'A': 'mouthOpen',
    'O': 'mouthRound',
    'E': 'mouthWide',
    // 更多音素映射...
  };
  
  // 處理每個音素
  audioData.phonemes.forEach(phoneme => {
    const morphName = phonemeToMorph[phoneme.sound];
    if (morphName) {
      const morphIndex = morphMesh.morphTargetDictionary[morphName];
      
      // 在正確的時間設置morph target
      setTimeout(() => {
        // 設置morph target影響值
        morphMesh.morphTargetInfluences[morphIndex] = phoneme.intensity;
        
        // 設置持續時間後恢復
        setTimeout(() => {
          morphMesh.morphTargetInfluences[morphIndex] = 0;
        }, phoneme.duration);
      }, phoneme.startTime);
    }
  });
}
```

## 結合情感分析的表情生成

結合Gemini API的情感分析，可以自動生成適合對話情境的表情：

```javascript
async function generateExpressionFromText(text, morphMesh) {
  // 使用Gemini API分析文本情感
  const emotionAnalysis = await analyzeEmotionWithGemini(text);
  
  // 根據情感分析結果設置表情
  if (emotionAnalysis.joy > 0.7) {
    animateToExpression('smile', emotionAnalysis.joy, 500);
  } else if (emotionAnalysis.sadness > 0.5) {
    animateToExpression('sad', emotionAnalysis.sadness, 500);
  } else if (emotionAnalysis.surprise > 0.6) {
    animateToExpression('surprised', emotionAnalysis.surprise, 300);
  }
  // 更多情感映射...
}

// Gemini API情感分析函數
async function analyzeEmotionWithGemini(text) {
  // 實際實現將調用Gemini API
  // 返回情感分析結果
  return {
    joy: 0.8,
    sadness: 0.1,
    anger: 0.0,
    surprise: 0.2,
    // 其他情感...
  };
}
```

## 技術挑戰與解決方案

1. **Blender導出問題**：確保在Blender中正確設置Shape Keys，並使用最新的glTF導出器
2. **表情自然度**：使用多個Morph Target的組合，而不是單一表情
3. **性能優化**：限制同時活躍的Morph Target數量，使用LOD（Level of Detail）技術
4. **語音同步精確度**：使用音素級別的分析，而不僅僅是單詞級別
