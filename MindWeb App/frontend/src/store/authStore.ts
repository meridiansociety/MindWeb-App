import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  userId: string | null
  setTokens: (access: string, refresh: string, userId?: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      userId: null,

      setTokens: (access, refresh, userId) =>
        set({ accessToken: access, refreshToken: refresh, userId: userId ?? null }),

      logout: () =>
        set({ accessToken: null, refreshToken: null, userId: null }),
    }),
    { name: 'mindweb-auth' }
  )
)
