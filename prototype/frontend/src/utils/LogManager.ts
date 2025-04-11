/**
 * 日誌管理器 - 控制應用中的日誌輸出
 */

// 日誌級別
export enum LogLevel {
  NONE = 0,   // 不輸出任何日誌
  ERROR = 1,  // 只輸出錯誤
  WARN = 2,   // 輸出警告和錯誤
  INFO = 3,   // 輸出信息、警告和錯誤
  DEBUG = 4,  // 輸出所有級別的日誌，包括調試信息
}

// 日誌類別 - 用於分組不同類型的日誌
export enum LogCategory {
  GENERAL = 'general',
  WEBSOCKET = 'websocket',
  MODEL = 'model',
  AUDIO = 'audio',
  CHAT = 'chat',
  ANIMATION = 'animation',
  MORPH = 'morph',
  PERFORMANCE = 'performance',
}

// 當前環境
const isProduction = typeof window !== 'undefined' && 
  window.location.hostname !== 'localhost' && 
  window.location.hostname !== '127.0.0.1';

// 日誌管理器類
class LogManager {
  private static instance: LogManager;
  
  // 默認日誌級別 - 生產環境只顯示錯誤，開發環境顯示所有
  private logLevel: LogLevel = isProduction ? LogLevel.ERROR : LogLevel.INFO;
  
  // 每個類別的日誌設置
  private categorySettings: Map<LogCategory, LogLevel> = new Map();
  
  // 是否顯示時間戳
  private showTimestamp: boolean = true;
  
  // 禁用的高頻日誌類型
  private disabledHighFrequencyLogs: Set<string> = new Set([
    'lipsync_update',
    'morph_update', 
    'animation_frame'
  ]);
  
  // 日誌計數器，用於限制高頻日誌的輸出
  private logCounters: Map<string, number> = new Map();
  
  // 上次重置計數器的時間
  private lastCounterReset: number = Date.now();
  
  // 單例模式
  public static getInstance(): LogManager {
    if (!LogManager.instance) {
      LogManager.instance = new LogManager();
    }
    return LogManager.instance;
  }
  
  constructor() {
    // 初始化每個類別的默認日誌級別
    Object.values(LogCategory).forEach(category => {
      this.categorySettings.set(category as LogCategory, this.logLevel);
    });
    
    // 為高頻類別設置更嚴格的級別
    this.categorySettings.set(LogCategory.ANIMATION, LogLevel.ERROR);
    this.categorySettings.set(LogCategory.MORPH, LogLevel.WARN);
    this.categorySettings.set(LogCategory.MODEL, LogLevel.ERROR);
  }
  
  // 設置全局日誌級別
  public setLogLevel(level: LogLevel): void {
    this.logLevel = level;
    
    // 更新所有未特別指定的類別
    Object.values(LogCategory).forEach(category => {
      this.categorySettings.set(category as LogCategory, level);
    });
  }
  
  // 設置特定類別的日誌級別
  public setCategoryLogLevel(category: LogCategory, level: LogLevel): void {
    this.categorySettings.set(category, level);
  }
  
  // 啟用/禁用時間戳
  public setShowTimestamp(show: boolean): void {
    this.showTimestamp = show;
  }
  
  // 添加禁用的高頻日誌類型
  public addDisabledHighFrequencyLog(type: string): void {
    this.disabledHighFrequencyLogs.add(type);
  }
  
  // 移除禁用的高頻日誌類型
  public removeDisabledHighFrequencyLog(type: string): void {
    this.disabledHighFrequencyLogs.delete(type);
  }
  
  // 檢查是否應該輸出特定類型的日誌
  private shouldLog(category: LogCategory, level: LogLevel, type?: string): boolean {
    // 檢查類別日誌級別
    const categoryLevel = this.categorySettings.get(category) || this.logLevel;
    if (level > categoryLevel) {
      return false;
    }
    
    // 檢查高頻日誌類型
    if (type && this.disabledHighFrequencyLogs.has(type)) {
      // 重置計數器（每10秒）
      const now = Date.now();
      if (now - this.lastCounterReset > 10000) {
        this.logCounters.clear();
        this.lastCounterReset = now;
      }
      
      // 增加計數並檢查是否超出限制
      const count = (this.logCounters.get(type) || 0) + 1;
      this.logCounters.set(type, count);
      
      // 對於高頻日誌，每100條只顯示一條
      return count % 100 === 1;
    }
    
    return true;
  }
  
  // 格式化日誌前綴
  private formatPrefix(category: LogCategory, level: string): string {
    let prefix = `[${level}][${category}]`;
    
    if (this.showTimestamp) {
      const now = new Date();
      const timeStr = now.toLocaleTimeString('zh-TW', { hour12: false });
      prefix = `[${timeStr}]${prefix}`;
    }
    
    return prefix;
  }
  
  // 輸出調試日誌
  public debug(message: any, category: LogCategory = LogCategory.GENERAL, type?: string): void {
    if (this.shouldLog(category, LogLevel.DEBUG, type)) {
      const prefix = this.formatPrefix(category, 'DEBUG');
      console.debug(prefix, message);
    }
  }
  
  // 輸出信息日誌
  public info(message: any, category: LogCategory = LogCategory.GENERAL, type?: string): void {
    if (this.shouldLog(category, LogLevel.INFO, type)) {
      const prefix = this.formatPrefix(category, 'INFO');
      console.info(prefix, message);
    }
  }
  
  // 輸出警告日誌
  public warn(message: any, category: LogCategory = LogCategory.GENERAL, type?: string): void {
    if (this.shouldLog(category, LogLevel.WARN, type)) {
      const prefix = this.formatPrefix(category, 'WARN');
      console.warn(prefix, message);
    }
  }
  
  // 輸出錯誤日誌
  public error(message: any, category: LogCategory = LogCategory.GENERAL, error?: any): void {
    if (this.shouldLog(category, LogLevel.ERROR)) {
      const prefix = this.formatPrefix(category, 'ERROR');
      if (error) {
        console.error(prefix, message, error);
      } else {
        console.error(prefix, message);
      }
    }
  }
}

// 導出全局logger實例
export const logger = LogManager.getInstance();

// 簡便使用方法
export default logger;
