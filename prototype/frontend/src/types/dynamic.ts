/**
 * Schema describing when each slot should start relative to the entire play
 * duration. Percentages are expressed in 0-100.
 */
export interface DynamicTemplate {
  /** Human friendly name of the template */
  template_name: string;
  /** Array of slots ordered by their trigger time */
  slots: {
    /** Name of the slot. e.g. bgm, video_intro */
    slot_name: string;
    /** Percentage of the total duration when this slot triggers */
    percentage: number;
  }[];
}

/**
 * A bundle describing which media files to play and the total duration in
 * seconds.
 */
export interface PlayPackage {
  /** Unique name of the play */
  play_name: string;
  /** Total play length in seconds */
  total_duration: number;
  /** Mapping from slot name to media path */
  contents: Record<string, string>;
}

/**
 * Event dispatched whenever a slot begins playback.
 */
export interface PlaybackEvent {
  /** Slot identifier */
  slotName: string;
  /** Timestamp when the slot started */
  startedAtMs: number;
}
