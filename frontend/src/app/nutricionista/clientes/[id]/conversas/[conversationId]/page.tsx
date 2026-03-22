"use client";

import Link from "next/link";
import React, { useEffect, useState } from "react";
import { getConversa, fecharConversaDireta } from "@/lib/api";

export default function ConversaDetalhe({ params }: { params: { id: string; conversationId: string } }) {
  const clienteId = Number(params.id);
  const conversaId = Number(params.conversationId);
  const [conversa, setConversa] = useState<any>(null);
  const [erro, setErro] = useState("");
  const [sucesso, setSucesso] = useState("");

  useEffect(() => {
    async function fetchConversa() {
      try {
        const dados = await getConversa(conversaId);
        setConversa(dados);
      } catch (e) {
        console.error(e);
        setErro("Falha ao carregar conversa");
      }
    }
    fetchConversa();
  }, [conversaId]);

  const handleFechar = async () => {
    setErro("");
    setSucesso("");
    try {
      await fecharConversaDireta(conversaId);
      setSucesso("Conversa direcionada ao modo IA e retorno à secretária realizado.");
      const dados = await getConversa(conversaId);
      setConversa(dados);
    } catch (e) {
      console.error(e);
      setErro("Falha ao finalizar conversa");
    }
  };

  if (!conversa) {
    return <div className="p-8 text-sm text-zinc-600">Carregando conversa...</div>;
  }

  return (
    <div className="mx-auto w-full max-w-5xl space-y-6">
      <section className="rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm">
        <h1 className="text-3xl font-black text-zinc-900">Conversa #{conversaId}</h1>
        <p className="mt-2 text-zinc-600">
          Acompanhe o atendimento direto e retorne o fluxo para secretária IA quando necessário.
        </p>
      </section>

      <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        <div className="grid gap-3 rounded-xl border border-zinc-200 bg-zinc-50 p-4 text-sm text-zinc-700 md:grid-cols-2">
          <p><strong>Cliente ID:</strong> {conversa.cliente_id}</p>
          <p><strong>Nutricionista ID:</strong> {conversa.nutricionista_id}</p>
          <p><strong>Modo:</strong> {conversa.modo}</p>
          <p><strong>Direto:</strong> {conversa.em_conversa_direta ? "Sim" : "Não"}</p>
        </div>

        <div className="mt-4 rounded-xl border border-zinc-200 bg-zinc-50 p-4">
          <h2 className="text-sm font-semibold text-zinc-700">Mensagem</h2>
          <p className="mt-2 text-sm text-zinc-800">{conversa.mensagem}</p>
        </div>

        {erro && <div className="mt-4 rounded-xl bg-rose-50 px-3 py-2 text-sm font-semibold text-rose-700">{erro}</div>}
        {sucesso && <div className="mt-4 rounded-xl bg-emerald-50 px-3 py-2 text-sm font-semibold text-emerald-700">{sucesso}</div>}

        <div className="mt-5 flex flex-wrap gap-3">
          <button onClick={handleFechar} className="rounded-xl bg-cyan-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-cyan-700">
            Fechar atendimento direto
          </button>
          <Link href={`/nutricionista/clientes/${clienteId}`} className="rounded-xl border border-zinc-300 bg-white px-5 py-2.5 text-sm font-semibold text-zinc-700 hover:bg-zinc-50">
            Voltar ao cliente
          </Link>
        </div>
      </section>
    </div>
  );
}
