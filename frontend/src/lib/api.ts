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
  return api<any[]>("/nutricionista/clientes");
}

export function novoCliente(data: any) {
  return api<any>("/nutricionista/clientes", {
    method: "POST",
    body: JSON.stringify(data),
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
