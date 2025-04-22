import React, { useState } from 'react';
import { useSoundEffects } from '../../hooks';
import logger, { LogCategory } from '../../utils/LogManager';

// 接口定義
interface FreesoundResult {
  id: number;
  name: string;
  username: string;
  license: string;
  duration: number;
  previews: {
    'preview-hq-mp3': string;
    'preview-lq-mp3': string;
  };
}

interface FreesoundResponse {
  count: number;
  results: FreesoundResult[];
  next: string | null;
  previous: string | null;
}

interface FreesoundPanelProps {
  soundEffects: ReturnType<typeof useSoundEffects>;
}

const FreesoundPanel: React.FC<FreesoundPanelProps> = ({ soundEffects }) => {
  // 狀態管理
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<FreesoundResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [nextPageUrl, setNextPageUrl] = useState<string | null>(null);
  const [prevPageUrl, setPrevPageUrl] = useState<string | null>(null);
  const [totalResults, setTotalResults] = useState(0);
  const [currentlyPlaying, setCurrentlyPlaying] = useState<number | null>(null);

  // 從sound effects hook中獲取必要的函數
  const { 
    unlockAudioContext,
    stopAllSounds,
    playSingleSoundEffect: playSound
  } = soundEffects;

  // 處理搜尋輸入變更
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  // 當用戶按下Enter鍵時觸發搜尋
  const handleSearchKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // 執行搜尋
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Freesound API 請求
      const response = await fetch(
        `/api/freesound/search?query=${encodeURIComponent(searchQuery)}`
      );
      
      if (!response.ok) {
        throw new Error(`API 錯誤: ${response.status}`);
      }
      
      const data: FreesoundResponse = await response.json();
      
      logger.info(`[FreesoundPanel] Search results for "${searchQuery}":`, LogCategory.AUDIO);
      
      setSearchResults(data.results);
      setTotalResults(data.count);
      setNextPageUrl(data.next);
      setPrevPageUrl(data.previous);
    } catch (err) {
      logger.error('[FreesoundPanel] Search error:', LogCategory.AUDIO);
      setError(`搜尋出錯: ${err instanceof Error ? err.message : '未知錯誤'}`);
      setSearchResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  // 處理分頁
  const handlePageNavigation = async (url: string | null) => {
    if (!url) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      // 解析URL以獲取查詢參數
      const urlObj = new URL(url);
      const queryParams = Object.fromEntries(urlObj.searchParams);
      
      // 構建API請求URL
      const apiUrl = `/api/freesound/search?${new URLSearchParams(queryParams)}`;
      
      const response = await fetch(apiUrl);
      
      if (!response.ok) {
        throw new Error(`API 錯誤: ${response.status}`);
      }
      
      const data: FreesoundResponse = await response.json();
      
      logger.info('[FreesoundPanel] Pagination results:', LogCategory.AUDIO);
      
      setSearchResults(data.results);
      setNextPageUrl(data.next);
      setPrevPageUrl(data.previous);
    } catch (err) {
      logger.error('[FreesoundPanel] Pagination error:', LogCategory.AUDIO);
      setError(`分頁出錯: ${err instanceof Error ? err.message : '未知錯誤'}`);
    } finally {
      setIsLoading(false);
    }
  };

  // 播放音頻預覽
  const handlePlayPreview = (sound: FreesoundResult) => {
    logger.info(`[FreesoundPanel] Playing preview for sound ${sound.id}: ${sound.name}`, LogCategory.AUDIO);
    
    // 如果有其他音效正在播放，先停止
    if (currentlyPlaying !== null) {
      stopAllSounds();
    }
    
    // 由於我們沒有直接的playExternalAudio方法，這裡需要進行適當的替代實現
    // 在實際應用中，可能需要先將聲音下載並加載到系統中
    // 這裡僅做示意
    unlockAudioContext().then(success => {
      if (success) {
        // 這裡應該使用適當的方法播放外部音頻
        // 臨時解決方案，實際中需要實現外部音頻的播放
        console.log(`Would play: ${sound.previews['preview-hq-mp3']}`);
        
        // 模擬音頻播放結束
        setTimeout(() => {
          setCurrentlyPlaying(null);
        }, sound.duration * 1000);
        
        setCurrentlyPlaying(sound.id);
      } else {
        logger.warn('[FreesoundPanel] Cannot play sound: AudioContext not unlocked', LogCategory.AUDIO);
      }
    });
  };

  // 停止播放
  const handleStopPreview = () => {
    logger.info('[FreesoundPanel] Stopping all previews', LogCategory.AUDIO);
    stopAllSounds();
    setCurrentlyPlaying(null);
  };

  return (
    <div>
      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-2">Freesound 音效搜尋</h3>
        <div className="flex space-x-2">
          <input
            type="text"
            className="flex-1 px-3 py-2 bg-gray-700 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="輸入關鍵字搜尋 (例如: 'piano', 'explosion', 'bird')"
            value={searchQuery}
            onChange={handleSearchChange}
            onKeyPress={handleSearchKeyPress}
          />
          <button
            onClick={handleSearch}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors duration-200"
            disabled={isLoading}
          >
            {isLoading ? '搜尋中...' : '搜尋'}
          </button>
        </div>
        
        {/* 錯誤訊息 */}
        {error && (
          <div className="mt-2 text-red-400 text-sm">
            {error}
          </div>
        )}
        
        {/* 搜尋結果信息 */}
        {searchResults.length > 0 && (
          <div className="mt-2 text-gray-400 text-sm">
            顯示 {searchResults.length} 個結果，共 {totalResults} 個
          </div>
        )}
      </div>
      
      {/* 搜尋結果列表 */}
      {searchResults.length > 0 && (
        <div className="mt-4">
          <div className="space-y-2">
            {searchResults.map(sound => (
              <div 
                key={sound.id} 
                className={`p-3 rounded-md ${
                  currentlyPlaying === sound.id 
                    ? 'bg-gray-600 border border-blue-500' 
                    : 'bg-gray-700 hover:bg-gray-600'
                } transition-colors duration-200`}
              >
                <div className="flex justify-between items-center">
                  <div className="flex-1">
                    <h4 className="font-medium text-white">{sound.name}</h4>
                    <div className="text-sm text-gray-400">
                      by {sound.username} • {sound.duration.toFixed(1)}s • {sound.license}
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    {currentlyPlaying === sound.id ? (
                      <button
                        onClick={handleStopPreview}
                        className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded-md transition-colors duration-200"
                        title="停止播放"
                      >
                        停止
                      </button>
                    ) : (
                      <button
                        onClick={() => handlePlayPreview(sound)}
                        className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-sm rounded-md transition-colors duration-200"
                        title="播放預覽"
                      >
                        播放
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {/* 分頁控制 */}
          <div className="mt-4 flex justify-between">
            <button
              onClick={() => handlePageNavigation(prevPageUrl)}
              className={`px-3 py-1 text-sm rounded-md ${
                prevPageUrl
                  ? 'bg-blue-600 hover:bg-blue-700 text-white'
                  : 'bg-gray-700 text-gray-500 cursor-not-allowed'
              } transition-colors duration-200`}
              disabled={!prevPageUrl || isLoading}
            >
              上一頁
            </button>
            <button
              onClick={() => handlePageNavigation(nextPageUrl)}
              className={`px-3 py-1 text-sm rounded-md ${
                nextPageUrl
                  ? 'bg-blue-600 hover:bg-blue-700 text-white'
                  : 'bg-gray-700 text-gray-500 cursor-not-allowed'
              } transition-colors duration-200`}
              disabled={!nextPageUrl || isLoading}
            >
              下一頁
            </button>
          </div>
        </div>
      )}
      
      {/* 空結果提示 */}
      {!isLoading && searchQuery && searchResults.length === 0 && !error && (
        <div className="mt-4 p-4 bg-gray-700 rounded-md text-center text-gray-400">
          沒有找到匹配"{searchQuery}"的音效，請嘗試其他關鍵詞。
        </div>
      )}
      
      {/* 初始提示 */}
      {!searchQuery && searchResults.length === 0 && (
        <div className="mt-4 p-4 bg-gray-700 rounded-md">
          <p className="text-gray-400 text-center">
            在上方搜尋欄輸入關鍵詞，搜尋來自 Freesound.org 的免費音效。
          </p>
          <p className="text-gray-500 text-sm text-center mt-2">
            建議關鍵詞: piano, explosion, bird, water, footsteps, door, wind
          </p>
        </div>
      )}
    </div>
  );
};

export default FreesoundPanel; 