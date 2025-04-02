import React, { useEffect, useRef, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, useGLTF, useAnimations, Stars } from '@react-three/drei'
import * as THREE from 'three'
import './App.css'

// 太空背景組件
function SpaceBackground() {
  return (
    <>
      <color attach="background" args={['#000']} />
      <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
      <fog attach="fog" args={['#000', 20, 40]} />
    </>
  )
}

// 模型加載和動畫處理組件
function Model({ 
  url, 
  scale, 
  rotation, 
  position,
  currentAnimation,
  setAvailableAnimations
}: { 
  url: string, 
  scale: number,
  rotation: [number, number, number],
  position: [number, number, number],
  currentAnimation: string | null,
  setAvailableAnimations: (anims: string[]) => void
}) {
  const group = useRef<THREE.Group>(null!)
  const { scene, animations } = useGLTF(url)
  const { actions, mixer } = useAnimations(animations, group)
  
  // 更新可用動畫列表並設定預設動畫
  useEffect(() => {
    const animationNames = Object.keys(actions)
    console.log('可用動畫:', animationNames)
    setAvailableAnimations(animationNames)
  }, [actions, setAvailableAnimations])
  
  // 根據選擇播放動畫
  useEffect(() => {
    // 先停止所有動畫
    Object.values(actions).forEach(action => {
      if (action) action.stop()
    })
    
    // 播放選定的動畫
    if (currentAnimation && actions[currentAnimation]) {
      actions[currentAnimation]?.play()
    }
    
    return () => {
      if (mixer) mixer.stopAllAction()
    }
  }, [currentAnimation, actions, mixer])

  // 旋轉模型
  useFrame(() => {
    if (group.current) {
      group.current.rotation.y = rotation[1] 
    }
  })

  return (
    <group ref={group} position={position}>
      <primitive object={scene} scale={scale} />
    </group>
  )
}

function App() {
  const [isModelLoaded, setIsModelLoaded] = useState(false)
  const [modelScale, setModelScale] = useState(1)
  const [modelRotation, setModelRotation] = useState<[number, number, number]>([0, 0, 0])
  const [modelPosition, setModelPosition] = useState<[number, number, number]>([0, -1, 0])
  const [availableAnimations, setAvailableAnimations] = useState<string[]>([])
  const [currentAnimation, setCurrentAnimation] = useState<string | null>(null)
  const [showSpaceBackground, setShowSpaceBackground] = useState(true)
  
  // 預加載模型
  useEffect(() => {
    const modelUrl = '/models/mixamowomanwithface.glb'
    useGLTF.preload(modelUrl)
    
    // 模擬模型加載完成
    const timer = setTimeout(() => {
      setIsModelLoaded(true)
    }, 1000)
    
    return () => clearTimeout(timer)
  }, [])

  // 旋轉模型
  const rotateModel = (direction: 'left' | 'right') => {
    setModelRotation(prev => {
      const step = direction === 'left' ? 0.1 : -0.1
      return [prev[0], prev[1] + step, prev[2]]
    })
  }

  // 縮放模型
  const scaleModel = (factor: number) => {
    setModelScale(prev => {
      const newScale = prev + factor
      return newScale > 0.1 ? newScale : 0.1 
    })
  }

  // 重置模型
  const resetModel = () => {
    setModelScale(1)
    setModelRotation([0, 0, 0])
    setModelPosition([0, -1, 0])
    setCurrentAnimation(null)
  }

  // 選擇動畫
  const selectAnimation = (animationName: string) => {
    setCurrentAnimation(animationName)
  }

  // 切換背景
  const toggleBackground = () => {
    setShowSpaceBackground(prev => !prev)
  }

  return (
    <div className="app-container">
      <div className="canvas-container">
        <Canvas camera={{ position: [0, 1, 5], fov: 50 }}>
          {showSpaceBackground ? (
            <SpaceBackground />
          ) : (
            <color attach="background" args={['#121212']} />
          )}
          
          <ambientLight intensity={0.5} />
          <directionalLight position={[10, 10, 5]} intensity={1} />
          <directionalLight position={[-10, -10, -5]} intensity={0.5} />
          
          {isModelLoaded && 
            <Model 
              url="/models/mixamowomanwithface.glb" 
              scale={modelScale}
              rotation={modelRotation}
              position={modelPosition}
              currentAnimation={currentAnimation}
              setAvailableAnimations={setAvailableAnimations}
            />
          }
          <OrbitControls />
        </Canvas>
      </div>
      
      <div className="controls-panel">
        <h1>虛擬太空人互動原型</h1>
        <p>這是一個基本的3D模型顯示原型，使用React和Three.js開發</p>
        
        <div className="status-info">
          <p>模型狀態: {isModelLoaded ? '已加載' : '加載中...'}</p>
          <p>模型縮放: {modelScale.toFixed(2)}</p>
          <p>當前動畫: {currentAnimation || '無'}</p>
        </div>
        
        <div className="button-row">
          <button onClick={() => rotateModel('left')} disabled={!isModelLoaded}>
            向左旋轉
          </button>
          <button onClick={() => rotateModel('right')} disabled={!isModelLoaded}>
            向右旋轉
          </button>
          <button onClick={() => scaleModel(0.1)} disabled={!isModelLoaded}>
            放大
          </button>
          <button onClick={() => scaleModel(-0.1)} disabled={!isModelLoaded}>
            縮小
          </button>
          <button onClick={resetModel} disabled={!isModelLoaded}>
            重置
          </button>
          <button onClick={toggleBackground}>
            {showSpaceBackground ? '隱藏星空' : '顯示星空'}
          </button>
        </div>
        
        {availableAnimations.length > 0 && (
          <div className="animation-controls">
            <h3>動畫控制</h3>
            <div className="animation-buttons">
              {availableAnimations.map((anim) => (
                <button 
                  key={anim}
                  onClick={() => selectAnimation(anim)}
                  className={currentAnimation === anim ? 'active' : ''}
                  disabled={!isModelLoaded}
                >
                  {anim}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App 