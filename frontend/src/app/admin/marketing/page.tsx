"use client";

import React, { useMemo, useState } from "react";

export default function CampanhasMarketing() {
  const [campanhas, setCampanhas] = useState([
    { nome: "Promoção de Lançamento", canal: "WhatsApp", status: "Ativa", conversao: 22 },
    { nome: "Webinar NutrIA-Pro", canal: "Instagram", status: "Finalizada", conversao: 15 },
  ]);
  const [novaCampanha, setNovaCampanha] = useState("");
  const [novoCanal, setNovoCanal] = useState("");

  const adicionarCampanha = () => {
    if (!novaCampanha || !novoCanal) return;
    setCampanhas((prev) => [...prev, { nome: novaCampanha, canal: novoCanal, status: "Ativa", conversao: 0 }]);
    setNovaCampanha("");
    setNovoCanal("");
  };

  const taxaMedia = useMemo(
    () => (campanhas.length ? Math.round(campanhas.reduce((acc, c) => acc + c.conversao, 0) / campanhas.length) : 0),
    [campanhas]
  );

  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-zinc-200 bg-white p-7 shadow-sm">
        <h1 className="text-3xl font-black text-zinc-900">Marketing e Campanhas</h1>
        <p className="mt-2 text-zinc-600">Engine comercial para aquisição, conversão e retenção de clientes em escala.</p>
      </section>

      <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-bold text-zinc-900">Criar campanha</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-[1fr_1fr_auto]">
          <input
            value={novaCampanha}
            onChange={(e) => setNovaCampanha(e.target.value)}
            placeholder="Nome da campanha"
            className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-cyan-300"
          />
          <input
            value={novoCanal}
            onChange={(e) => setNovoCanal(e.target.value)}
            placeholder="Canal"
            className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-cyan-300"
          />
          <button onClick={adicionarCampanha} className="rounded-xl bg-zinc-900 hover:bg-zinc-800 text-white px-4 py-2.5 text-sm font-semibold">
            Adicionar
          </button>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <article className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-zinc-500">Campanhas ativas</p>
          <p className="text-3xl font-black text-zinc-900">{campanhas.filter((c) => c.status === "Ativa").length}</p>
        </article>
        <article className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-zinc-500">Taxa média de conversão</p>
          <p className="text-3xl font-black text-zinc-900">{taxaMedia}%</p>
        </article>
        <article className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-zinc-500">Automação de IA</p>
          <p className="text-sm font-semibold text-emerald-700 mt-1">Segmentação e disparo inteligente ativos</p>
        </article>
      </section>

      <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        <div className="overflow-x-auto rounded-xl border border-zinc-200">
          <table className="min-w-full text-left">
            <thead className="bg-zinc-100">
              <tr className="text-sm text-zinc-700">
                <th className="px-4 py-3">Campanha</th>
                <th className="px-4 py-3">Canal</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Conversão</th>
              </tr>
            </thead>
            <tbody>
              {campanhas.map((c) => (
                <tr key={`${c.nome}-${c.canal}`} className="border-t border-zinc-200 text-sm text-zinc-700">
                  <td className="px-4 py-3 font-semibold text-zinc-900">{c.nome}</td>
                  <td className="px-4 py-3">{c.canal}</td>
                  <td className="px-4 py-3">{c.status}</td>
                  <td className="px-4 py-3">{c.conversao}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
