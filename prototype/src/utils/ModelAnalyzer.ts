import * as THREE from 'three';
import { GLTF, GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

// 模型分析結果接口
export interface ModelAnalysisResult {
  fileName: string;
  totalMeshes: number;
  totalSkinnedMeshes: number;
  totalBones: number;
  totalAnimations: number;
  animationNames: string[];
  hasMorphTargets: boolean;
  morphTargetCount: number;
  morphTargetNames: string[];
  hierarchy: string;
}

/**
 * 分析GLB/GLTF模型文件的結構和內容
 * @param url 模型URL
 * @returns Promise<ModelAnalysisResult> 包含模型分析結果的Promise
 */
export function analyzeModel(url: string): Promise<ModelAnalysisResult> {
  return new Promise((resolve, reject) => {
    // 創建加載器
    const loader = new GLTFLoader();
    
    // 加載模型
    loader.load(
      url,
      (gltf: GLTF) => {
        // 初始化結果
        const result: ModelAnalysisResult = {
          fileName: url.split('/').pop() || 'unknown',
          totalMeshes: 0,
          totalSkinnedMeshes: 0,
          totalBones: 0,
          totalAnimations: gltf.animations.length,
          animationNames: gltf.animations.map(a => a.name),
          hasMorphTargets: false,
          morphTargetCount: 0,
          morphTargetNames: [],
          hierarchy: ''
        };
        
        // 處理骨骼骨架
        const skeletons: THREE.Skeleton[] = [];
        
        // 構建層次結構的字符串表示
        let hierarchyString = '';
        
        // 遞歸函數來構建層次結構
        function processNode(node: THREE.Object3D, depth: number): void {
          const indent = '  '.repeat(depth);
          hierarchyString += `${indent}- ${node.name || '未命名'} (${node.type})\n`;
          
          // 檢查是否是Mesh或SkinnedMesh
          if (node instanceof THREE.Mesh) {
            result.totalMeshes++;
            
            if (node instanceof THREE.SkinnedMesh) {
              result.totalSkinnedMeshes++;
              
              // 檢查骨骼
              if (node.skeleton && !skeletons.includes(node.skeleton)) {
                skeletons.push(node.skeleton);
                result.totalBones += node.skeleton.bones.length;
              }
            }
            
            // 檢查是否有Morph Targets
            const meshWithMorphs = node as {
              morphTargetDictionary?: {[key: string]: number};
              morphTargetInfluences?: number[];
            };
            
            if (meshWithMorphs.morphTargetDictionary && meshWithMorphs.morphTargetInfluences) {
              result.hasMorphTargets = true;
              
              const targets = Object.keys(meshWithMorphs.morphTargetDictionary);
              result.morphTargetCount += targets.length;
              
              // 添加這個網格的morph target名稱
              result.morphTargetNames = [
                ...result.morphTargetNames,
                ...targets
              ];
              
              // 添加morph target詳情到層次結構
              hierarchyString += `${indent}  Morph targets: ${targets.join(', ')}\n`;
            }
          }
          
          // 處理子節點
          node.children.forEach(child => {
            processNode(child, depth + 1);
          });
        }
        
        // 開始處理場景
        processNode(gltf.scene, 0);
        
        // 確保morphTargetNames不包含重複項
        result.morphTargetNames = Array.from(new Set(result.morphTargetNames));
        
        // 設置層次結構
        result.hierarchy = hierarchyString;
        
        // 解析完成
        resolve(result);
      },
      // 進度回調
      (xhr: ProgressEvent) => {
        // 可以添加加載進度邏輯
      },
      // 錯誤回調
      (error: unknown) => {
        let errorMessage = '未知錯誤';
        if (error instanceof Error) {
          errorMessage = error.message;
        } else if (typeof error === 'string') {
          errorMessage = error;
        } else if (error && typeof error === 'object' && 'message' in error) {
          errorMessage = String((error as { message: unknown }).message);
        }
        reject(new Error(`模型加載錯誤: ${errorMessage}`));
      }
    );
  });
}

/**
 * 比較兩個模型的分析結果
 * @param model1 第一個模型的分析結果
 * @param model2 第二個模型的分析結果
 * @returns 包含比較結果的字符串
 */
export function compareModels(model1: ModelAnalysisResult, model2: ModelAnalysisResult): string {
  let comparison = `模型比較: ${model1.fileName} vs ${model2.fileName}\n\n`;
  
  // 比較網格數量
  comparison += `網格數量: ${model1.totalMeshes} vs ${model2.totalMeshes}\n`;
  comparison += `蒙皮網格數量: ${model1.totalSkinnedMeshes} vs ${model2.totalSkinnedMeshes}\n`;
  comparison += `骨骼數量: ${model1.totalBones} vs ${model2.totalBones}\n`;
  
  // 比較動畫
  comparison += `動畫數量: ${model1.totalAnimations} vs ${model2.totalAnimations}\n`;
  
  // 比較動畫名稱
  comparison += '\n動畫比較:\n';
  const commonAnimations = model1.animationNames.filter(name => 
    model2.animationNames.includes(name)
  );
  const uniqueToModel1 = model1.animationNames.filter(name => 
    !model2.animationNames.includes(name)
  );
  const uniqueToModel2 = model2.animationNames.filter(name => 
    !model1.animationNames.includes(name)
  );
  
  comparison += `共有動畫: ${commonAnimations.length}\n`;
  if (commonAnimations.length > 0) {
    comparison += `  ${commonAnimations.join(', ')}\n`;
  }
  
  comparison += `僅在 ${model1.fileName} 中: ${uniqueToModel1.length}\n`;
  if (uniqueToModel1.length > 0) {
    comparison += `  ${uniqueToModel1.join(', ')}\n`;
  }
  
  comparison += `僅在 ${model2.fileName} 中: ${uniqueToModel2.length}\n`;
  if (uniqueToModel2.length > 0) {
    comparison += `  ${uniqueToModel2.join(', ')}\n`;
  }
  
  // 比較Morph Targets
  comparison += '\nMorph Targets比較:\n';
  comparison += `${model1.fileName}: ${model1.hasMorphTargets ? '有' : '無'} Morph Targets (數量: ${model1.morphTargetCount})\n`;
  comparison += `${model2.fileName}: ${model2.hasMorphTargets ? '有' : '無'} Morph Targets (數量: ${model2.morphTargetCount})\n`;
  
  // 比較Morph Target名稱
  const commonMorphs = model1.morphTargetNames.filter(name => 
    model2.morphTargetNames.includes(name)
  );
  const uniqueToModel1Morphs = model1.morphTargetNames.filter(name => 
    !model2.morphTargetNames.includes(name)
  );
  const uniqueToModel2Morphs = model2.morphTargetNames.filter(name => 
    !model1.morphTargetNames.includes(name)
  );
  
  comparison += `共有Morph Targets: ${commonMorphs.length}\n`;
  if (commonMorphs.length > 0) {
    comparison += `  ${commonMorphs.join(', ')}\n`;
  }
  
  comparison += `僅在 ${model1.fileName} 中的Morph Targets: ${uniqueToModel1Morphs.length}\n`;
  if (uniqueToModel1Morphs.length > 0) {
    comparison += `  ${uniqueToModel1Morphs.join(', ')}\n`;
  }
  
  comparison += `僅在 ${model2.fileName} 中的Morph Targets: ${uniqueToModel2Morphs.length}\n`;
  if (uniqueToModel2Morphs.length > 0) {
    comparison += `  ${uniqueToModel2Morphs.join(', ')}\n`;
  }
  
  return comparison;
}

/**
 * 導出模型分析結果為JSON文件（在瀏覽器環境中）
 * @param analysis 模型分析結果
 */
export function downloadAnalysisAsJson(analysis: ModelAnalysisResult): void {
  const dataStr = JSON.stringify(analysis, null, 2);
  const dataUri = `data:application/json;charset=utf-8,${encodeURIComponent(dataStr)}`;
  
  const downloadAnchorNode = document.createElement('a');
  downloadAnchorNode.setAttribute('href', dataUri);
  downloadAnchorNode.setAttribute('download', `${analysis.fileName}_analysis.json`);
  document.body.appendChild(downloadAnchorNode);
  downloadAnchorNode.click();
  downloadAnchorNode.remove();
} 