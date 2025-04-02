import React, { useRef, useEffect, useState } from 'react';
import { useGLTF } from '@react-three/drei';
import * as THREE from 'three';

interface ModelDebuggerProps {
  url: string;
}

// 為THREE.Mesh擴展類型定義，添加可選的morphTargetDictionary和morphTargetInfluences
interface MeshWithMorphs extends THREE.Mesh {
  morphTargetDictionary?: {[key: string]: number};
  morphTargetInfluences?: number[];
}

interface SkinnedMeshWithMorphs extends THREE.SkinnedMesh {
  morphTargetDictionary?: {[key: string]: number};
  morphTargetInfluences?: number[];
}

const ModelDebugger: React.FC<ModelDebuggerProps> = ({ url }) => {
  const [debugInfo, setDebugInfo] = useState<string>('正在載入模型...');
  const { scene } = useGLTF(url);

  useEffect(() => {
    if (scene) {
      let info = `模型URL: ${url}\n\n`;
      info += `模型層級結構:\n`;
      
      const meshes: MeshWithMorphs[] = [];
      const skinnedMeshes: SkinnedMeshWithMorphs[] = [];
      
      scene.traverse((object) => {
        if (object.type === 'Mesh' || object.type === 'SkinnedMesh') {
          info += `- ${object.name || '未命名'} (${object.type})\n`;
          
          if (object instanceof THREE.SkinnedMesh) {
            skinnedMeshes.push(object as SkinnedMeshWithMorphs);
          } else if (object instanceof THREE.Mesh) {
            meshes.push(object as MeshWithMorphs);
          }
        }
      });
      
      info += `\n總共找到 ${meshes.length} 個標準網格和 ${skinnedMeshes.length} 個蒙皮網格\n\n`;
      
      // 詳細分析每個蒙皮網格
      if (skinnedMeshes.length > 0) {
        info += `蒙皮網格詳細信息:\n`;
        
        skinnedMeshes.forEach((mesh, index) => {
          info += `\n[SkinnedMesh ${index + 1}]: ${mesh.name || '未命名'}\n`;
          info += `- 是否有morphTargetDictionary: ${mesh.morphTargetDictionary ? '是' : '否'}\n`;
          info += `- 是否有morphTargetInfluences: ${mesh.morphTargetInfluences ? '是' : '否'}\n`;
          
          if (mesh.morphTargetDictionary) {
            const targets = Object.keys(mesh.morphTargetDictionary);
            info += `- MorphTarget數量: ${targets.length}\n`;
            info += `- MorphTarget名稱列表:\n`;
            targets.forEach(name => {
              const index = mesh.morphTargetDictionary![name];
              info += `  · ${name} (索引: ${index})\n`;
            });
          }
          
          if (mesh.morphTargetInfluences) {
            info += `- MorphTargetInfluences長度: ${mesh.morphTargetInfluences.length}\n`;
            info += `- 當前影響值:\n`;
            mesh.morphTargetInfluences.forEach((influence, i) => {
              let name = `未知目標 ${i}`;
              if (mesh.morphTargetDictionary) {
                const foundKey = Object.keys(mesh.morphTargetDictionary).find(
                  key => mesh.morphTargetDictionary![key] === i
                );
                if (foundKey) {
                  name = foundKey;
                }
              }
              info += `  · ${name}: ${influence}\n`;
            });
          }
          
          // 檢查骨骼和動畫
          if (mesh.skeleton) {
            info += `- 骨骼骨骼數: ${mesh.skeleton.bones.length}\n`;
          }
        });
      } else {
        info += `沒有找到蒙皮網格，檢查標準網格的MorphTargets:\n`;
        
        meshes.forEach((mesh, index) => {
          info += `\n[Mesh ${index + 1}]: ${mesh.name || '未命名'}\n`;
          info += `- 是否有morphTargetDictionary: ${mesh.morphTargetDictionary ? '是' : '否'}\n`;
          info += `- 是否有morphTargetInfluences: ${mesh.morphTargetInfluences ? '是' : '否'}\n`;
          
          if (mesh.morphTargetDictionary) {
            const targets = Object.keys(mesh.morphTargetDictionary);
            info += `- MorphTarget數量: ${targets.length}\n`;
            info += `- MorphTarget名稱列表: ${targets.join(', ')}\n`;
          }
        });
      }
      
      setDebugInfo(info);
    }
  }, [scene, url]);

  return (
    <div style={{ 
      position: 'absolute', 
      top: '10px', 
      left: '10px', 
      backgroundColor: 'rgba(0, 0, 0, 0.7)',
      color: 'white',
      padding: '10px',
      borderRadius: '5px',
      maxHeight: '80vh',
      overflowY: 'auto',
      zIndex: 1000,
      fontFamily: 'monospace',
      fontSize: '12px',
      whiteSpace: 'pre-wrap'
    }}>
      <h3>模型調試信息</h3>
      <button onClick={() => navigator.clipboard.writeText(debugInfo)}>
        複製調試信息
      </button>
      <pre>{debugInfo}</pre>
    </div>
  );
};

export default ModelDebugger; 