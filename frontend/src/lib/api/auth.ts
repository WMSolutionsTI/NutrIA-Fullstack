/**
 * NutrIA-Pro — Auth API
 *
 * Funções para autenticação (login, logout, refresh token).
 */

import { apiClient, setTokens, clearTokens } from './client'

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface UserProfile {
  id: string
  email: string
  name: string
  tenant_id: string
  role: 'owner' | 'admin' | 'nutritionist'
}

/** Realiza login e armazena os tokens */
export async function login(credentials: LoginRequest): Promise<UserProfile> {
  const response = await apiClient.post<LoginResponse>('/v1/auth/login', credentials, {
    public: true,
  })
  setTokens(response.access_token, response.refresh_token)

  return apiClient.get<UserProfile>('/v1/auth/me')
}

/** Remove os tokens e invalida a sessão no servidor */
export async function logout(): Promise<void> {
  try {
    await apiClient.post('/v1/auth/logout', {})
  } finally {
    clearTokens()
  }
}

/** Retorna o perfil do usuário autenticado */
export function getMe(): Promise<UserProfile> {
  return apiClient.get<UserProfile>('/v1/auth/me')
}
