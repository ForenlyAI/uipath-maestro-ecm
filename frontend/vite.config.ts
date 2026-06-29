import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  // base must match the GitHub repository name for gh-pages to resolve assets correctly
  base: '/uipath-maestro-ecm/',
  plugins: [react()],
  server: {
    // During local dev the base is overridden to '/' so the Vite proxy works normally
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
