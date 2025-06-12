#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

/**
 * 通用 GLB 模型分析工具
 * 使用方法: node analyze_glb_model.js <模型檔案路徑> [輸出檔案路徑]
 * 範例: node analyze_glb_model.js "./models/新頭.glb" "./docs/model_data/新頭.glb_analysis.json"
 */

// 從 GLB 檔案中提取詳細的 GLTF 資訊
function analyzeGLBModel(filePath) {
    try {
        const fileBuffer = fs.readFileSync(filePath);
        const stats = fs.statSync(filePath);
        
        // 解析 GLB 檔案頭部
        const magic = fileBuffer.readUInt32LE(0);
        if (magic !== 0x46546C67) {
            throw new Error('不是有效的 GLB 檔案');
        }
        
        const version = fileBuffer.readUInt32LE(4);
        const length = fileBuffer.readUInt32LE(8);
        
        // 解析第一個 chunk (JSON)
        const firstChunkLength = fileBuffer.readUInt32LE(12);
        const firstChunkType = fileBuffer.readUInt32LE(16);
        
        if (firstChunkType !== 0x4E4F534A) { // JSON
            throw new Error('第一個 chunk 不是 JSON');
        }
        
        const jsonData = fileBuffer.subarray(20, 20 + firstChunkLength).toString('utf8');
        const gltfData = JSON.parse(jsonData);
        
        const fileName = path.basename(filePath);
        
        console.log(`=== 分析 ${fileName} ===`);
        console.log(`檔案大小: ${(fileBuffer.length / 1024 / 1024).toFixed(2)} MB`);
        console.log(`建立時間: ${stats.birthtime.toLocaleString()}`);
        console.log(`修改時間: ${stats.mtime.toLocaleString()}`);
        console.log(`GLB 版本: ${version}`);
        console.log(`場景數量: ${gltfData.scenes ? gltfData.scenes.length : 0}`);
        console.log(`節點數量: ${gltfData.nodes ? gltfData.nodes.length : 0}`);
        console.log(`網格數量: ${gltfData.meshes ? gltfData.meshes.length : 0}`);
        console.log(`材質數量: ${gltfData.materials ? gltfData.materials.length : 0}`);
        console.log(`貼圖數量: ${gltfData.textures ? gltfData.textures.length : 0}`);
        console.log(`動畫數量: ${gltfData.animations ? gltfData.animations.length : 0}`);
        console.log(`皮膚數量: ${gltfData.skins ? gltfData.skins.length : 0}`);
        
        // 分析結果
        const result = {
            fileName: fileName,
            totalMeshes: gltfData.meshes ? gltfData.meshes.length : 0,
            totalSkinnedMeshes: 0,
            totalBones: 0,
            totalAnimations: gltfData.animations ? gltfData.animations.length : 0,
            animationNames: gltfData.animations ? gltfData.animations.map(anim => anim.name || '未命名') : [],
            hasMorphTargets: false,
            morphTargetCount: 0,
            morphTargetNames: [],
            meshDetails: [], // 新增：每個網格的詳細資訊
            hierarchy: ""
        };
        
        // 統計骨骼數量
        if (gltfData.skins) {
            gltfData.skins.forEach(skin => {
                if (skin.joints) {
                    result.totalBones += skin.joints.length;
                }
            });
        }
        
        // 統計蒙皮網格數量
        let skinnedMeshCount = 0;
        if (gltfData.nodes) {
            gltfData.nodes.forEach(node => {
                if (node.mesh !== undefined && node.skin !== undefined) {
                    skinnedMeshCount++;
                }
            });
        }
        result.totalSkinnedMeshes = skinnedMeshCount;
        
        // 詳細分析每個網格的 morph targets
        const allMorphTargets = new Set();
        let totalMorphTargets = 0;
        
        if (gltfData.meshes) {
            console.log('\n=== 網格詳細分析 ===');
            
            gltfData.meshes.forEach((mesh, meshIndex) => {
                const meshDetail = {
                    index: meshIndex,
                    name: mesh.name || `未命名網格_${meshIndex}`,
                    primitiveCount: mesh.primitives ? mesh.primitives.length : 0,
                    totalMorphTargets: 0,
                    morphTargetsByPrimitive: [],
                    morphTargetNames: []
                };
                
                console.log(`\n網格 ${meshIndex}: ${meshDetail.name}`);
                
                if (mesh.primitives) {
                    mesh.primitives.forEach((primitive, pIndex) => {
                        const primitiveDetail = {
                            index: pIndex,
                            attributes: primitive.attributes ? Object.keys(primitive.attributes) : [],
                            morphTargetCount: primitive.targets ? primitive.targets.length : 0,
                            morphTargetNames: []
                        };
                        
                        console.log(`  基元 ${pIndex}:`);
                        console.log(`    屬性: ${primitiveDetail.attributes.join(', ')}`);
                        
                        if (primitive.targets && primitive.targets.length > 0) {
                            result.hasMorphTargets = true;
                            totalMorphTargets += primitive.targets.length;
                            meshDetail.totalMorphTargets += primitive.targets.length;
                            
                            console.log(`    Morph Targets: ${primitive.targets.length} 個`);
                            
                            // 檢查是否有 morph target 名稱
                            if (mesh.extras && mesh.extras.targetNames) {
                                // 取得對應這個基元的 target 名稱
                                const targetNames = mesh.extras.targetNames.slice(0, primitive.targets.length);
                                primitiveDetail.morphTargetNames = targetNames;
                                meshDetail.morphTargetNames = meshDetail.morphTargetNames.concat(targetNames);
                                
                                console.log(`    Target 名稱: ${targetNames.join(', ')}`);
                                targetNames.forEach(name => allMorphTargets.add(name));
                            } else {
                                // 如果沒有明確的名稱，生成預設名稱
                                for (let i = 0; i < primitive.targets.length; i++) {
                                    const defaultName = `${meshDetail.name}_target_${i}`;
                                    primitiveDetail.morphTargetNames.push(defaultName);
                                    meshDetail.morphTargetNames.push(defaultName);
                                    allMorphTargets.add(defaultName);
                                }
                                console.log(`    Target 名稱 (預設): ${primitiveDetail.morphTargetNames.join(', ')}`);
                            }
                        }
                        
                        meshDetail.morphTargetsByPrimitive.push(primitiveDetail);
                    });
                }
                
                // 去除重複的 morph target 名稱
                meshDetail.morphTargetNames = [...new Set(meshDetail.morphTargetNames)];
                result.meshDetails.push(meshDetail);
            });
        }
        
        result.morphTargetCount = totalMorphTargets;
        result.morphTargetNames = Array.from(allMorphTargets).sort();
        
        // 生成層次結構
        result.hierarchy = generateHierarchy(gltfData, result.meshDetails);
        
        // 顯示動畫資訊
        if (gltfData.animations && gltfData.animations.length > 0) {
            console.log('\n=== 動畫資訊 ===');
            gltfData.animations.forEach((anim, index) => {
                console.log(`動畫 ${index + 1}: ${anim.name || '未命名'}`);
                if (anim.channels) {
                    console.log(`  通道數: ${anim.channels.length}`);
                }
                if (anim.samplers) {
                    console.log(`  採樣器數: ${anim.samplers.length}`);
                }
            });
        }
        
        console.log('\n=== 最終統計 ===');
        console.log(`總網格數: ${result.totalMeshes}`);
        console.log(`蒙皮網格數: ${result.totalSkinnedMeshes}`);
        console.log(`骨骼數: ${result.totalBones}`);
        console.log(`變形目標總數: ${result.morphTargetCount}`);
        console.log(`動畫數: ${result.totalAnimations}`);
        
        // 按網格分組顯示 morph targets
        console.log('\n=== 按網格分組的 Morph Targets ===');
        result.meshDetails.forEach(meshDetail => {
            if (meshDetail.totalMorphTargets > 0) {
                console.log(`${meshDetail.name}: ${meshDetail.totalMorphTargets} 個`);
                console.log(`  名稱: ${meshDetail.morphTargetNames.join(', ')}`);
            }
        });
        
        return result;
        
    } catch (error) {
        console.error('分析檔案時發生錯誤:', error.message);
        return null;
    }
}

