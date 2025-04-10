/**
 * 動畫關鍵幀接口
 * 定義動畫序列中的單個關鍵幀
 */
export interface AnimationKeyframe {
    /**
     * 動畫名稱 (必須是 ANIMATION_NAMES 中的友好名稱)
     */
    name: string;
    
    /**
     * 開始播放的時間比例 (0.0 到 1.0)
     * 相對於總語音時長的比例
     */
    proportion: number;
    
    /**
     * 過渡時間 (秒)
     * 從上一個動畫過渡到這個動畫的時間
     * 默認為 0.5 秒
     */
    transitionDuration?: number;
    
    /**
     * 是否循環播放
     * 如果為 true，則會一直循環播放此動畫直到下一個關鍵幀開始
     * 如果為 false，則播放一次後保持最後一幀
     * 默認為 false
     */
    loop?: boolean;
    
    /**
     * 動畫權重 (0.0 到 1.0)
     * 用於混合多個動畫時的權重分配
     * 默認為 1.0
     */
    weight?: number;
    
    /**
     * 循環次數
     * 指定動畫應該循環的確切次數
     * 僅當 loop 為 true 時生效
     * 如果未設置，則無限循環直到下一個關鍵幀
     */
    loopCount?: number;
}

/**
 * 動畫混合模式
 */
export enum AnimationBlendMode {
    /**
     * 正常模式 - 默認過渡
     */
    NORMAL = 'normal',
    
    /**
     * 交叉淡入淡出 - 使用 crossFadeTo
     */
    CROSSFADE = 'crossfade',
    
    /**
     * 加法混合 - 兩個動畫同時播放並添加效果
     */
    ADDITIVE = 'additive'
}

/**
 * 播放狀態
 */
export enum PlaybackState {
    /**
     * 已停止
     */
    STOPPED = 'stopped',
    
    /**
     * 正在播放
     */
    PLAYING = 'playing',
    
    /**
     * 已暫停
     */
    PAUSED = 'paused'
} 