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
  refresh_token?: string
  token_type: string
  expires_in: number
  user?: UserProfile
}

export interface UserProfile {
  id: string
  email: string
  name: string
  tenant_id: string | number | null
  role: 'owner' | 'admin' | 'nutritionist' | 'nutri' | 'secretaria'
  must_change_password?: boolean
  profile_completed?: boolean
  setup_completed?: boolean
  cpf?: string | null
  cnpj?: string | null
  endereco?: string | null
  telefone?: string | null
}

/** Realiza login e armazena os tokens */
export async function login(credentials: LoginRequest): Promise<UserProfile> {
  const response = await apiClient.post<LoginResponse>('/api/v1/auth/login', credentials, {
    public: true,
  })
  setTokens(response.access_token, response.refresh_token)

  return response.user ?? apiClient.get<UserProfile>('/api/v1/auth/me')
}

/** Remove os tokens e invalida a sessão no servidor */
export async function logout(): Promise<void> {
  try {
    await apiClient.post('/api/v1/auth/logout', {})
  } finally {
    clearTokens()
  }
}

/** Retorna o perfil do usuário autenticado */
export function getMe(): Promise<UserProfile> {
  return apiClient.get<UserProfile>('/api/v1/auth/me')
}

export interface TrialSignupRequest {
  nome: string
  email: string
  telefone: string
}

export interface AssinaturaCheckoutRequest {
  nome: string
  email: string
  plano_nome: string
  valor: number
  documento?: string
  telefone?: string
  billing_type?: 'PIX' | 'BOLETO' | 'CREDIT_CARD'
}

export function solicitarTrial(data: TrialSignupRequest): Promise<{ message: string }> {
  return apiClient.post('/api/v1/onboarding/trial/solicitar', data, { public: true })
}

export function solicitarCheckoutAssinatura(data: AssinaturaCheckoutRequest): Promise<{
  status: string
  pagamento_id: string
  payment_link?: string
  pix_qrcode?: string
}> {
  return apiClient.post('/api/v1/onboarding/assinatura/checkout', data, { public: true })
}

export function obterStatusAssinatura(pagamentoId: string): Promise<{
  pagamento_id: string
  payment_status: string
  provisioned: boolean
  nutricionista_id?: number
  tenant_id?: number
  chatwoot_account?: string
  email: string
  plano_nome: string
}> {
  return apiClient.get(`/api/v1/onboarding/assinatura/status/${pagamentoId}`, { public: true })
}

export function trocarSenhaPrimeiroAcesso(data: {
  senha_atual: string
  nova_senha: string
}): Promise<{ message: string; user: UserProfile }> {
  return apiClient.post('/api/v1/auth/primeiro-acesso/trocar-senha', data)
}

export function completarPerfilPessoal(data: {
  cpf: string
  cnpj?: string
  endereco: string
}): Promise<{ status: string; profile_completed: boolean }> {
  return apiClient.patch('/api/v1/onboarding/perfil/pessoal', data)
}

export function salvarConfiguracaoInicial(data: {
  sobre_nutricionista: string
  tipos_atendimento: string
  especialidade: string
  publico_alvo: string
  periodo_trabalho: string
  disponibilidade_agenda: string
  duracao_consulta_minutos: number
  preco_consulta: string
  pacotes_atendimento: string
  metodo_atendimento: string
  endereco_consulta_presencial?: string
  instagram?: string
  facebook?: string
  telefone_profissional?: string
  site?: string
  contatos_adicionais?: string
  google_agenda_configurada: boolean
  asaas_configurada: boolean
  primeira_inbox_configurada: boolean
}): Promise<{ status: string; setup_completed: boolean }> {
  return apiClient.patch('/api/v1/onboarding/configuracao-inicial', data)
}

export function configurarIntegracaoAsaas(data: {
  api_key: string
  api_url?: string
  webhook_token?: string
  wallet_id?: string
}): Promise<{
  status: string
  escopo: string
  api_url: string
  wallet_id: string
  token: string
  enabled: boolean
}> {
  return apiClient.put('/api/v1/onboarding/integracoes/asaas', data)
}