function generateHierarchy(gltfData, meshDetails) {
    let hierarchy = "- Scene (Group)\\n";
    
    if (gltfData.scenes && gltfData.scenes.length > 0) {
        const scene = gltfData.scenes[0];
        if (scene.nodes && gltfData.nodes) {
            scene.nodes.forEach(nodeIndex => {
                hierarchy += generateNodeHierarchy(gltfData, nodeIndex, 1, meshDetails);
            });
        }
    }
    
    return hierarchy;
}

function generateNodeHierarchy(gltfData, nodeIndex, depth, meshDetails) {
    const indent = "  ".repeat(depth);
    const node = gltfData.nodes[nodeIndex];
    let nodeInfo = `${indent}- ${node.name || 'Node_' + nodeIndex}`;
    
    // 判斷節點類型
    if (node.mesh !== undefined) {
        const mesh = gltfData.meshes[node.mesh];
        const meshDetail = meshDetails[node.mesh];
        
        if (node.skin !== undefined) {
            nodeInfo += " (SkinnedMesh)";
        } else {
            nodeInfo += " (Mesh)";
        }
        
        // 添加詳細的 morph targets 資訊
        if (meshDetail && meshDetail.totalMorphTargets > 0) {
            nodeInfo += `\\n${indent}  Morph targets: ${meshDetail.totalMorphTargets} 個`;
            if (meshDetail.morphTargetNames.length <= 10) {
                nodeInfo += ` (${meshDetail.morphTargetNames.join(', ')})`;
            } else {
                nodeInfo += ` (${meshDetail.morphTargetNames.slice(0, 10).join(', ')}...)`;
            }
        }
    } else if (gltfData.skins && gltfData.skins.some(skin => skin.joints && skin.joints.includes(nodeIndex))) {
        nodeInfo += " (Bone)";
    } else {
        nodeInfo += " (Object3D)";
    }
    
    nodeInfo += "\\n";
    
    // 處理子節點
    if (node.children && node.children.length > 0) {
        node.children.forEach(childIndex => {
            nodeInfo += generateNodeHierarchy(gltfData, childIndex, depth + 1, meshDetails);
        });
    }
    
    return nodeInfo;
}

