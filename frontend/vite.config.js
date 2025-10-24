import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    hmr: {
      overlay: false,
      // Disable HMR in production
      protocol: process.env.NODE_ENV === 'production' ? null : 'ws'
    },
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false
      }
    },
    watch: {
      usePolling: false,
      interval: 3000
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})