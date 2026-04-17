import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Dev proxy: tüm cookie-tabanlı ve API çağrılarını aynı origin'e yönlendirir,
// böylece Flask session cookie'si sorunsuz çalışır.
const FLASK = 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api':              { target: FLASK, changeOrigin: true },
      '/asset':            { target: FLASK, changeOrigin: true },
      '/assets':           { target: FLASK, changeOrigin: true },
      '/login':            { target: FLASK, changeOrigin: true },
      '/register':         { target: FLASK, changeOrigin: true },
      '/logout':           { target: FLASK, changeOrigin: true },
      '/add_comment':      { target: FLASK, changeOrigin: true },
      '/like_comment':     { target: FLASK, changeOrigin: true },
      '/dislike_comment':  { target: FLASK, changeOrigin: true },
      '/delete_comment':   { target: FLASK, changeOrigin: true },
      '/follow':           { target: FLASK, changeOrigin: true },
      '/unfollow':         { target: FLASK, changeOrigin: true },
      '/profile':          { target: FLASK, changeOrigin: true },
      '/set_alarm':        { target: FLASK, changeOrigin: true },
      '/clear_alarm':      { target: FLASK, changeOrigin: true },
      '/static':           { target: FLASK, changeOrigin: true }
    }
  }
})
