import { api } from './client'

export interface RegisterResponse {
  user_id: string
  access_token: string
  refresh_token: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export const authApi = {
  register: (email: string, password: string) =>
    api.post<RegisterResponse>('/auth/register', { email, password }),

  login: (email: string, password: string) =>
    api.post<TokenResponse>('/auth/login', { email, password }),
}
