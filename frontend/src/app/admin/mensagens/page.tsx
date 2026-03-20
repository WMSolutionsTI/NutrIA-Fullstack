"use client";
import React, { useState } from "react";

export default function GestaoMensagens() {
  // Simulação de mensagens
  const [mensagens, setMensagens] = useState([
    { canal: "WhatsApp", conteudo: "Bem-vindo ao NutrIA Pro!", status: "Enviada", engajamento: 80 },
    { canal: "Instagram", conteudo: "Participe do webinar!", status: "Enviada", engajamento: 65 },
  ]);
  const [filtro, setFiltro] = useState("");

  // Filtragem
  const mensagensFiltradas = filtro ? mensagens.filter(m => m.conteudo.toLowerCase().includes(filtro.toLowerCase())) : mensagens;

  // Simulação de automação IA
  const automacaoIA = "IA ativa: monitora mensagens, ajusta conteúdo, dispara follow-ups e analisa engajamento.";

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 via-white to-pink-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-blue-700 dark:text-blue-300 mb-8">Gestão de Mensagens</h1>
        {/* Filtros */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Filtrar Mensagens</h2>
          <div className="flex gap-4">
            <input value={filtro} onChange={e => setFiltro(e.target.value)} placeholder="Conteúdo da mensagem" className="input" />
          </div>
        </section>
        {/* Tabela de mensagens */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Mensagens Enviadas</h2>
          <table className="w-full bg-white dark:bg-zinc-900 rounded shadow">
            <thead>
              <tr>
                <th className="py-2 px-4">Canal</th>
                <th className="py-2 px-4">Conteúdo</th>
                <th className="py-2 px-4">Status</th>
                <th className="py-2 px-4">Engajamento (%)</th>
              </tr>
            </thead>
            <tbody>
              {mensagensFiltradas.map((m, idx) => (
                <tr key={idx}>
                  <td className="py-2 px-4">{m.canal}</td>
                  <td className="py-2 px-4">{m.conteudo}</td>
                  <td className="py-2 px-4">{m.status}</td>
                  <td className="py-2 px-4">{m.engajamento}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
        {/* Automação IA */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Automação IA</h2>
          <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
            <p>{automacaoIA}</p>
            <p>Integração Chatwoot e n8n: <span className="font-bold">Ativa</span></p>
          </div>
        </section>
      </div>
    </div>
  );
}

// Estilos básicos para inputs
// Adicione ao seu CSS global:
// .input { border-radius: 0.5rem; border: 1px solid #d1d5db; padding: 0.5rem; background: #fff; color: #222; }
// .input:focus { outline: none; border-color: #3b82f6; background: #f0f6ff; }