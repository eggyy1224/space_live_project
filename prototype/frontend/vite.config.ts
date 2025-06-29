import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    host: true, // 允許來自外部網路的連線
    allowedHosts: [
      '.ngrok-free.app' // 允許所有 ngrok-free.app 的子網域
    ],
    fs: {
      // 允許訪問 public 目錄和子目錄
      allow: ['..', '.'],
    }
  },
  // 確保靜態資源能正確服務
  publicDir: 'public',
  // 添加對音頻文件的 MIME 類型支持
  define: {
    // 這可以幫助確保音頻文件被正確識別
  }
})
