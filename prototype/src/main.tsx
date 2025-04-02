import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App'
import logger, { LogLevel } from './utils/LogManager'

// 設置日誌級別 - 生產環境使用WARN，開發環境使用INFO
logger.setLogLevel(window.location.hostname !== 'localhost' ? LogLevel.WARN : LogLevel.INFO);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
