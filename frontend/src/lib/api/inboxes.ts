import { apiClient } from "@/lib/api/client";

export interface InboxResumo {
  nutricionista_id: number;
  tenant_id: number | null;
  plano: string;
  chatwoot_account_id: string;
  chatwoot_instance: string;
  limite_inboxes_base: number;
  inboxes_extra: number;
  limite_total: number;
  em_uso: number;
  disponiveis: number;
}

export interface Inbox {
  id: number;
  tipo: string;
  identificador_chatwoot: string;
  status: string;
  data_aquisicao: string | null;
  nutricionista_id: number;
}

export interface InboxPendencia {
  id: number;
  status: string;
  tipo: string;
  nutricionista_id: number;
  tenant_id: number;
  detalhes?: {
    caixa_id?: number;
    tipo?: string;
    identificador?: string;
    detalhes_integracao?: Record<string, unknown>;
    descricao_raw?: string;
  } | null;
  criado_em: string | null;
  atualizado_em: string | null;
}

export interface CriarInboxRequest {
  tipo: string;
  identificador_chatwoot?: string;
  detalhes_integracao?: Record<string, unknown>;
}

export interface CriarInboxResponse {
  id: number;
  status: string;
  nutricionista_id: number;
  limite_total: number;
  em_uso: number;
}

export interface ComprarInboxExtraRequest {
  quantidade: number;
}

export interface ComprarInboxExtraResponse {
  status: string;
  quantidade_adquirida: number;
  novo_limite_total: number;
}

export function getInboxResumo() {
  return apiClient.get<InboxResumo>("/api/v1/caixas/resumo");
}

export function listInboxes() {
  return apiClient.get<Inbox[]>("/api/v1/caixas");
}

export function listInboxPendencias() {
  return apiClient.get<InboxPendencia[]>("/api/v1/caixas/pendencias");
}

export function createInbox(data: CriarInboxRequest) {
  return apiClient.post<CriarInboxResponse>("/api/v1/caixas", data);
}

export function comprarInboxExtra(data: ComprarInboxExtraRequest) {
  return apiClient.post<ComprarInboxExtraResponse>("/api/v1/caixas/extras/comprar", data);
}
