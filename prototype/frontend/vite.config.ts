import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // 允許來自外部網路的連線
    allowedHosts: [
      '.ngrok-free.app' // 允許所有 ngrok-free.app 的子網域
    ],
  }
})
