/**
 * Data types for DynamicPlayRunner
 */

export interface DynamicTemplate {
  template_name: string;
  slots: {
    slot_name: string;
    percentage: number;
  }[];
}

export interface PlayPackage {
  play_name: string;
  total_duration: number;
  contents: Record<string, string>;
}

export interface PlaybackEvent {
  slotName: string;
  startedAtMs: number;
}
