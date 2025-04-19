import axios from 'axios';
import logger, { LogCategory } from '../utils/LogManager';

/**
 * Freesound 音效搜索結果介面
 */
export interface FreesoundSearchResult {
  id: number;            // 音效ID
  name: string;          // 音效名稱
  tags: string[];        // 音效標籤
  username: string;      // 上傳者
  license: string;       // 許可證
  previews: {            // 預覽URL
    'preview-hq-mp3': string;
    'preview-lq-mp3': string;
    'preview-hq-ogg': string;
    'preview-lq-ogg': string;
  };
  duration: number;      // 時長(秒)
  description: string;   // 描述
  url: string;           // Freesound頁面URL
  download: string;      // 下載URL(需授權)
  created: string;       // 創建時間
  images: {              // 波形圖
    waveform_m: string;
    waveform_l: string;
    spectral_m: string;
    spectral_l: string;
  };
  num_downloads: number; // 下載次數
  avg_rating: number;    // 平均評分
  num_ratings: number;   // 評分次數
}

/**
 * Freesound API搜索參數
 */
export interface FreesoundSearchParams {
  query: string;                 // 搜索關鍵詞
  filter?: string;               // 過濾器，如 "duration:[0 TO 10]"
  sort?: string;                 // 排序方式，如 "rating_desc"
  fields?: string;               // 返回字段
  page?: number;                 // 頁碼
  page_size?: number;            // 頁大小
  descriptors?: string;          // 內容分析描述符
  normalized?: boolean;          // 是否標準化描述符
  group_by_pack?: boolean;       // 是否按包分組
  target?: string;               // 內容相似性搜索目標
  target_descriptors?: string[]; // 目標描述符
}

/**
 * Freesound API 搜索結果分頁
 */
export interface FreesoundSearchResultsPage {
  count: number;                   // 總結果數
  next: string | null;             // 下一頁URL
  previous: string | null;         // 上一頁URL
  results: FreesoundSearchResult[]; // 結果列表
  page: number;                    // 當前頁碼
  page_size: number;               // 頁大小
}

/**
 * Freesound 服務類
 * 提供對Freesound API的訪問功能
 */
class FreesoundService {
  private apiKey: string | null = null;
  private baseUrl = 'https://freesound.org/apiv2';
  private proxyBaseUrl = '/api/freesound'; // 後端代理
  private useProxy = true; // 是否使用後端代理(建議)

  /**
   * 設置API金鑰
   * @param apiKey Freesound API金鑰
   */
  setApiKey(apiKey: string): void {
    this.apiKey = apiKey;
    logger.info('[FreesoundService] API金鑰已設置', LogCategory.AUDIO);
  }

  /**
   * 檢查API金鑰是否已設置
   * @returns 是否已設置金鑰
   */
  hasApiKey(): boolean {
    return !!this.apiKey;
  }

  /**
   * 設置是否使用後端代理
   * @param useProxy 是否使用代理
   */
  setUseProxy(useProxy: boolean): void {
    this.useProxy = useProxy;
  }

  /**
   * 獲取API請求URL
   * @param endpoint API端點
   * @returns 完整URL
   */
  private getUrl(endpoint: string): string {
    return this.useProxy 
      ? `${this.proxyBaseUrl}${endpoint}` 
      : `${this.baseUrl}${endpoint}`;
  }

  /**
   * 獲取API請求頭
   * @returns HTTP請求頭
   */
  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {};
    
    if (!this.useProxy && this.apiKey) {
      headers['Authorization'] = `Token ${this.apiKey}`;
    }
    
