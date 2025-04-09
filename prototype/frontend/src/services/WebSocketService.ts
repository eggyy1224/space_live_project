import { useState, useEffect, useRef } from 'react';
import logger, { LogCategory } from '../utils/LogManager';
import { useStore } from '../store';

// WebSocket連接配置
const WS_URL = `ws://${window.location.hostname}:8000/ws`;
const WS_RETRY_MAX = 5;
const WS_RETRY_INTERVAL = 3000; // 3秒

// 消息處理器類型
type MessageHandler = (data: any) => void;

interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

// WebSocket服務類
class WebSocketService {
  private static instance: WebSocketService;
  private ws: WebSocket | null = null;
  private retryCount = 0;
  private messageHandlers: { [type: string]: MessageHandler[] } = {};
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  // 添加防抖動和批量處理的函數
  private _debounceMap: Map<string, {
    timeout: number | null,
    lastData: any,
    lastTime: number
  }> = new Map();

  // 單例模式
  public static getInstance(): WebSocketService {
    if (!WebSocketService.instance) {
      WebSocketService.instance = new WebSocketService();
    }
    return WebSocketService.instance;
  }

  // 連接WebSocket
  public connect(): void {
    logger.debug("Connect method entered.", LogCategory.WEBSOCKET);

    if (this.ws) {
      logger.debug(`WebSocket object exists. Current state: ${this.ws.readyState}`, LogCategory.WEBSOCKET);
      if (this.ws.readyState === WebSocket.CONNECTING || this.ws.readyState === WebSocket.OPEN) {
        logger.info({ msg: 'WebSocket已連接或正在連接中', details: { readyState: this.ws.readyState }}, LogCategory.WEBSOCKET);
        return;
      } else {
        logger.warn(`WebSocket exists but state is ${this.ws.readyState}. Proceeding to reconnect.`, LogCategory.WEBSOCKET);
        try { this.ws.close(); } catch (e) { /* ignore potential errors closing already closed socket */ }
        this.ws = null;
      }
    } else {
      logger.debug("WebSocket object (this.ws) is null. Proceeding to create.", LogCategory.WEBSOCKET);
    }

    if (this.reconnectTimer) {
        logger.debug("Clearing existing reconnect timer before new connection attempt.", LogCategory.WEBSOCKET);
        clearTimeout(this.reconnectTimer);
        this.reconnectTimer = null;
    }
    this.retryCount = 0;

    try {
      logger.info({ msg: 'Attempting to create new WebSocket object...', details: { url: WS_URL }}, LogCategory.WEBSOCKET);
      this.ws = new WebSocket(WS_URL);
      logger.debug({ msg: 'New WebSocket object created.', details: { readyState: this.ws.readyState }}, LogCategory.WEBSOCKET);
      logger.debug("Attaching WebSocket event handlers (onopen, onmessage, onerror, onclose)", LogCategory.WEBSOCKET);
      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onerror = this.handleError.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
      logger.debug("WebSocket event handlers attached.", LogCategory.WEBSOCKET);

    } catch (error) {
      logger.error('Error during WebSocket object creation or handler attachment:', LogCategory.WEBSOCKET, error);
      this.ws = null;
      this.handleReconnect();
    }
    logger.debug("Connect method finished.", LogCategory.WEBSOCKET);
  }

