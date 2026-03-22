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
    return <div className="p-8 text-sm text-zinc-600">Carregando cliente...</div>;
  }

  return (
    <div className="mx-auto w-full max-w-6xl space-y-6">
      <section className="rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-3xl font-black text-zinc-900">{cliente.nome || `Cliente #${clienteId}`}</h1>
            <p className="mt-2 text-zinc-600">Ficha completa de atendimento, status comercial e histórico de conversas.</p>
          </div>
          <Link className="rounded-xl bg-cyan-600 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-700" href={`/nutricionista/clientes/${clienteId}/upload`}>
            Upload de arquivo
          </Link>
        </div>
      </section>

      <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2 rounded-xl border border-zinc-200 bg-zinc-50 p-4 text-sm text-zinc-700">
            <p><strong>E-mail:</strong> {cliente.email}</p>
            <p><strong>Telefone:</strong> {cliente.telefone}</p>
            <p><strong>Status:</strong> {cliente.status}</p>
            <p><strong>Nutricionista ID:</strong> {cliente.nutricionista_id}</p>
          </div>
          <div className="space-y-2 rounded-xl border border-zinc-200 bg-zinc-50 p-4 text-sm text-zinc-700">
            <p><strong>Cadastro:</strong> {cliente.created_at || "Não disponível"}</p>
            <p><strong>Observações:</strong> {cliente.historico || "Nenhuma"}</p>
          </div>
        </div>

        <div className="mt-5 flex flex-wrap gap-2">
          {["cliente_potencial", "cliente_ativo", "cliente_inativo", "cliente_satisfeito", "nutri", "em_atendimento_direto"].map((status) => (
            <button
              key={status}
              onClick={() => atualizarStatus(status)}
              className="rounded-xl bg-emerald-500 px-3 py-2 text-xs font-semibold text-white hover:bg-emerald-600"
            >
              {status}
            </button>
          ))}
        </div>

        {erro && <div className="mt-4 rounded-xl bg-rose-50 px-3 py-2 text-sm font-semibold text-rose-700">{erro}</div>}
        {sucesso && <div className="mt-4 rounded-xl bg-emerald-50 px-3 py-2 text-sm font-semibold text-emerald-700">{sucesso}</div>}
      </section>

      <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
          <h2 className="text-2xl font-bold text-zinc-900">Conversas</h2>
          {conversas.length === 0 && <p className="mt-2 text-sm text-zinc-500">Nenhuma conversa encontrada.</p>}
          {conversas.length > 0 && (
            <ul className="space-y-2 mt-2">
              {conversas.map((conv) => (
                <li key={conv.id} className="rounded-xl border border-zinc-200 bg-zinc-50 p-3">
                  <div className="text-sm text-zinc-500">{new Date(conv.data || Date.now()).toLocaleString()}</div>
                  <div className="text-sm text-zinc-800">{conv.mensagem}</div>
                  <div className="mt-1 text-xs text-zinc-500">Modo: {conv.modo || "ia"}</div>
                  <div className="mt-2">
                    <Link href={`/nutricionista/clientes/${clienteId}/conversas/${conv.id}`} className="text-sm font-semibold text-cyan-700 hover:text-cyan-800">
                      Abrir conversa no painel de atendimento
                    </Link>
                  </div>
                </li>
              ))}
            </ul>
          )}
      </section>
    </div>
  );
}
