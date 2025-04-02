import React, { useState, useEffect } from 'react';
import { analyzeModel, ModelAnalysisResult, compareModels, downloadAnalysisAsJson } from '../utils/ModelAnalyzer';

interface ModelAnalyzerToolProps {
  availableModels?: string[];
}

const ModelAnalyzerTool: React.FC<ModelAnalyzerToolProps> = ({ 
  availableModels = ['/models/mixamowomanwithface.glb', '/models/headonly.glb'] 
}) => {
  const [selectedModel1, setSelectedModel1] = useState<string>(availableModels[0]);
  const [selectedModel2, setSelectedModel2] = useState<string>(availableModels[1]);
  const [model1Analysis, setModel1Analysis] = useState<ModelAnalysisResult | null>(null);
  const [model2Analysis, setModel2Analysis] = useState<ModelAnalysisResult | null>(null);
  const [comparison, setComparison] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  
  // 分析選定的模型
  const analyzeSelectedModels = async () => {
    setLoading(true);
    setError('');
    
    try {
      // 分析第一個模型
      const analysis1 = await analyzeModel(selectedModel1);
      setModel1Analysis(analysis1);
      
      // 如果選擇了第二個模型，也分析它
      if (selectedModel2) {
        const analysis2 = await analyzeModel(selectedModel2);
        setModel2Analysis(analysis2);
        
        // 比較兩個模型
        const comparisonResult = compareModels(analysis1, analysis2);
        setComparison(comparisonResult);
      } else {
        setModel2Analysis(null);
        setComparison('');
      }
    } catch (err) {
      let errorMessage = '分析模型時發生錯誤';
      if (err instanceof Error) {
        errorMessage = err.message;
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };
  
  // 下載分析結果
  const downloadAnalysis = (analysis: ModelAnalysisResult | null) => {
    if (analysis) {
      downloadAnalysisAsJson(analysis);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.9)',
      color: 'white',
      padding: '20px',
      zIndex: 1000,
      overflowY: 'auto',
      display: 'flex',
      flexDirection: 'column',
      fontFamily: 'monospace'
    }}>
      <h2>3D模型分析工具</h2>
      
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <div>
          <label>
            模型 1:
            <select 
              value={selectedModel1} 
              onChange={(e) => setSelectedModel1(e.target.value)}
              style={{ margin: '0 10px' }}
            >
              {availableModels.map(model => (
                <option key={model} value={model}>{model.split('/').pop()}</option>
              ))}
            </select>
          </label>
        </div>
        
        <div>
          <label>
            模型 2:
            <select 
              value={selectedModel2} 
              onChange={(e) => setSelectedModel2(e.target.value)}
              style={{ margin: '0 10px' }}
            >
              <option value="">不選擇</option>
              {availableModels.map(model => (
                <option key={model} value={model}>{model.split('/').pop()}</option>
              ))}
            </select>
          </label>
        </div>
        
        <button 
          onClick={analyzeSelectedModels}
          disabled={loading || !selectedModel1}
          style={{
            padding: '5px 15px',
            backgroundColor: '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'wait' : 'pointer'
          }}
        >
          {loading ? '分析中...' : '分析模型'}
        </button>
      </div>
      
      {error && (
        <div style={{ color: '#ff6b6b', marginBottom: '10px' }}>
          錯誤: {error}
        </div>
      )}
      
      <div style={{ display: 'flex', flexGrow: 1, gap: '20px' }}>
        {/* 模型1分析結果 */}
        <div style={{ flex: 1, maxHeight: '100%', overflowY: 'auto' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>模型 1 分析結果</h3>
            {model1Analysis && (
              <button 
                onClick={() => downloadAnalysis(model1Analysis)}
                style={{
                  padding: '5px 10px',
                  backgroundColor: '#2196F3',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                下載JSON
              </button>
            )}
          </div>
          
          {model1Analysis ? (
            <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12px' }}>
              文件名: {model1Analysis.fileName}
              網格總數: {model1Analysis.totalMeshes}
              蒙皮網格數: {model1Analysis.totalSkinnedMeshes}
              骨骼數: {model1Analysis.totalBones}
              動畫數: {model1Analysis.totalAnimations}
              動畫名稱: {model1Analysis.animationNames.join(', ')}
              有無Morph Targets: {model1Analysis.hasMorphTargets ? '有' : '無'}
              Morph Target數量: {model1Analysis.morphTargetCount}
              Morph Target名稱: {model1Analysis.morphTargetNames.join(', ')}
              
              模型層級結構:
              {model1Analysis.hierarchy}
            </pre>
          ) : (
            <p>尚未分析模型...</p>
          )}
        </div>
        
        {/* 模型2分析結果 */}
        {selectedModel2 && (
          <div style={{ flex: 1, maxHeight: '100%', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3>模型 2 分析結果</h3>
              {model2Analysis && (
                <button 
                  onClick={() => downloadAnalysis(model2Analysis)}
                  style={{
                    padding: '5px 10px',
                    backgroundColor: '#2196F3',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  下載JSON
                </button>
              )}
            </div>
            
            {model2Analysis ? (
              <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12px' }}>
                文件名: {model2Analysis.fileName}
                網格總數: {model2Analysis.totalMeshes}
                蒙皮網格數: {model2Analysis.totalSkinnedMeshes}
                骨骼數: {model2Analysis.totalBones}
                動畫數: {model2Analysis.totalAnimations}
                動畫名稱: {model2Analysis.animationNames.join(', ')}
                有無Morph Targets: {model2Analysis.hasMorphTargets ? '有' : '無'}
                Morph Target數量: {model2Analysis.morphTargetCount}
                Morph Target名稱: {model2Analysis.morphTargetNames.join(', ')}
                
                模型層級結構:
                {model2Analysis.hierarchy}
              </pre>
            ) : (
              <p>尚未分析模型...</p>
            )}
          </div>
        )}
      </div>
      
      {/* 比較結果 */}
      {comparison && (
        <div style={{ marginTop: '20px' }}>
          <h3>模型比較結果</h3>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12px' }}>
            {comparison}
          </pre>
        </div>
      )}
      
      <button 
        onClick={() => window.history.back()}
        style={{
          position: 'fixed',
          top: '10px',
          right: '10px',
          padding: '5px 15px',
          backgroundColor: '#ff6b6b',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        關閉
      </button>
    </div>
  );
};

export default ModelAnalyzerTool; 