    return headers;
  }

  /**
   * 搜索音效
   * @param params 搜索參數
   * @returns 搜索結果頁
   */
  async searchSounds(params: FreesoundSearchParams): Promise<FreesoundSearchResultsPage> {
    try {
      logger.info(`[FreesoundService] 搜索音效: ${params.query}`, LogCategory.AUDIO);
      
      const url = this.getUrl('/search/text/');
      const headers = this.getHeaders();
      
      const response = await axios.get(url, {
        headers,
        params: {
          query: params.query,
          filter: params.filter,
          sort: params.sort || 'score',
          fields: params.fields || 'id,name,tags,username,license,previews,duration,description,url,download,created,images,num_downloads,avg_rating,num_ratings',
          page: params.page || 1,
          page_size: params.page_size || 15,
          descriptors: params.descriptors,
          normalized: params.normalized ? 1 : 0,
          group_by_pack: params.group_by_pack ? 1 : 0
        }
      });
      
      logger.info(`[FreesoundService] 搜索成功: 找到 ${response.data.count} 個結果`, LogCategory.AUDIO);
      return response.data;
    } catch (error) {
      logger.error('[FreesoundService] 搜索失敗', LogCategory.AUDIO, error);
      throw new Error(`搜索失敗: ${error instanceof Error ? error.message : '未知錯誤'}`);
    }
  }

  /**
   * 獲取音效詳情
   * @param soundId 音效ID
   * @returns 音效詳情
   */
  async getSoundDetails(soundId: number): Promise<FreesoundSearchResult> {
    try {
      logger.info(`[FreesoundService] 獲取音效詳情: ${soundId}`, LogCategory.AUDIO);
      
      const url = this.getUrl(`/sounds/${soundId}/`);
      const headers = this.getHeaders();
      
      const response = await axios.get(url, { headers });
      
      logger.info(`[FreesoundService] 獲取音效詳情成功: ${response.data.name}`, LogCategory.AUDIO);
      return response.data;
    } catch (error) {
      logger.error('[FreesoundService] 獲取音效詳情失敗', LogCategory.AUDIO, error);
      throw new Error(`獲取音效詳情失敗: ${error instanceof Error ? error.message : '未知錯誤'}`);
    }
  }

  /**
   * 獲取類似音效
   * @param soundId 音效ID
   * @param params 搜索參數
   * @returns 類似音效列表
   */
  async getSimilarSounds(soundId: number, params: { page?: number, page_size?: number } = {}): Promise<FreesoundSearchResultsPage> {
    try {
      logger.info(`[FreesoundService] 獲取類似音效: ${soundId}`, LogCategory.AUDIO);
      
      const url = this.getUrl(`/sounds/${soundId}/similar/`);
      const headers = this.getHeaders();
      
      const response = await axios.get(url, {
        headers,
        params: {
          page: params.page || 1,
          page_size: params.page_size || 15,
          fields: 'id,name,tags,username,license,previews,duration,description,url,download,created,images,num_downloads,avg_rating,num_ratings'
        }
      });
      
      logger.info(`[FreesoundService] 獲取類似音效成功: 找到 ${response.data.count} 個結果`, LogCategory.AUDIO);
      return response.data;
    } catch (error) {
      logger.error('[FreesoundService] 獲取類似音效失敗', LogCategory.AUDIO, error);
      throw new Error(`獲取類似音效失敗: ${error instanceof Error ? error.message : '未知錯誤'}`);
    }
  }

  /**
   * 獲取音效預覽URL
   * @param sound 音效對象
   * @param quality 預覽質量 ('hq'|'lq')
   * @param format 音頻格式 ('mp3'|'ogg')
   * @returns 預覽URL
   */
  getPreviewUrl(sound: FreesoundSearchResult, quality: 'hq' | 'lq' = 'hq', format: 'mp3' | 'ogg' = 'mp3'): string {
    const previewKey = `preview-${quality}-${format}` as keyof typeof sound.previews;
    return sound.previews[previewKey];
  }

  /**
   * 使用標籤搜索音效
   * @param tag 標籤
   * @param params 其他搜索參數
   * @returns 搜索結果頁
   */
  async searchSoundsByTag(tag: string, params: Omit<FreesoundSearchParams, 'query'> = {}): Promise<FreesoundSearchResultsPage> {
    return this.searchSounds({
      query: `tag:${tag}`,
      ...params
    });
  }

  /**
   * 緩存音效到本地存儲
   * @param sound 音效對象
   */
  async cacheSound(sound: FreesoundSearchResult): Promise<void> {
    try {
      logger.info(`[FreesoundService] 緩存音效: ${sound.id} - ${sound.name}`, LogCategory.AUDIO);
      
      // 這裡僅存儲元數據
      localStorage.setItem(`freesound_cache_${sound.id}`, JSON.stringify({
        id: sound.id,
        name: sound.name,
        previews: sound.previews,
        duration: sound.duration,
        license: sound.license,
        username: sound.username,
        tags: sound.tags,
        cached_at: new Date().toISOString()
      }));
      
      logger.info(`[FreesoundService] 音效元數據已緩存: ${sound.id}`, LogCategory.AUDIO);
    } catch (error) {
      logger.error('[FreesoundService] 緩存音效失敗', LogCategory.AUDIO, error);
    }
  }

  /**
   * 獲取緩存的音效
   * @param soundId 音效ID
   * @returns 緩存的音效(如果存在)
   */
  getCachedSound(soundId: number): Partial<FreesoundSearchResult> | null {
    try {
      const cached = localStorage.getItem(`freesound_cache_${soundId}`);
      if (!cached) return null;
      
      return JSON.parse(cached);
    } catch (error) {
      logger.error('[FreesoundService] 獲取緩存音效失敗', LogCategory.AUDIO, error);
      return null;
    }
  }

  /**
   * 獲取所有緩存的音效
   * @returns 緩存的音效列表
   */
  getAllCachedSounds(): Partial<FreesoundSearchResult>[] {
    const sounds: Partial<FreesoundSearchResult>[] = [];
    
    try {
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith('freesound_cache_')) {
          const soundData = localStorage.getItem(key);
          if (soundData) {
            sounds.push(JSON.parse(soundData));
          }
        }
      }
    } catch (error) {
      logger.error('[FreesoundService] 獲取所有緩存音效失敗', LogCategory.AUDIO, error);
    }
    
    return sounds;
  }

  /**
   * 清除音效緩存
   * @param soundId 音效ID(可選,若不提供則清除所有緩存)
   */
  clearCache(soundId?: number): void {
    try {
      if (soundId) {
        localStorage.removeItem(`freesound_cache_${soundId}`);
        logger.info(`[FreesoundService] 已清除音效緩存: ${soundId}`, LogCategory.AUDIO);
      } else {
        // 清除所有Freesound相關緩存
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i);
          if (key && key.startsWith('freesound_cache_')) {
            localStorage.removeItem(key);
          }
        }
        logger.info('[FreesoundService] 已清除所有音效緩存', LogCategory.AUDIO);
      }
    } catch (error) {
      logger.error('[FreesoundService] 清除緩存失敗', LogCategory.AUDIO, error);
    }
  }
}

// 導出單例
export const freesoundService = new FreesoundService();
export default freesoundService; 