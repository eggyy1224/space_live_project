/**
 * 音效配置文件
 * 定義可用於應用程式的音效及其URL路徑
 */

/**
 * 音效列表
 * name: 音效識別符
 * url: 音效文件路徑 (相對於public目錄)
 */
export const soundEffects: Record<string, string> = {
  // 綜藝音效
  'entrance': '/audio/effects/entrance.mp3',
  'whoosh': '/audio/effects/whoosh.mp3',
  'applause': '/audio/effects/applause.mp3',
  'cheer': '/audio/effects/cheer.mp3',
  'drumroll': '/audio/effects/drumroll.mp3',
  'tada': '/audio/effects/tada.mp3',
  'transition': '/audio/effects/transition.mp3',
  'fail': '/audio/effects/fail.mp3',
  'success': '/audio/effects/success.mp3',
  
  // 科幻音效
  'laser': '/audio/effects/laser.mp3',
  'beep': '/audio/effects/beep.mp3',
  'spaceship': '/audio/effects/spaceship.mp3',
  'teleport': '/audio/effects/teleport.mp3',
  'alien': '/audio/effects/alien.mp3',
  'robot': '/audio/effects/robot.mp3',
  
  // 環境音效
  'wind': '/audio/effects/wind.mp3',
  'rain': '/audio/effects/rain.mp3',
  'thunder': '/audio/effects/thunder.mp3',
  'space': '/audio/effects/space.mp3',
};

/**
 * 音效分類
 * 將音效按類型進行分組，方便UI顯示
 */
export const soundEffectCategories: Record<string, string[]> = {
  'variety': ['entrance', 'whoosh', 'applause', 'cheer', 'drumroll', 'tada', 'transition', 'fail', 'success'],
  'sci-fi': ['laser', 'beep', 'spaceship', 'teleport', 'alien', 'robot'],
  'environment': ['wind', 'rain', 'thunder', 'space'],
};

/**
 * 音效信息配置，包含顯示名稱和描述
 */
export interface SoundEffectDetails {
  name: string;
  description: string;
}

export const soundEffectInfo: Record<string, SoundEffectDetails> = {
  'entrance': {
    name: '登場音',
    description: '角色華麗登場時使用的音效',
  },
  'whoosh': {
    name: 'Whoosh',
    description: '快速移動或場景切換時的嗖聲',
  },
  'applause': {
    name: '掌聲',
    description: '觀眾鼓掌聲，用於角色精彩表現',
  },
  'cheer': {
    name: '歡呼',
    description: '觀眾歡呼聲，表示熱烈反應',
  },
  'drumroll': {
    name: '鼓點',
    description: '期待感增強，預示重要事件',
  },
  'tada': {
    name: '歡慶',
    description: '慶祝或揭曉時的喜慶音效',
  },
  'transition': {
    name: '轉場',
    description: '切換場景或話題時的提示音',
  },
  'fail': {
    name: '失敗',
    description: '表示失敗或出錯的喜劇音效',
  },
  'success': {
    name: '成功',
    description: '表示成功或完成的音效',
  },
  'laser': {
    name: '雷射',
    description: '科幻感的雷射槍射擊音效',
  },
  'beep': {
    name: '嗶聲',
    description: '電子設備的提示音',
  },
  'spaceship': {
    name: '飛船',
    description: '宇宙飛船引擎聲',
  },
  'teleport': {
    name: '傳送',
    description: '瞬間移動或傳送的音效',
  },
  'alien': {
    name: '外星',
    description: '外星生物或UFO音效',
  },
  'robot': {
    name: '機器人',
    description: '機器人說話或移動音效',
  },
  'wind': {
    name: '風聲',
    description: '環境風聲音效',
  },
  'rain': {
    name: '雨聲',
    description: '環境雨聲音效',
  },
  'thunder': {
    name: '雷聲',
    description: '環境雷聲音效',
  },
  'space': {
    name: '太空',
    description: '太空環境背景音效',
  },
};

export default soundEffects; 