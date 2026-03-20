"use client";
import React, { useEffect, useState } from "react";
import { getClientes, getConversasCliente, criarConversa } from "@/lib/api";

interface Cliente {
  id: string;
  nome: string;
  email: string;
  telefone: string;
  status: string;
}

interface Mensagem {
  id: string;
  cliente_id: number;
  conteudo: string;
  data: string;
  autor: "nutricionista" | "cliente";
}

const MOCK_MENSAGENS: Mensagem[] = [
  { id: "1", cliente_id: 1, conteudo: "Olá, gostaria de agendar uma consulta.", data: "2026-03-13 09:00", autor: "cliente" },
  { id: "2", cliente_id: 1, conteudo: "Claro, posso te atender amanhã às 10h.", data: "2026-03-13 09:01", autor: "nutricionista" },
];

export default function Mensagens() {
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [clienteSelecionado, setClienteSelecionado] = useState<Cliente | null>(null);
  const [mensagens, setMensagens] = useState<Mensagem[]>(MOCK_MENSAGENS);
  const [novaMensagem, setNovaMensagem] = useState("");
  const [erro, setErro] = useState("");

  useEffect(() => {
    async function loadClientes() {
      try {
        const dados = await getClientes();
        setClientes(Array.isArray(dados) ? dados : []);
      } catch (e) {
        console.error("Falha ao trazer clientes", e);
      }
    }
    loadClientes();
  }, []);

  useEffect(() => {
    async function loadConversas() {
      if (!clienteSelecionado) return;
      try {
        const conversas = await getConversasCliente(Number(clienteSelecionado.id));
        if (Array.isArray(conversas) && conversas.length > 0) {
          setMensagens(
            conversas.map((c: any) => ({
              id: String(c.id),
              cliente_id: c.cliente_id,
              conteudo: c.mensagem,
              data: c.data ?? new Date().toISOString(),
              autor: "cliente",
            }))
          );
        } else {
          setMensagens(MOCK_MENSAGENS.filter(m => m.cliente_id === Number(clienteSelecionado.id)));
        }
      } catch (e) {
        console.error("Falha ao buscar conversas", e);
      }
    }
    loadConversas();
  }, [clienteSelecionado]);

  const handleEnviar = async () => {
    if (!clienteSelecionado) return setErro("Selecione um cliente primeiro.");
    if (!novaMensagem.trim()) return;

    try {
      setErro("");
      const conversa = await criarConversa({
        cliente_id: Number(clienteSelecionado.id),
        nutricionista_id: 1,
        caixa_id: 1,
        mensagem: novaMensagem,
        modo: "ia",
      });

      setMensagens(prev => [
        ...prev,
        {
          id: String(conversa.id || Date.now()),
          cliente_id: Number(clienteSelecionado.id),
          conteudo: novaMensagem,
          data: new Date().toISOString(),
          autor: "nutricionista",
        },
      ]);
      setNovaMensagem("");
    } catch (e) {
      console.error(e);
      setErro("Erro ao enviar mensagem");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-5xl mx-auto bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-8 border border-emerald-100 dark:border-zinc-800 flex flex-col gap-6">
        <h1 className="text-3xl font-bold text-emerald-700 dark:text-emerald-300 mb-2">Central de Mensagens</h1>

        <label className="block">
          <span className="text-sm font-medium text-zinc-600 dark:text-zinc-300">Selecionar cliente</span>
          <select
            className="mt-1 block w-full rounded-md border-gray-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 px-3 py-2"
            value={clienteSelecionado?.id || ""}
            onChange={e => {
              const id = e.target.value;
              setClienteSelecionado(clientes.find(c => c.id === id) || null);
            }}
          >
            <option value="">-- escolha um cliente --</option>
            {clientes.map(c => (
              <option key={c.id} value={c.id}>
                {c.nome} ({c.status})
              </option>
            ))}
          </select>
        </label>

        <div className="flex flex-col gap-2 h-80 overflow-y-auto bg-zinc-50 dark:bg-zinc-800 rounded p-4 border border-zinc-100 dark:border-zinc-800">
          {mensagens.map(msg => (
            <div key={msg.id} className={`flex ${msg.autor === "nutricionista" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-xs px-4 py-2 rounded-lg shadow text-sm ${msg.autor === "nutricionista" ? "bg-emerald-500 text-white" : "bg-zinc-200 dark:bg-zinc-700 text-zinc-800 dark:text-zinc-100"}`}>
                <div>{msg.conteudo}</div>
                <div className="text-xs text-zinc-300 mt-1">{new Date(msg.data).toLocaleTimeString()}</div>
              </div>
            </div>
          ))}

          {mensagens.length === 0 && <div className="text-center text-zinc-500">Nenhuma conversa encontrada.</div>}
        </div>

        <div className="flex gap-2 mt-2">
          <input
            type="text"
            placeholder="Digite uma mensagem..."
            className="flex-1 rounded px-4 py-2 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800"
            value={novaMensagem}
            onChange={e => setNovaMensagem(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleEnviar()}
          />
          <button onClick={handleEnviar} className="rounded-full bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-2 font-semibold shadow transition-colors">Enviar</button>
        </div>

        {erro && <div className="text-red-600 text-sm">{erro}</div>}
      </div>
    </div>
  );
}
