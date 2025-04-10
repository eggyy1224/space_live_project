// 從共享配置導入動畫定義
import animationsJson from '../../../shared/config/animations.json';

// 定義動畫類型介面
export interface AnimationDefinition {
  path: string;
  description: string;
}

// 從 JSON 轉換到強類型的映射
export const ANIMATIONS: Record<string, AnimationDefinition> = animationsJson as Record<string, AnimationDefinition>;

// 導出動畫路徑陣列 (用於預加載)
export const ANIMATION_PATHS: string[] = Object.values(ANIMATIONS).map(anim => anim.path);

// 導出動畫名稱陣列 (用於 UI 和狀態管理)
export const ANIMATION_NAMES: string[] = Object.keys(ANIMATIONS);

// 提供按名稱查詢動畫路徑的函數
export function getAnimationPathByName(name: string): string | undefined {
  return ANIMATIONS[name]?.path;
}

// 提供按名稱查詢動畫描述的函數
export function getAnimationDescriptionByName(name: string): string | undefined {
  return ANIMATIONS[name]?.description;
} 