import { useState, useEffect, useCallback } from 'react';
import freesoundService, { 
  FreesoundSearchParams, 
  FreesoundSearchResult, 
  FreesoundSearchResultsPage 
} from '../services/FreesoundService';
import logger, { LogCategory } from '../utils/LogManager';

interface UseFreesoundAPIProps {
  initialQuery?: string;
  autoSearch?: boolean;
}

interface UseFreesoundAPIReturn {
  // 搜索相關
  isLoading: boolean;
  error: string | null;
  results: FreesoundSearchResultsPage | null;
  searchResults: FreesoundSearchResult[];
  
  // 搜索操作
  search: (params: FreesoundSearchParams) => Promise<void>;
  searchByTag: (tag: string, params?: Omit<FreesoundSearchParams, 'query'>) => Promise<void>;
  loadMore: () => Promise<void>;
  
  // 音效詳情
  getSound: (soundId: number) => Promise<FreesoundSearchResult>;
  getSimilarSounds: (soundId: number) => Promise<FreesoundSearchResultsPage>;
  
  // 緩存管理
  cachedSounds: Partial<FreesoundSearchResult>[];
  cacheSound: (sound: FreesoundSearchResult) => Promise<void>;
  clearCache: (soundId?: number) => void;
  
  // 播放控制
  getPreviewUrl: (sound: FreesoundSearchResult, quality?: 'hq' | 'lq', format?: 'mp3' | 'ogg') => string;
  
  // 頁面控制
  currentPage: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
  totalResults: number;
  setPage: (page: number) => void;
}

/**
 * Freesound API Hook
 * 提供在React組件中使用Freesound API的功能
 */
