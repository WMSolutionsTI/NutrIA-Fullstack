"use client";
import React, { useEffect, useState } from "react";
import Link from "next/link";
import { getCliente, atualizarCliente, ativarCliente, getConversasCliente } from "@/lib/api";

export default function ClienteDetalhe({ params }: { params: { id: string } }) {
  const clienteId = Number(params.id);
  const [cliente, setCliente] = useState<any>(null);
  const [conversas, setConversas] = useState<any[]>([]);
  const [statusNovo, setStatusNovo] = useState("cliente_potencial");
  const [erro, setErro] = useState("");
  const [sucesso, setSucesso] = useState("");

  useEffect(() => {
    async function fetchDados() {
      try {
        const dados = await getCliente(clienteId);
        setCliente(dados);
      } catch (e) {
        console.error(e);
        setErro("Falha ao buscar cliente");
      }

      try {
        const conv = await getConversasCliente(clienteId);
        setConversas(Array.isArray(conv) ? conv : []);
      } catch (e) {
        console.error(e);
      }
    }
    fetchDados();
  }, [clienteId]);

  const atualizarStatus = async (status: string) => {
    setErro("");
    setSucesso("");
    try {
      if (status === "cliente_ativo") {
        await ativarCliente(clienteId);
      } else {
        await atualizarCliente(clienteId, { status });
      }
      setStatusNovo(status);
      setSucesso(`Status atualizado para ${status}`);
      const updated = await getCliente(clienteId);
      setCliente(updated);
    } catch (e) {
      console.error(e);
      setErro("Falha ao atualizar status");
    }
  };

  if (!cliente) {
    return <div className="p-8">Carregando cliente...</div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-4xl mx-auto bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-8 border border-emerald-100 dark:border-zinc-800">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-emerald-700 dark:text-emerald-300 mb-4">{cliente.nome || `Cliente #${clienteId}`}</h1>
          <Link className="rounded bg-blue-500 hover:bg-blue-600 text-white px-4 py-2" href={`/nutricionista/clientes/${clienteId}/upload`}>
            Upload de arquivo
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <p className="text-zinc-700 dark:text-zinc-200"><strong>E-mail:</strong> {cliente.email}</p>
            <p className="text-zinc-700 dark:text-zinc-200"><strong>Telefone:</strong> {cliente.telefone}</p>
            <p className="text-zinc-700 dark:text-zinc-200"><strong>Status:</strong> {cliente.status}</p>
            <p className="text-zinc-700 dark:text-zinc-200"><strong>Nutricionista ID:</strong> {cliente.nutricionista_id}</p>
          </div>
          <div>
            <p className="text-zinc-700 dark:text-zinc-200"><strong>Cadastro:</strong> {cliente.created_at || "Não disponível"}</p>
            <p className="text-zinc-700 dark:text-zinc-200"><strong>Observações:</strong> {cliente.historico || "Nenhuma"}</p>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 mb-4">
          {["cliente_potencial", "cliente_ativo", "cliente_inativo", "cliente_satisfeito", "nutri", "em_atendimento_direto"].map(status => (
            <button
              key={status}
              onClick={() => atualizarStatus(status)}
              className="rounded bg-emerald-500 hover:bg-emerald-600 text-white px-3 py-2 text-sm"
            >
              {status}
            </button>
          ))}
        </div>

        {erro && <div className="mb-2 text-sm text-red-600">{erro}</div>}
        {sucesso && <div className="mb-2 text-sm text-green-600">{sucesso}</div>}

        <div className="mb-4">
          <h2 className="text-2xl font-semibold text-emerald-700 dark:text-emerald-300">Conversas</h2>
          {conversas.length === 0 && <p>Nenhuma conversa encontrada.</p>}
          {conversas.length > 0 && (
            <ul className="space-y-2 mt-2">
              {conversas.map(conv => (
                <li key={conv.id} className="border p-3 rounded bg-zinc-50 dark:bg-zinc-800">
                  <div className="text-sm text-zinc-500">{new Date(conv.data || Date.now()).toLocaleString()}</div>
                  <div className="text-md">{conv.mensagem}</div>
                  <div className="text-xs text-zinc-400 mt-1">Modo: {conv.modo || "ia"}</div>
                  <div className="mt-2">
                    <Link href={`/nutricionista/clientes/${clienteId}/conversas/${conv.id}`} className="text-blue-600 hover:underline text-sm">
                      Abrir conversa no painel de atendimento
                    </Link>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

