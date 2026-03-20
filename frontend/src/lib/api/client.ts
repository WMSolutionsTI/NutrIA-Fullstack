/**
 * NutrIA-Pro — API Client
 *
 * Cliente HTTP centralizado para comunicação com o backend (VPS via Cloudflare Tunnel).
 *
 * Funcionalidades:
 * - Base URL configurada via variável de ambiente
 * - Interceptor de requisição: injeta JWT no header Authorization
 * - Interceptor de resposta: trata erros 401 (token expirado) e renova token
 * - Timeout configurável
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
const AUTH_COOKIE = 'nutria_token'

/** Chaves para o localStorage */
const TOKEN_KEY = 'nutria-pro:access_token'
const REFRESH_TOKEN_KEY = 'nutria-pro:refresh_token'

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly detail: string,
    message?: string
  ) {
    super(message ?? detail)
    this.name = 'ApiError'
  }
}

/** Retorna o access token armazenado */
export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(TOKEN_KEY)
}

/** Armazena os tokens de autenticação */
export function setTokens(accessToken: string, refreshToken?: string): void {
  if (typeof window === 'undefined') return
  localStorage.setItem(TOKEN_KEY, accessToken)
  if (refreshToken) {
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
  }
  document.cookie = `${AUTH_COOKIE}=${accessToken}; path=/; SameSite=Lax`
}

/** Remove os tokens (logout) */
export function clearTokens(): void {
  if (typeof window === 'undefined') return
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  document.cookie = `${AUTH_COOKIE}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT`
}

/** Tenta renovar o access token usando o refresh token */
async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
  if (!refreshToken) return null

  try {
    const response = await fetch(`${API_URL}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })

    if (!response.ok) {
      clearTokens()
      return null
    }

    const data = (await response.json()) as { access_token: string }
    setTokens(data.access_token)
    return data.access_token
  } catch {
    clearTokens()
    return null
  }
}

interface RequestOptions extends RequestInit {
  /** Timeout em milissegundos (padrão: 10000) */
  timeout?: number
  /** Se true, não injeta o JWT no header (ex: login, refresh) */
  public?: boolean
}

/**
 * Cliente HTTP principal — wrapper sobre fetch com:
 * - Injeção automática de JWT
 * - Renovação automática de token em caso de 401
 * - Timeout configurável
 * - Tratamento centralizado de erros
 */
async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { timeout = 10_000, public: isPublic = false, ...fetchOptions } = options

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeout)

  const headers = new Headers(fetchOptions.headers)
  headers.set('Content-Type', headers.get('Content-Type') ?? 'application/json')

  if (!isPublic) {
    const token = getAccessToken()
    if (token) {
      headers.set('Authorization', `Bearer ${token}`)
    }
  }

  const url = `${API_URL}${path}`

  let response = await fetch(url, {
    ...fetchOptions,
    headers,
    signal: controller.signal,
  }).finally(() => clearTimeout(timeoutId))

  // Token expirado → tenta renovar e repetir a requisição
  if (response.status === 401 && !isPublic) {
    const newToken = await refreshAccessToken()
    if (newToken) {
      headers.set('Authorization', `Bearer ${newToken}`)
      response = await fetch(url, { ...fetchOptions, headers })
    } else {
      // Não conseguiu renovar → lança erro para que o componente React
      // possa usar o router do Next.js para redirecionar ao login.
      // Evita usar window.location.href diretamente aqui para não bypassar
      // o roteador do Next.js.
      throw new ApiError(401, 'Sessão expirada. Faça login novamente.')
    }
  }

  if (!response.ok) {
    let detail = `HTTP ${response.status}`
    try {
      const body = (await response.json()) as { detail?: string }
      detail = body.detail ?? detail
    } catch {
      // ignora erro de parsing do body
    }
    throw new ApiError(response.status, detail)
  }

  // 204 No Content — sem body
  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

/** API Client com métodos tipados */
export const apiClient = {
  get: <T>(path: string, options?: RequestOptions) =>
    request<T>(path, { ...options, method: 'GET' }),

  post: <T>(path: string, body: unknown, options?: RequestOptions) =>
    request<T>(path, {
      ...options,
      method: 'POST',
      body: JSON.stringify(body),
    }),

  put: <T>(path: string, body: unknown, options?: RequestOptions) =>
    request<T>(path, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(body),
    }),

  patch: <T>(path: string, body: unknown, options?: RequestOptions) =>
    request<T>(path, {
      ...options,
      method: 'PATCH',
      body: JSON.stringify(body),
    }),

  delete: <T>(path: string, options?: RequestOptions) =>
    request<T>(path, { ...options, method: 'DELETE' }),
}

export default apiClient
