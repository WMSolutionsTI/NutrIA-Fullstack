import { apiClient } from "@/lib/api/client";

export interface GoogleIntegracaoStatus {
  conectado: boolean;
  google_email?: string;
  calendar_id?: string;
  expira_em?: string | null;
}

export interface GoogleIntegracaoIniciar {
  auth_url: string;
  state: string;
}

export interface AgendaEvento {
  id: number;
  cliente_id?: number | null;
  titulo: string;
  descricao?: string | null;
  inicio_em: string;
  fim_em: string;
  status: string;
  google_event_id?: string | null;
}

export interface CriarAgendaEventoRequest {
  titulo: string;
  descricao?: string;
  inicio_em: string;
  fim_em: string;
  cliente_id?: number;
}

export interface AtualizarAgendaEventoRequest {
  titulo?: string;
  descricao?: string;
  inicio_em?: string;
  fim_em?: string;
  status?: string;
}

export function getGoogleIntegracaoStatus() {
  return apiClient.get<GoogleIntegracaoStatus>("/api/v1/integracoes/google/status");
}

export function iniciarGoogleIntegracao() {
  return apiClient.post<GoogleIntegracaoIniciar>("/api/v1/integracoes/google/iniciar", {});
}

export function desconectarGoogleIntegracao() {
  return apiClient.post<{ status: string }>("/api/v1/integracoes/google/desconectar", {});
}

export function listAgendaEventos() {
  return apiClient.get<AgendaEvento[]>("/api/v1/agenda/eventos");
}

export function getAgendaEvento(id: number) {
  return apiClient.get<AgendaEvento>(`/api/v1/agenda/eventos/${id}`);
}

export function createAgendaEvento(data: CriarAgendaEventoRequest) {
  return apiClient.post<{ status: string; evento_id: number; google_event_id?: string }>(
    "/api/v1/agenda/eventos",
    data
  );
}

export function patchAgendaEvento(id: number, data: AtualizarAgendaEventoRequest) {
  return apiClient.patch<{ status: string; evento_id: number }>(
    `/api/v1/agenda/eventos/${id}`,
    data
  );
}

export function deleteAgendaEvento(id: number) {
  return apiClient.delete<{ status: string; evento_id: number }>(`/api/v1/agenda/eventos/${id}`);
}
