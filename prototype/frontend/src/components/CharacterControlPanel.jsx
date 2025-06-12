import React, { useEffect } from 'react'
import { useCharacterStore } from '../stores/useCharacterStore'

const CharacterControlPanel = () => {
  const visible = useCharacterStore((s) => s.panelVisible)
  const togglePanel = useCharacterStore((s) => s.togglePanel)
  const morphTargets = useCharacterStore((s) => s.morphTargets)
  const setMorphTarget = useCharacterStore((s) => s.setMorphTarget)
  const setMorphTargets = useCharacterStore((s) => s.setMorphTargets)

  useEffect(() => {
    fetch('/model_data/character0611.glb_analysis.json')
      .then((res) => res.json())
      .then((data) => {
        if (data.morphTargetNames) {
          const targets = {}
          data.morphTargetNames.forEach((name) => {
            targets[name] = 0
          })
          setMorphTargets(targets)
        }
      })
  }, [setMorphTargets])

  if (!visible) {
    return (
      <button
        onClick={togglePanel}
        style={{ position: 'fixed', bottom: '10px', right: '10px', zIndex: 1000 }}
      >
        Show Controls
      </button>
    )
  }

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '10px',
        right: '10px',
        width: '260px',
        maxHeight: '50vh',
        overflowY: 'auto',
        background: 'rgba(0,0,0,0.8)',
        color: '#fff',
        padding: '10px',
        borderRadius: '8px',
        zIndex: 1000
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <strong>Morph Targets</strong>
        <button onClick={togglePanel}>×</button>
      </div>
      {Object.keys(morphTargets).map((key) => (
        <div key={key} style={{ marginBottom: '4px' }}>
          <label style={{ display: 'block' }}>{key}</label>
          <input
            type="range"
            min={0}
            max={1}
            step={0.01}
            value={morphTargets[key]}
            onChange={(e) => setMorphTarget(key, parseFloat(e.target.value))}
          />
        </div>
      ))}
    </div>
  )
}

export default CharacterControlPanel