// 主程式
function main() {
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.log('使用方法: node analyze_glb_model.js <模型檔案路徑> [輸出檔案路徑]');
        console.log('範例: node analyze_glb_model.js "./models/新頭.glb" "./docs/model_data/新頭.glb_analysis.json"');
        process.exit(1);
    }
    
    const modelPath = args[0];
    const outputPath = args[1];
    
    if (!fs.existsSync(modelPath)) {
        console.error(`錯誤: 找不到檔案 ${modelPath}`);
        process.exit(1);
    }
    
    const result = analyzeGLBModel(modelPath);
    
    if (result) {
        if (outputPath) {
            // 確保輸出目錄存在
            const outputDir = path.dirname(outputPath);
            if (!fs.existsSync(outputDir)) {
                fs.mkdirSync(outputDir, { recursive: true });
            }
            
            // 寫入檔案
            fs.writeFileSync(outputPath, JSON.stringify(result, null, 2), 'utf8');
            console.log(`\n✅ 分析完成！檔案已保存至: ${outputPath}`);
        } else {
            // 如果沒有指定輸出路徑，只顯示分析結果
            console.log('\n=== JSON 結果 ===');
            console.log(JSON.stringify(result, null, 2));
        }
    } else {
        console.error('❌ 分析失敗');
        process.exit(1);
    }
}

// 如果直接執行此檔案，則執行主程式
if (require.main === module) {
    main();
}

module.exports = { analyzeGLBModel }; 