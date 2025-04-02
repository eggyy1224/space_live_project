import { useState, useEffect, useRef } from 'react';
import logger, { LogCategory } from '../utils/LogManager';

// WebSocket連接配置
const WS_URL = 'ws://localhost:8000/ws';
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
  private connected = false;
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
    if (this.ws && (this.ws.readyState === WebSocket.CONNECTING || this.ws.readyState === WebSocket.OPEN)) {
      logger.info('WebSocket已連接或正在連接中', LogCategory.WEBSOCKET);
      return;
    }

    try {
      logger.info('嘗試連接WebSocket...', LogCategory.WEBSOCKET);
      this.ws = new WebSocket(WS_URL);

      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onerror = this.handleError.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
    } catch (error) {
      logger.error('創建WebSocket連接錯誤:', LogCategory.WEBSOCKET, error);
      this.handleReconnect();
    }
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
    
    this.connected = false;
    this.retryCount = 0;
  }

  // 發送消息
  public sendMessage(message: WebSocketMessage): boolean {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
      return true;
    }
    console.error('WebSocket未連接，無法發送消息');
    return false;
  }

  // 發送文本消息
  public sendTextMessage(content: string): boolean {
    return this.sendMessage({
      type: 'message',
      content
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

  // 獲取連接狀態
  public isConnected(): boolean {
    return this.connected;
  }

  // 處理WebSocket打開事件
  private handleOpen(): void {
    logger.info('WebSocket已連接', LogCategory.WEBSOCKET);
    this.connected = true;
    this.retryCount = 0;
    
    // 通知所有連接狀態變更的處理器
    if (this.messageHandlers['connection_status']) {
      this.messageHandlers['connection_status'].forEach(handler => handler({ connected: true }));
    }
  }

  // 處理WebSocket消息
  private handleMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data) as WebSocketMessage;
      // 只保留重要消息類型的日誌，移除高頻消息類型的日誌
      const highFrequencyTypes = ['lipsync_update', 'morph_update', 'animation_update'];
      if (data.type && !highFrequencyTypes.includes(data.type)) {
        logger.info(`收到WebSocket消息: ${data.type}`, LogCategory.WEBSOCKET);
      } else if (data.type) {
        // 高頻消息使用debug級別，並提供消息類型以進行過濾
        logger.debug(`收到WebSocket消息: ${data.type}`, LogCategory.WEBSOCKET, data.type);
      }
      
      if (data.type && highFrequencyTypes.includes(data.type)) {
        // 使用防抖動機制處理高頻消息
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
        
        // 調用通用消息處理器
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
    } catch (error) {
      logger.error('解析WebSocket消息錯誤', LogCategory.WEBSOCKET, error);
    }
  }

  // 處理WebSocket錯誤
  private handleError(error: Event): void {
    logger.error('WebSocket錯誤', LogCategory.WEBSOCKET, error);
    
    // 通知所有連接狀態變更的處理器
    if (this.messageHandlers['connection_status']) {
      this.messageHandlers['connection_status'].forEach(handler => 
        handler({ connected: false, error: true })
      );
    }
  }

  // 處理WebSocket關閉
  private handleClose(event: CloseEvent): void {
    logger.info(`WebSocket已關閉: ${event.code} ${event.reason}`, LogCategory.WEBSOCKET);
    this.connected = false;
    this.ws = null;
    
    // 清理所有防抖動計時器
    this._debounceMap.forEach((info, type) => {
      if (info.timeout !== null) {
        window.clearTimeout(info.timeout);
        info.timeout = null;
      }
    });
    this._debounceMap.clear();
    
    // 通知所有連接狀態變更的處理器
    if (this.messageHandlers['connection_status']) {
      this.messageHandlers['connection_status'].forEach(handler => 
        handler({ connected: false })
      );
    }
    
    this.handleReconnect();
  }

  // 處理重新連接
  private handleReconnect(): void {
    if (this.retryCount >= WS_RETRY_MAX) {
      logger.warn('超過最大重試次數，停止嘗試連接', LogCategory.WEBSOCKET);
      return;
    }
    
    this.retryCount += 1;
    logger.info(`WebSocket重連中... (${this.retryCount}/${WS_RETRY_MAX})`, LogCategory.WEBSOCKET);
    
    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, WS_RETRY_INTERVAL);
  }

  // 處理高頻消息的防抖動
  private _handleHighFrequencyMessage(type: string, message: any): void {
    const now = Date.now();
    
    // 獲取或創建此類型消息的防抖動信息
    if (!this._debounceMap.has(type)) {
      this._debounceMap.set(type, {
        timeout: null,
        lastData: null,
        lastTime: 0
      });
    }
    
    const debounceInfo = this._debounceMap.get(type)!;
    
    // 更新最新的數據
    debounceInfo.lastData = message;
    debounceInfo.lastTime = now;
    
    // 如果已經有一個計時器在運行，不做任何事
    if (debounceInfo.timeout !== null) {
      return;
    }
    
    // 設置防抖動計時器，對於不同類型的消息使用不同的延遲
    const debounceDelay = type === 'lipsync_update' ? 50 : 100;
    
    debounceInfo.timeout = window.setTimeout(() => {
      // 檢查是否有最新數據需要處理
      if (debounceInfo.lastData) {
        // 處理最新的數據
        const handlers = this.messageHandlers[type];
        if (handlers) {
          handlers.forEach(handler => {
            try {
              handler(debounceInfo.lastData);
            } catch (error) {
              logger.error(`處理 ${type} 消息錯誤`, LogCategory.WEBSOCKET, error);
            }
          });
        }
      }
      
      // 重置防抖動信息
      debounceInfo.timeout = null;
      debounceInfo.lastData = null;
      
      // 如果在處理過程中又收到新消息，則再次啟動計時器
      const timeSinceLastUpdate = Date.now() - debounceInfo.lastTime;
      if (timeSinceLastUpdate < debounceDelay) {
        this._handleHighFrequencyMessage(type, debounceInfo.lastData);
      }
    }, debounceDelay);
  }
}

// React Hook - 使用WebSocket
export function useWebSocket() {
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const wsService = useRef<WebSocketService>(WebSocketService.getInstance());

  useEffect(() => {
    // 連接狀態處理器
    const connectionHandler = (data: { connected: boolean }) => {
      setIsConnected(data.connected);
    };
    
    // 註冊連接狀態處理器
    wsService.current.registerHandler('connection_status', connectionHandler);
    
    // 建立連接
    wsService.current.connect();
    
    // 首次檢查連接狀態
    setIsConnected(wsService.current.isConnected());

    // 組件卸載時清理
    return () => {
      wsService.current.removeHandler('connection_status', connectionHandler);
    };
  }, []);

  return {
    isConnected,
    sendMessage: (message: WebSocketMessage) => wsService.current.sendMessage(message),
    sendTextMessage: (content: string) => wsService.current.sendTextMessage(content),
    registerHandler: (type: string, handler: MessageHandler) => 
      wsService.current.registerHandler(type, handler),
    removeHandler: (type: string, handler: MessageHandler) => 
      wsService.current.removeHandler(type, handler),
  };
}

export default WebSocketService; 