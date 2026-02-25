import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'
import { hostname } from 'os'

export default defineConfig({
  plugins: [tailwindcss(), svelte()],
  resolve: {
    alias: {
      '$lib': resolve(__dirname, 'src/lib')
    }
  },
  server: {
    host: true,
    allowedHosts: [hostname()],
    proxy: {
      '/ws': {
        target: 'http://localhost:8000',
        ws: true
      }
    }
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true
  }
})
