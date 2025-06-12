import { create } from 'zustand'

interface CharacterState {
  panelVisible: boolean
  morphTargets: Record<string, number>
  morphTargetDictionary: Record<string, number>
  togglePanel: () => void
  setMorphTarget: (name: string, value: number) => void
  setMorphTargets: (targets: Record<string, number>) => void
  setMorphTargetDictionary: (dict: Record<string, number>) => void
}

export const useCharacterStore = create<CharacterState>((set) => ({
  panelVisible: false,
  morphTargets: {},
  morphTargetDictionary: {},
  togglePanel: () => set((s) => ({ panelVisible: !s.panelVisible })),
  setMorphTarget: (name, value) =>
    set((state) => ({
      morphTargets: { ...state.morphTargets, [name]: value }
    })),
  setMorphTargets: (targets) => set({ morphTargets: targets }),
  setMorphTargetDictionary: (dict) => set({ morphTargetDictionary: dict })
}))
