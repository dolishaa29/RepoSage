import react, { reactCompilerPreset } from '@vitejs/plugin-react'
import babel from '@rolldown/plugin-babel'
import { defineConfig, loadEnv } from 'vite'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backend = env.VITE_BACKEND_URL || 'http://localhost:8000'

  return {
    plugins: [
      react(),
      babel({ presets: [reactCompilerPreset()] })
    ],
    server: {
      // forward API routes to FastAPI during development
      proxy: {
        '/register': { target: backend, changeOrigin: true },
        '/login': { target: backend, changeOrigin: true },
        '/me': { target: backend, changeOrigin: true },
        '/github': { target: backend, changeOrigin: true },
        '/reviews': { target: backend, changeOrigin: true },
      },
    },
  }
})
