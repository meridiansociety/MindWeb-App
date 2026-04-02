import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi } from '../api/auth'
import { useAuthStore } from '../store/authStore'

export function useAuth() {
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const setTokens = useAuthStore((s) => s.setTokens)
  const logout = useAuthStore((s) => s.logout)

  const login = async (email: string, password: string) => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await authApi.login(email, password)
      setTokens(data.access_token, data.refresh_token)
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  const register = async (email: string, password: string) => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await authApi.register(email, password)
      setTokens(data.access_token, data.refresh_token, data.user_id)
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  const signOut = () => {
    logout()
    navigate('/login')
  }

  return { login, register, signOut, loading, error }
}
