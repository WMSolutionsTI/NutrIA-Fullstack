// API utilitário para chamadas ao backend NutrIA Pro

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function api<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
    credentials: "include",
  });
  if (!res.ok) throw new Error(res.statusText);
  return res.json();
}

// Exemplos de endpoints
export function loginNutri(email: string, senha: string) {
  return api<{ token: string; user: any }>("/nutricionista/login", {
    method: "POST",
    body: JSON.stringify({ email, senha }),
  });
}

export function cadastroNutri(data: any) {
  return api<{ token: string; user: any }>("/nutricionista/cadastro", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function getClientes() {
  return api<any[]>("/api/v1/clientes");
}

export function getCliente(clienteId: number) {
  return api<any>(`/api/v1/clientes/${clienteId}`);
}

export function atualizarCliente(clienteId: number, data: any) {
  return api<any>(`/api/v1/clientes/${clienteId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function ativarCliente(clienteId: number) {
  return api<any>(`/api/v1/clientes/${clienteId}/ativar`, {
    method: "POST",
  });
}

export function novoCliente(data: any) {
  return api<any>("/api/v1/clientes", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function getConversasCliente(clienteId: number) {
  return api<any[]>(`/api/v1/conversas/cliente/${clienteId}`);
}

export function getConversa(conversaId: number) {
  return api<any>(`/api/v1/conversas/${conversaId}`);
}

export function abrirConversaDireta(conversaId: number) {
  return api<any>(`/api/v1/conversas/conversas/${conversaId}/abrir`, {
    method: "POST",
  });
}

export function fecharConversaDireta(conversaId: number) {
  return api<any>(`/api/v1/conversas/conversas/${conversaId}/fechar`, {
    method: "POST",
  });
}

export function criarConversa(data: any) {
  return api<any>("/api/v1/conversas/armazenar", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function uploadArquivo(formData: FormData) {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const res = await fetch(`${API_URL}/api/v1/arquivos/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error(res.statusText);
  return res.json();
}

export function enviarArquivoIA(fileId: number, clienteId: number, contexto: string) {
  return api<any>(`/api/v1/arquivos/enviar_ia`, {
    method: "POST",
    body: JSON.stringify({ file_id: fileId, cliente_id: clienteId, contexto }),
  });
}

export function getArquivosRepository(tenantId: number) {
  return api<any[]>(`/api/v1/arquivos/repository/${tenantId}`);
}

export function enviarArquivoRepositoryParaCliente(arquivoId: number, clienteId: number, accountId: string, conversationId: string) {
  return api<any>(`/api/v1/arquivos/repository/enviar_cliente`, {
    method: "POST",
    body: JSON.stringify({ arquivo_id: arquivoId, cliente_id: clienteId, account_id: accountId, conversation_id: conversationId }),
  });
}


export function getConsultas() {
  return api<any[]>("/nutricionista/consultas");
}

export function novaConsulta(data: any) {
  return api<any>("/nutricionista/consultas", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function getConfiguracoesNutri() {
  return api<any>("/nutricionista/configuracoes");
}

export function salvarConfiguracoesNutri(data: any) {
  return api<any>("/nutricionista/configuracoes", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
// Adicione endpoints para mensagens, campanhas, cobranças, relatórios, configurações etc.
