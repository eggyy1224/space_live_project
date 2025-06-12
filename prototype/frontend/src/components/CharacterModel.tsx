import React, { useEffect } from 'react'
import { useGLTF } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { useCharacterStore } from '../stores/useCharacterStore'

interface Props {
  position?: [number, number, number]
  rotation?: [number, number, number]
  scale?: number | [number, number, number]
}

const MODEL_URL = '/models/character0611.glb'

const CharacterModel: React.FC<Props> = ({ position = [0, 0, 0], rotation = [0, 0, 0], scale = 1 }) => {
  const { scene } = useGLTF(MODEL_URL)
  const morphTargets = useCharacterStore((s) => s.morphTargets)
  const setDict = useCharacterStore((s) => s.setMorphTargetDictionary)

  useEffect(() => {
    const dict: Record<string, number> = {}
    scene.traverse((obj: THREE.Object3D) => {
      const mesh = obj as THREE.Mesh
      if (mesh.morphTargetDictionary) {
        Object.assign(dict, mesh.morphTargetDictionary)
      }
    })
    setDict(dict)
  }, [scene, setDict])

  useFrame(() => {
    scene.traverse((obj: THREE.Object3D) => {
      const mesh = obj as THREE.Mesh
      if (mesh.morphTargetDictionary && mesh.morphTargetInfluences) {
        Object.entries(mesh.morphTargetDictionary).forEach(([name, index]) => {
          mesh.morphTargetInfluences![index] = morphTargets[name] || 0
        })
      }
    })
  })

  return <primitive object={scene} position={position} rotation={rotation} scale={scale} />
}

useGLTF.preload(MODEL_URL)

export default CharacterModel
