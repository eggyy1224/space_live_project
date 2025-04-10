const fs = require('fs');
const path = require('path');

// --- 配置路徑 ---
// 動畫目錄相對於腳本的位置
const animationsRelativeDir = '../prototype/frontend/public/animations';
// 共享配置文件輸出位置相對於腳本的位置
const outputRelativePath = '../prototype/shared/config/animations.json'; // *** 確保這個目錄存在 ***
// ----------------

const animationsDir = path.resolve(__dirname, animationsRelativeDir);
const outputPath = path.resolve(__dirname, outputRelativePath);

console.log(`Scanning directory: ${animationsDir}`);
console.log(`Outputting config to: ${outputPath}`);

// 提取友好名稱的函數 (與 animationUtils.ts 邏輯保持一致)
function getFriendlyAnimationName(filename) {
  const nameWithoutSuffix = filename
    .replace(/_animation\.glb$/i, '') // 移除 "_animation.glb"
    .replace(/\.glb$/i, '');          // 移除 ".glb"
  return nameWithoutSuffix || filename; // Fallback to filename if empty
}

try {
  // 確保動畫目錄存在
  if (!fs.existsSync(animationsDir)) {
    throw new Error(`動畫目錄未找到: ${animationsDir}`);
  }

  const files = fs.readdirSync(animationsDir);
  const animationConfig = {};

  files.forEach(file => {
    // 只處理 .glb 文件，忽略隱藏文件如 .DS_Store
    if (path.extname(file).toLowerCase() === '.glb' && !file.startsWith('.')) {
      const friendlyName = getFriendlyAnimationName(file);
      // 確保友好名稱有效 (非空)
      if (!friendlyName) {
         console.warn(`警告：無法從文件 "${file}" 生成有效的友好名稱。已跳過。`);
         return;
      }
      const frontendPath = `/animations/${file}`; // 前端使用的公開路徑

      if (animationConfig[friendlyName]) {
        console.warn(`警告：發現重複的友好名稱 "${friendlyName}" (來自文件 ${file} 和 ${path.basename(animationConfig[friendlyName].path)})。後者將被覆蓋！請檢查命名。`);
      }

      // 基礎描述，可以後續手動編輯 JSON 文件補充
      let description = `Animation for ${friendlyName}.`;
      if (friendlyName === 'Idle') description = "角色的自然待機動作";
      if (friendlyName === 'SwingToLand') description = "輕盈降落的動作";
      if (friendlyName === 'SneakWalk') description = "悄悄行走的動作";


      animationConfig[friendlyName] = {
        path: frontendPath,
        description: description
      };
      console.log(`  發現動畫: ${file} -> 友好名稱: ${friendlyName}, 路徑: ${frontendPath}`);
    } else {
      console.log(`  忽略文件: ${file}`);
    }
  });

  // 確保輸出目錄存在
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });

  // 寫入 JSON 文件
  fs.writeFileSync(outputPath, JSON.stringify(animationConfig, null, 2), 'utf-8'); // 使用 null, 2 格式化輸出
  console.log(`✅ 成功生成動畫配置文件: ${outputPath}`);
  console.log(`   包含 ${Object.keys(animationConfig).length} 個動畫。`);

} catch (error) {
  console.error(`❌ 處理動畫時發生錯誤: ${error.message}`);
  console.error(error.stack); // 打印更詳細的錯誤堆棧
  process.exit(1); // 以錯誤碼退出
} 