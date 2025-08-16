import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: import.meta.env.MODE === 'development' ? {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false
      }
    } : undefined
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/tests/setup.js',
  },
})