  // 關閉WebSocket連接
  public disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    // 更新全局狀態
    useStore.getState().setConnected(false);
    this.retryCount = 0;
  }

  // 發送消息
  public sendMessage(message: WebSocketMessage): boolean {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
      logger.debug({ msg: `發送 WebSocket 消息: ${message.type}`, details: message }, LogCategory.WEBSOCKET, message.type);
      return true;
    }
    logger.error({ 
      msg: 'WebSocket未連接，無法發送消息', 
      details: {
        readyState: this.ws?.readyState,
        message 
      }
    }, LogCategory.WEBSOCKET);
    return false;
  }

  // 發送文本消息
  public sendTextMessage(content: string): boolean {
    return this.sendMessage({
      type: 'chat-message',
      message: content
    });
  }

  // 註冊消息處理器
  public registerHandler(type: string, handler: MessageHandler): void {
    if (!this.messageHandlers[type]) {
      this.messageHandlers[type] = [];
    }
    this.messageHandlers[type].push(handler);
  }

  // 移除消息處理器
  public removeHandler(type: string, handler: MessageHandler): void {
    if (this.messageHandlers[type]) {
      this.messageHandlers[type] = this.messageHandlers[type].filter(h => h !== handler);
    }
  }

  // 獲取連接狀態 (使用 Zustand)
  public isConnected(): boolean {
    return useStore.getState().isConnected;
  }

  // 處理WebSocket打開事件
  private handleOpen(): void {
    logger.info('WebSocket已連接', LogCategory.WEBSOCKET);
    
    // 更新全局狀態
    useStore.getState().setConnected(true);
    this.retryCount = 0;
    
    // 仍然保留通知處理器，以支持舊的代碼
    if (this.messageHandlers['connection_status']) {
      this.messageHandlers['connection_status'].forEach(handler => handler({ connected: true }));
    }
  }

  // 處理WebSocket消息
  private handleMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data) as WebSocketMessage;
      // --- 從高頻類型中移除 lipsync_update --- 
      const highFrequencyTypes = ['morph_update', 'animation_update']; // Remove 'lipsync_update'

      // Log received message (conditionally based on frequency)
      if (data.type && !highFrequencyTypes.includes(data.type)) {
        logger.info(`收到WebSocket消息: ${data.type}`, LogCategory.WEBSOCKET);
      } else if (data.type) {
        logger.debug(`收到WebSocket消息: ${data.type}`, LogCategory.WEBSOCKET, data.type);
      }
      
      // --- 新增：直接處理 emotionalTrajectory 消息 --- 
      if (data.type === 'emotionalTrajectory') {
        // --- 添加日誌記錄 ---
        console.log('[WebSocketService] Received Emotional Trajectory:', JSON.stringify(data.payload, null, 2));
        // --- 日誌記錄結束 ---
        logger.debug('[WebSocketService] Detected emotionalTrajectory, updating lastJsonMessage.', LogCategory.WEBSOCKET);
        useStore.getState().setLastJsonMessage(data); // 更新軌跡數據
        // --- 新增：清空手動/預設權重狀態 --- 
        useStore.getState().setMorphTargets({}); // 重置 morphTargets，確保情緒軌跡優先
        logger.debug('[WebSocketService] Reset morphTargets state to prioritize trajectory.', LogCategory.WEBSOCKET);
        // --- 新增結束 ---
      } 
      // --- 新增結束 ---
      
      // --- 原有邏輯：處理高頻消息和註冊的 handlers --- 
      else if (data.type && highFrequencyTypes.includes(data.type)) {
        this._handleHighFrequencyMessage(data.type, data);
      } else {
        // 調用對應類型的消息處理器
        if (data.type && this.messageHandlers[data.type]) {
          this.messageHandlers[data.type].forEach(handler => {
            try {
              handler(data);
            } catch (error) {
              logger.error(`處理 ${data.type} 消息錯誤:`, LogCategory.WEBSOCKET, error);
            }
          });
        }
        
        // 調用通用消息處理器 (如果有的話)
        if (this.messageHandlers['*']) {
          this.messageHandlers['*'].forEach(handler => {
            try {
              handler(data);
            } catch (error) {
              logger.error('處理通用消息錯誤', LogCategory.WEBSOCKET, error);
            }
          });
        }
      }
      // --- 原有邏輯結束 ---

    } catch (error) {
      logger.error('解析WebSocket消息錯誤', LogCategory.WEBSOCKET, error);
    }
  }

  // 處理WebSocket錯誤
  private handleError(error: Event): void {
    logger.error('WebSocket 發生錯誤', LogCategory.WEBSOCKET, { 
      errorEvent: error, 
      readyState: this.ws?.readyState // 添加 readyState 方便調試
    });
    
    // 更新全局狀態
    useStore.getState().setConnected(false);
    
    // 仍然保留通知處理器，以支持舊的代碼
    if (this.messageHandlers['connection_status']) {
      this.messageHandlers['connection_status'].forEach(handler => 
        handler({ connected: false, error: true })
      );
    }
    // 錯誤發生後也應該嘗試重連
    this.handleReconnect(); 
  }

  // 處理WebSocket關閉
  private handleClose(event: CloseEvent): void {
    logger.info({ 
      msg: `WebSocket 已關閉`, 
      details: {
        code: event.code,
        reason: event.reason,
        wasClean: event.wasClean,
        readyState: this.ws?.readyState
      }
    }, LogCategory.WEBSOCKET);
    
    // 更新全局狀態
    useStore.getState().setConnected(false);
    this.ws = null;
    
    // 清理所有防抖動計時器
    this._debounceMap.forEach((info, type) => {
      if (info.timeout !== null) {
        window.clearTimeout(info.timeout);
        info.timeout = null;
      }
    });
    this._debounceMap.clear();
    
    // 仍然保留通知處理器，以支持舊的代碼
    if (this.messageHandlers['connection_status']) {
      this.messageHandlers['connection_status'].forEach(handler => 
        handler({ connected: false })
      );
    }
    
    // 判斷是否需要重新連接
    if (event.code !== 1000 && event.code !== 1001) {
      // 非正常關閉，嘗試重新連接
      this.handleReconnect();
    }
  }

  // 處理重新連接
  private handleReconnect(): void {
    if (this.retryCount >= WS_RETRY_MAX) {
      logger.warn(`嘗試重連已達最大次數 (${WS_RETRY_MAX})，不再嘗試重連`, LogCategory.WEBSOCKET);
      return;
    }
    
    this.retryCount++;
    const delay = WS_RETRY_INTERVAL * Math.min(this.retryCount, 5);
    
    logger.info(`計劃在 ${delay}ms 後進行第 ${this.retryCount} 次重連`, LogCategory.WEBSOCKET);
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
    
    this.reconnectTimer = setTimeout(() => {
      logger.info(`開始第 ${this.retryCount} 次重連...`, LogCategory.WEBSOCKET);
      this.connect();
    }, delay);
  }

  // 處理高頻消息 (使用防抖動策略)
  private _handleHighFrequencyMessage(type: string, message: any): void {
    // 防抖動邏輯: 如果消息類型在防抖動映射中不存在，則創建一個
    if (!this._debounceMap.has(type)) {
      this._debounceMap.set(type, {
        timeout: null,
        lastData: null,
        lastTime: 0
      });
    }
    
    const info = this._debounceMap.get(type)!;
    const now = Date.now();
    const debounceTime = type === 'lipsync_update' ? 30 : 50; // 唇同步需要更快的響應
    
    // 保存最後收到的數據
    info.lastData = message;
    
    // 如果已經有一個定時器在運行，則不處理
    if (info.timeout !== null) {
      return;
    }
    
    // 如果上次處理到現在的時間足夠長，則立即處理
    if (now - info.lastTime > debounceTime) {
      this._processHighFrequencyMessage(type, message);
      info.lastTime = now;
      
      // 設置一個定時器來防止過於頻繁的消息處理
      info.timeout = window.setTimeout(() => {
        // 檢查在此期間是否收到新數據
        if (info.lastData !== message) {
          this._processHighFrequencyMessage(type, info.lastData);
          info.lastTime = Date.now();
        }
        info.timeout = null;
      }, debounceTime);
    } else {
      // 設置一個定時器，等待足夠的時間後處理最後一條數據
      info.timeout = window.setTimeout(() => {
        this._processHighFrequencyMessage(type, info.lastData);
        info.lastTime = Date.now();
        info.timeout = null;
      }, debounceTime - (now - info.lastTime));
    }
  }

  // 處理高頻消息的具體實現
  private _processHighFrequencyMessage(type: string, message: any): void {
    // 調用對應類型的消息處理器
    if (this.messageHandlers[type]) {
      this.messageHandlers[type].forEach(handler => {
        try {
          handler(message);
        } catch (error) {
          logger.error(`處理 ${type} 高頻消息錯誤:`, LogCategory.WEBSOCKET, error);
        }
      });
    }
  }
}

// 使用 WebSocket 服務的 React Hook
export function useWebSocket() {
  // 直接從 Zustand 獲取連接狀態
  const isConnected = useStore((state) => state.isConnected);
  
  useEffect(() => {
    // 獲取 WebSocketService 實例並連接
    const wsService = WebSocketService.getInstance();
    wsService.connect();
    
    // 在組件卸載時斷開連接
    return () => {
      wsService.disconnect();
    };
  }, []);
  
  // 返回連接狀態
  return {
    isConnected
  };
}

export default WebSocketService; 