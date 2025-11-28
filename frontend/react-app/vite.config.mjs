import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  base: '/frontend/',
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        ws: true
      }
    },
  },
  build: {
    sourcemap: false,
    outDir: 'dist',       // gera dentro de react-app/dist
    emptyOutDir: true     // limpa a pasta antes de cada build
  }
})