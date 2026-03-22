"use client";

import React, { useMemo, useState } from "react";

export default function GestaoMensagens() {
  const [mensagens] = useState([
    { canal: "WhatsApp", conteudo: "Bem-vindo ao NutrIA Pro!", status: "Enviada", engajamento: 80 },
    { canal: "Instagram", conteudo: "Participe do webinar!", status: "Enviada", engajamento: 65 },
    { canal: "Telegram", conteudo: "Reagende sua consulta aqui.", status: "Pendente", engajamento: 40 },
  ]);
  const [filtro, setFiltro] = useState("");

  const mensagensFiltradas = useMemo(
    () => (filtro ? mensagens.filter((m) => m.conteudo.toLowerCase().includes(filtro.toLowerCase())) : mensagens),
    [filtro, mensagens]
  );

  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-zinc-200 bg-white p-7 shadow-sm">
        <h1 className="text-3xl font-black text-zinc-900">Gestão de Mensagens</h1>
        <p className="mt-2 text-zinc-600">Operação omnicanal com foco em engajamento, resposta e conversão comercial.</p>
      </section>

      <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <input
            value={filtro}
            onChange={(e) => setFiltro(e.target.value)}
            placeholder="Filtrar por conteúdo"
            className="w-full md:max-w-xs rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-cyan-300"
          />
          <div className="rounded-xl bg-zinc-900 text-white px-3 py-2 text-xs font-semibold">
            IA ativa para sugestões e follow-up
          </div>
        </div>

        <div className="mt-5 overflow-x-auto rounded-xl border border-zinc-200">
          <table className="min-w-full text-left">
            <thead className="bg-zinc-100">
              <tr className="text-sm text-zinc-700">
                <th className="px-4 py-3">Canal</th>
                <th className="px-4 py-3">Conteúdo</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Engajamento</th>
              </tr>
            </thead>
            <tbody>
              {mensagensFiltradas.map((m) => (
                <tr key={`${m.canal}-${m.conteudo}`} className="border-t border-zinc-200 text-sm text-zinc-700">
                  <td className="px-4 py-3 font-semibold text-zinc-900">{m.canal}</td>
                  <td className="px-4 py-3">{m.conteudo}</td>
                  <td className="px-4 py-3">{m.status}</td>
                  <td className="px-4 py-3">{m.engajamento}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
