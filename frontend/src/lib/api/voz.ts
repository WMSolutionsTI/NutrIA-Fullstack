import { apiClient } from "@/lib/api/client";

export interface VoiceHandoff {
  call_id: number;
  cliente_id: number;
  cliente_nome?: string | null;
  status: string;
  motivo: string;
  quando?: string | null;
  conversa_id?: number | null;
  conversa_link: string;
}

export function listVoiceHandoffs(limit = 20) {
  return apiClient.get<VoiceHandoff[]>(`/api/v1/voz/handoffs?limit=${limit}`);
}

