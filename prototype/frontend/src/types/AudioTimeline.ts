import Ajv from 'ajv';

/**
 * 音軌類型
 */
export type AudioTrackType = 'sfx' | 'voice';

/**
 * 聲音事件類型
 */
export type AudioEventType = 'music' | 'sfx' | 'combo' | 'tts' | 'singing';

/**
 * 動畫線索類型
 */
export type AnimationCueType = 'viseme' | 'emotion' | 'action';

/**
 * 動畫線索 / 表情時間點
 */
export interface AnimationCue {
  /**
   * 相對於事件開始的時間（秒）
   */
  time: number;
  /**
   * 線索類型
   */
  type: AnimationCueType;
  /**
   * 線索值，例如嘴型("A"), 情緒("happy"), 動作標籤("wave_hand")
   */
  value: string;
}

/**
 * 單一聲音事件
 */
export interface AudioTimelineEvent {
  /**
   * 事件開始時間（秒，必填）
   */
  startTime: number;
  /**
   * 音軌類型，可用於區分需要表情動畫的聲音管線
   * sfx: 背景/效果音；voice: 角色語音
   * 若不提供，預設為 'sfx'
   */
  track?: AudioTrackType;
  /**
   * 事件類型
   */
  type: AudioEventType;
  /**
   * 資源標識（ID 或 URL），由前端/後端協定
   */
  resource: string;
  /**
   * 持續時間（秒，可選）
   */
  duration?: number;
  /** 是否需要循環播放 */
  loop?: boolean;
  /** 建議音量 (0-1) */
  volume?: number;
  /**
   * 是否需要表情/動作動畫同步
   * 一般語音 (tts/singing) 或特定 sfx 設為 true
   */
  requiresAnimation?: boolean;
  /**
   * 若需要動畫，同步數據
   */
  animationCues?: AnimationCue[];
}

/**
 * 時間軸結構
 */
export interface AudioTimeline {
  timeline: AudioTimelineEvent[];
}

/* ------------------------------------------------------------------
 * JSON Schema & 驗證工具
 * ------------------------------------------------------------------ */

const ajv = new Ajv({ allErrors: true });

type JSONSchemaType<T> = any;

const animationCueSchema: JSONSchemaType<AnimationCue> = {
  type: 'object',
  properties: {
    time: {type: 'number'},
    type: {type: 'string', enum: ['viseme', 'emotion', 'action'] as any},
    value: {type: 'string'}
  },
  required: ['time', 'type', 'value'],
  additionalProperties: false
};

const audioTimelineEventSchema: JSONSchemaType<AudioTimelineEvent> = {
  type: 'object',
  properties: {
    startTime: {type: 'number'},
    track: {type: 'string', nullable: true, enum: ['sfx', 'voice'] as any},
    type: {type: 'string', enum: ['music', 'sfx', 'combo', 'tts', 'singing'] as any},
    resource: {type: 'string'},
    duration: {type: 'number', nullable: true},
    loop: {type: 'boolean', nullable: true},
    volume: {type: 'number', nullable: true},
    requiresAnimation: {type: 'boolean', nullable: true},
    animationCues: {type: 'array', nullable: true, items: animationCueSchema}
  },
  required: ['startTime', 'type', 'resource'],
  additionalProperties: false
};

const audioTimelineSchema: JSONSchemaType<AudioTimeline> = {
  type: 'object',
  properties: {
    timeline: {type: 'array', items: audioTimelineEventSchema}
  },
  required: ['timeline'],
  additionalProperties: false
};

const validateFn = ajv.compile(audioTimelineSchema);

export function validateAudioTimeline(data: any): {valid: boolean; errors?: any[]} {
  const valid = validateFn(data);
  if (!valid) {
    return {valid: false, errors: validateFn.errors || []};
  }
  return {valid: true};
} 