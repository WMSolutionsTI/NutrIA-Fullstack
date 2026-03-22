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
          setMensagens(MOCK_MENSAGENS.filter((m) => m.cliente_id === Number(clienteSelecionado.id)));
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
    <div className="mx-auto w-full max-w-6xl space-y-6">
      <section className="rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm">
        <h1 className="text-3xl font-black text-zinc-900">Central de Mensagens</h1>
        <p className="mt-2 text-zinc-600">
          Atendimento em tempo real com histórico unificado entre nutricionista, secretária e cliente.
        </p>
      </section>

      <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        <label className="block">
          <span className="text-sm font-medium text-zinc-600">Selecionar cliente</span>
          <select
            className="mt-1 block w-full rounded-xl border border-zinc-200 bg-zinc-50 px-3 py-2.5 text-sm md:max-w-md"
            value={clienteSelecionado?.id || ""}
            onChange={(e) => {
              const id = e.target.value;
              setClienteSelecionado(clientes.find((c) => c.id === id) || null);
            }}
          >
            <option value="">-- escolha um cliente --</option>
            {clientes.map((c) => (
              <option key={c.id} value={c.id}>
                {c.nome} ({c.status})
              </option>
            ))}
          </select>
        </label>

        <div className="mt-4 flex h-96 flex-col gap-2 overflow-y-auto rounded-xl border border-zinc-200 bg-zinc-50 p-4">
          {mensagens.map((msg) => (
            <div key={msg.id} className={`flex ${msg.autor === "nutricionista" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-xs rounded-lg px-4 py-2 text-sm shadow ${
                  msg.autor === "nutricionista" ? "bg-emerald-500 text-white" : "bg-white text-zinc-800"
                }`}
              >
                <div>{msg.conteudo}</div>
                <div className="mt-1 text-xs text-zinc-300">{new Date(msg.data).toLocaleTimeString()}</div>
              </div>
            </div>
          ))}

          {mensagens.length === 0 && <div className="text-center text-zinc-500">Nenhuma conversa encontrada.</div>}
        </div>

        <div className="mt-3 flex gap-2">
          <input
            type="text"
            placeholder="Digite uma mensagem..."
            className="flex-1 rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm"
            value={novaMensagem}
            onChange={(e) => setNovaMensagem(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleEnviar()}
          />
          <button onClick={handleEnviar} className="rounded-xl bg-emerald-500 px-6 py-2.5 text-sm font-semibold text-white hover:bg-emerald-600">
            Enviar
          </button>
        </div>

        {erro && <div className="mt-3 rounded-xl bg-rose-50 px-3 py-2 text-sm font-semibold text-rose-700">{erro}</div>}
      </section>
    </div>
  );
}