export const useFreesoundAPI = ({ 
  initialQuery = '', 
  autoSearch = false 
}: UseFreesoundAPIProps = {}): UseFreesoundAPIReturn => {
  // 搜索狀態
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<FreesoundSearchResultsPage | null>(null);
  const [searchParams, setSearchParams] = useState<FreesoundSearchParams>({
    query: initialQuery,
    page: 1,
    page_size: 15
  });
  
  // 緩存狀態
  const [cachedSounds, setCachedSounds] = useState<Partial<FreesoundSearchResult>[]>([]);
  
  // 載入緩存的音效
  useEffect(() => {
    const loadCachedSounds = () => {
      const sounds = freesoundService.getAllCachedSounds();
      setCachedSounds(sounds);
    };
    
    loadCachedSounds();
  }, []);
  
  // 執行搜索
  const search = useCallback(async (params: FreesoundSearchParams) => {
    setIsLoading(true);
    setError(null);
    
    try {
      setSearchParams(params);
      const searchResults = await freesoundService.searchSounds(params);
      setResults(searchResults);
      logger.info(`[useFreesoundAPI] 搜索成功: ${searchResults.count} 個結果`, LogCategory.AUDIO);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '搜索失敗';
      setError(errorMessage);
      logger.error(`[useFreesoundAPI] 搜索失敗: ${errorMessage}`, LogCategory.AUDIO);
    } finally {
      setIsLoading(false);
    }
  }, []);
  
  // 通過標籤搜索
  const searchByTag = useCallback(async (tag: string, params: Omit<FreesoundSearchParams, 'query'> = {}) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const newParams = {
        query: `tag:${tag}`,
        ...params
      };
      setSearchParams(newParams);
      const searchResults = await freesoundService.searchSounds(newParams);
      setResults(searchResults);
      logger.info(`[useFreesoundAPI] 標籤搜索成功: ${searchResults.count} 個結果`, LogCategory.AUDIO);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '標籤搜索失敗';
      setError(errorMessage);
      logger.error(`[useFreesoundAPI] 標籤搜索失敗: ${errorMessage}`, LogCategory.AUDIO);
    } finally {
      setIsLoading(false);
    }
  }, []);
  
  // 加載更多結果(下一頁)
  const loadMore = useCallback(async () => {
    if (!results || !results.next || isLoading) {
      return;
    }
    
    setIsLoading(true);
    
    try {
      const nextPage = searchParams.page ? searchParams.page + 1 : 2;
      const newParams = { ...searchParams, page: nextPage };
      setSearchParams(newParams);
      
      const nextResults = await freesoundService.searchSounds(newParams);
      setResults(prevResults => {
        if (!prevResults) return nextResults;
        
        return {
          ...nextResults,
          results: [...prevResults.results, ...nextResults.results]
        };
      });
      
      logger.info(`[useFreesoundAPI] 加載更多成功: 頁 ${nextPage}`, LogCategory.AUDIO);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '加載更多失敗';
      setError(errorMessage);
      logger.error(`[useFreesoundAPI] 加載更多失敗: ${errorMessage}`, LogCategory.AUDIO);
    } finally {
      setIsLoading(false);
    }
  }, [results, searchParams, isLoading]);
  
  // 設置頁碼
  const setPage = useCallback((page: number) => {
    setSearchParams(prev => ({ ...prev, page }));
    search({ ...searchParams, page });
  }, [search, searchParams]);
  
  // 獲取音效詳情
  const getSound = useCallback(async (soundId: number): Promise<FreesoundSearchResult> => {
    try {
      const sound = await freesoundService.getSoundDetails(soundId);
      return sound;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '獲取音效詳情失敗';
      logger.error(`[useFreesoundAPI] 獲取音效詳情失敗: ${errorMessage}`, LogCategory.AUDIO);
      throw err;
    }
  }, []);
  
  // 獲取類似音效
  const getSimilarSounds = useCallback(async (soundId: number): Promise<FreesoundSearchResultsPage> => {
    try {
      const similar = await freesoundService.getSimilarSounds(soundId);
      return similar;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '獲取類似音效失敗';
      logger.error(`[useFreesoundAPI] 獲取類似音效失敗: ${errorMessage}`, LogCategory.AUDIO);
      throw err;
    }
  }, []);
  
  // 緩存音效
  const cacheSound = useCallback(async (sound: FreesoundSearchResult): Promise<void> => {
    try {
      await freesoundService.cacheSound(sound);
      // 更新緩存列表
      setCachedSounds(prev => {
        const exists = prev.some(item => item.id === sound.id);
        if (exists) return prev;
        
        return [...prev, {
          id: sound.id,
          name: sound.name,
          previews: sound.previews,
          duration: sound.duration,
          license: sound.license,
          username: sound.username,
          tags: sound.tags
        }];
      });
    } catch (err) {
      logger.error(`[useFreesoundAPI] 緩存音效失敗`, LogCategory.AUDIO, err);
    }
  }, []);
  
  // 清除緩存
  const clearCache = useCallback((soundId?: number) => {
    freesoundService.clearCache(soundId);
    
    if (soundId) {
      // 只移除特定音效
      setCachedSounds(prev => prev.filter(sound => sound.id !== soundId));
    } else {
      // 清空所有
      setCachedSounds([]);
    }
  }, []);
  
  // 獲取預覽URL
  const getPreviewUrl = useCallback((sound: FreesoundSearchResult, quality: 'hq' | 'lq' = 'hq', format: 'mp3' | 'ogg' = 'mp3'): string => {
    return freesoundService.getPreviewUrl(sound, quality, format);
  }, []);
  
  // 初始搜索
  useEffect(() => {
    if (autoSearch && initialQuery) {
      search({ query: initialQuery, page: 1 });
    }
  }, [autoSearch, initialQuery, search]);
  
  return {
    isLoading,
    error,
    results,
    searchResults: results?.results || [],
    
    search,
    searchByTag,
    loadMore,
    
    getSound,
    getSimilarSounds,
    
    cachedSounds,
    cacheSound,
    clearCache,
    
    getPreviewUrl,
    
    currentPage: searchParams.page || 1,
    hasNextPage: !!results?.next,
    hasPreviousPage: !!results?.previous,
    totalResults: results?.count || 0,
    setPage
  };
};

export default useFreesoundAPI; 