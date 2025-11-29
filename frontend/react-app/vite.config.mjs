import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
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
    sourcemap: true,  // Ativar sourcemap para debug
    outDir: 'dist',       // gera dentro de react-app/dist
    emptyOutDir: true,     // limpa a pasta antes de cada build
    minify: 'esbuild',  // Usar esbuild ao invés de terser
    rollupOptions: {
      output: {
        manualChunks: undefined,  // Desabilita chunking automático
        entryFileNames: `assets/[name]-[hash]-${Date.now()}.js`,
        chunkFileNames: `assets/[name]-[hash]-${Date.now()}.js`,
        assetFileNames: `assets/[name]-[hash]-${Date.now()}.[ext]`
      }
    }
  }
})