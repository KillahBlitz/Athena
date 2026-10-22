import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vitest/config'
// Plugin que Nuxt ya instala para compilar SFC; se reutiliza para montar componentes en pruebas.
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '~': fileURLToPath(new URL('./app', import.meta.url))
    }
  },
  test: {
    environment: 'happy-dom',
    include: ['test/unit/**/*.spec.ts'],
    setupFiles: ['test/setup/waapi.ts']
  }
})
