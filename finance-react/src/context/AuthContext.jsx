import { createContext, useContext, useState, useCallback, useEffect } from 'react'
import { postForm } from '../api'

/**
 * Flask hâlâ session cookie'si ile giriş durumunu tutar.
 * React tarafında arayüz için bir ayna state'i saklarız (localStorage'da).
 * Mount sırasında /api/me ile senkronize edilir — sunucu yeniden başladıysa
 * veya başka bir sekmeden çıkış yapılmışsa tutarsızlık olmasın diye.
 */

const AuthContext = createContext(null)
const STORAGE_KEY = 'finance_auth_v1'

function readStored() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch { return null }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => readStored())

  const save = useCallback(u => {
    if (u) localStorage.setItem(STORAGE_KEY, JSON.stringify(u))
    else localStorage.removeItem(STORAGE_KEY)
    setUser(u)
  }, [])

  // Mount'ta sunucu ile senkronizasyon. /api/me yoksa (eski backend) sessizce yok say.
  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const res = await fetch('/api/me', { credentials: 'include' })
        if (!res.ok) return
        const body = await res.json()
        if (cancelled) return
        if (body?.user) save({ username: body.user.username })
        else save(null)
      } catch { /* endpoint yok veya offline — localStorage'e güven */ }
    })()
    return () => { cancelled = true }
  }, [save])

  const login = useCallback(async (username, password) => {
    const res = await postForm('/login', { username, password })
    // Başarılı giriş -> Flask "/" adresine yönlendirir.
    // Başarısız -> "/login" geri döner.
    const ok = res.ok && !res.url.endsWith('/login')
    if (ok) save({ username })
    return ok
  }, [save])

  const register = useCallback(async ({ username, email, password, confirm }) => {
    const res = await postForm('/register', { username, email, password, confirm })
    // Başarılı kayıt -> /login'e yönlendirilir (giriş değil, sadece kayıt).
    const ok = res.ok && res.url.endsWith('/login')
    return ok
  }, [])

  const logout = useCallback(async () => {
    await fetch('/logout', { credentials: 'include' })
    save(null)
  }, [save])

  return (
    <AuthContext.Provider value={{ user, login, register, logout, setUser: save }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
