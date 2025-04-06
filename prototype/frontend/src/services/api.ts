/**
 * API服務
 * 提供與後端API交互的工具函數
 */

// API基礎URL - 移除production模式中的'/api'前綴，因為後端路由已包含'/api'前綴
const API_BASE_URL = import.meta.env.MODE === 'production'
  ? window.location.origin
  : `http://${window.location.hostname}:8000`;

// 可能的API錯誤類型
export class ApiError extends Error {
  status: number;
  data: any;

  constructor(message: string, status: number, data: any = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

// API響應類型
type ApiResponse<T> = {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
};

/**
 * 基本HTTP請求函數
 * @param url API端點
 * @param options 請求選項
 * @returns 響應數據
 */
async function fetchApi<T>(url: string, options: RequestInit = {}): Promise<T> {
  const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url.startsWith('/') ? url : `/${url}`}`;
  
  // 默認請求設置
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    credentials: 'include', // 包含cookies
  };

  // 合併選項
  const fetchOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(fullUrl, fetchOptions);
    
    // 檢查是否為JSON響應
    const contentType = response.headers.get('content-type');
    let data: any;
    
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    // 處理非200響應
    if (!response.ok) {
      let errorMessage = typeof data === 'string' ? data : (data.error || data.message || `請求失敗，狀態碼: ${response.status}`);
      throw new ApiError(errorMessage, response.status, data);
    }

    return data as T;
  } catch (error) {
    // 重新拋出ApiError或包裝其他錯誤
    if (error instanceof ApiError) {
      throw error;
    }
    
    // 網絡錯誤或其他異常
    console.error('API請求錯誤:', error);
    throw new ApiError(
      error instanceof Error ? error.message : '網絡請求失敗',
      0,
      { originalError: error }
    );
  }
}

/**
 * 文本分析API
 * @param text 要分析的文本
 * @returns 分析結果
 */
export async function analyzeText(text: string): Promise<{ 
  response: string; 
  emotion?: string;
  confidence?: number;
}> {
  return fetchApi('/api/analyze_text', {
    method: 'POST',
    body: JSON.stringify({ text }),
  });
}

/**
 * 生成TTS音頻
 * @param text 要轉換為語音的文本
 * @returns 音頻URL
 */
export async function generateSpeech(text: string): Promise<{ 
  audio_url: string;
  duration?: number; 
}> {
  return fetchApi('/api/text_to_speech', {
    method: 'POST',
    body: JSON.stringify({ text }),
  });
}

/**
 * 上傳音頻進行語音轉文本
 * @param audioBlob 音頻Blob數據
 * @returns 轉換結果
 */
export async function speechToText(audioBlob: Blob): Promise<{ 
  text: string;
  confidence?: number;
}> {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'speech.webm');

  return fetchApi('/api/speech-to-text', {
    method: 'POST',
    headers: {}, // 重置headers，讓瀏覽器自動設置Content-Type為multipart/form-data
    body: formData,
  });
}

/**
 * 健康檢查API
 * @returns 服務狀態
 */
export async function checkHealth(): Promise<{ 
  status: string;
  version?: string;
}> {
  return fetchApi('/api/health');
}

/**
 * 獲取可用語音配置
 * @returns 語音配置列表
 */
export async function getVoiceConfigs(): Promise<{
  id: string;
  name: string;
  language_code: string;
  gender: string;
}[]> {
  return fetchApi('/api/voices');
}

/**
 * 設置當前使用的語音配置
 * @param voiceId 語音配置ID
 * @returns 操作結果
 */
export async function setVoiceConfig(voiceId: string): Promise<{ success: boolean }> {
  return fetchApi('/api/set_voice', {
    method: 'POST',
    body: JSON.stringify({ voice_id: voiceId }),
  });
}

/**
 * 獲取系統日誌
 * @param limit 最大日誌條目數
 * @returns 日誌條目列表
 */
export async function getLogs(limit: number = 100): Promise<{
  level: string;
  timestamp: string;
  message: string;
  context?: Record<string, any>;
}[]> {
  return fetchApi(`/api/logs?limit=${limit}`);
}

/**
 * 獲取預設表情設定
 * @param expression 表情類型
 * @returns 表情變形目標
 */
export async function getPresetExpression(expression: string): Promise<Record<string, number>> {
  return fetchApi(`/api/preset-expressions/${expression}`);
}

// 導出API服務
const apiService = {
  analyzeText,
  generateSpeech,
  speechToText,
  checkHealth,
  getVoiceConfigs,
  setVoiceConfig,
  getLogs,
  getPresetExpression,
};

export default apiService; 