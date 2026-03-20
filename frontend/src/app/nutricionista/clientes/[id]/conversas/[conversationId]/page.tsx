"use client";
import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
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
    return <div className="p-8">Carregando conversa...</div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-4xl mx-auto bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-8 border border-emerald-100 dark:border-zinc-800">
        <h1 className="text-3xl font-bold text-emerald-700 dark:text-emerald-300 mb-6">Conversa #{conversaId}</h1>
        <p className="text-zinc-700 dark:text-zinc-200 mb-2"><strong>Cliente ID:</strong> {conversa.cliente_id} / Nutricionista ID: {conversa.nutricionista_id}</p>
        <p className="text-zinc-700 dark:text-zinc-200 mb-4"><strong>Modo:</strong> {conversa.modo} / <strong>Direto:</strong> {conversa.em_conversa_direta ? "Sim" : "Não"}</p>
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-1">Mensagem</h2>
          <div className="p-4 bg-zinc-50 dark:bg-zinc-800 rounded">{conversa.mensagem}</div>
        </div>

        {erro && <div className="mb-2 text-sm text-red-600">{erro}</div>}
        {sucesso && <div className="mb-2 text-sm text-green-600">{sucesso}</div>}

        <button onClick={handleFechar} className="rounded bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 font-semibold shadow">
          Fechar atendimento direto e retornar à secretária
        </button>
      </div>
    </div>
  );
}
