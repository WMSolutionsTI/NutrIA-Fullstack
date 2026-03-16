"use client";
import React, { useState } from "react";

interface Mensagem {
  id: string;
  cliente: string;
  canal: string;
  conteudo: string;
  data: string;
  autor: "nutricionista" | "cliente";
}

const MOCK_MENSAGENS: Mensagem[] = [
  { id: "1", cliente: "Maria Silva", canal: "WhatsApp", conteudo: "Olá, gostaria de agendar uma consulta.", data: "2026-03-13 09:00", autor: "cliente" },
  { id: "2", cliente: "Maria Silva", canal: "WhatsApp", conteudo: "Claro, posso te atender amanhã às 10h.", data: "2026-03-13 09:01", autor: "nutricionista" },
];

export default function Mensagens() {
  const [mensagens, setMensagens] = useState<Mensagem[]>(MOCK_MENSAGENS);
  const [novaMensagem, setNovaMensagem] = useState("");

  // Simulação de envio
  const handleEnviar = () => {
    if (!novaMensagem.trim()) return;
    setMensagens([
      ...mensagens,
      {
        id: String(mensagens.length + 1),
        cliente: "Maria Silva",
        canal: "WhatsApp",
        conteudo: novaMensagem,
        data: new Date().toISOString(),
        autor: "nutricionista",
      },
    ]);
    setNovaMensagem("");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-3xl mx-auto bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-8 border border-emerald-100 dark:border-zinc-800 flex flex-col gap-6">
        <h1 className="text-3xl font-bold text-emerald-700 dark:text-emerald-300 mb-2">Central de Mensagens</h1>
        <div className="flex flex-col gap-2 h-80 overflow-y-auto bg-zinc-50 dark:bg-zinc-800 rounded p-4 border border-zinc-100 dark:border-zinc-800">
          {mensagens.map(msg => (
            <div key={msg.id} className={`flex ${msg.autor === "nutricionista" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-xs px-4 py-2 rounded-lg shadow text-sm ${msg.autor === "nutricionista" ? "bg-emerald-500 text-white" : "bg-zinc-200 dark:bg-zinc-700 text-zinc-800 dark:text-zinc-100"}`}>
                <div>{msg.conteudo}</div>
                <div className="text-xs text-zinc-300 mt-1">{msg.data.slice(11, 16)}</div>
              </div>
            </div>
          ))}
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
      </div>
    </div>
  );
}
