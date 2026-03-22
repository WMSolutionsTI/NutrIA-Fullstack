"use client";

import React, { useState } from "react";

export default function RelatoriosAnalyticsAdmin() {
  const [metricas] = useState({ vendas: 120, receita: 15000, clientes: 420, engajamento: 88 });
  const [insights] = useState([
    "Maior taxa de conversão em campanhas de WhatsApp.",
    "Clientes ativos aumentaram 12% no último ciclo mensal.",
    "Webinar de autoridade trouxe 30 novas assinaturas qualificadas.",
  ]);

  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-zinc-200 bg-white p-7 shadow-sm">
        <h1 className="text-3xl font-black text-zinc-900">Relatórios e Analytics</h1>
        <p className="mt-2 text-zinc-600">
          Inteligência estratégica para decisões de produto, vendas e retenção.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-4">
        {[
          { label: "Vendas", value: metricas.vendas },
          { label: "Receita", value: `R$ ${metricas.receita}` },
          { label: "Clientes", value: metricas.clientes },
          { label: "Engajamento", value: `${metricas.engajamento}%` },
        ].map((item) => (
          <article key={item.label} className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-zinc-500">{item.label}</p>
            <p className="mt-1 text-3xl font-black text-zinc-900">{item.value}</p>
          </article>
        ))}
      </section>

      <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-bold text-zinc-900">Insights de negócio</h2>
        <ul className="mt-4 space-y-2">
          {insights.map((insight) => (
            <li key={insight} className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-3 text-sm text-zinc-700">
              {insight}
            </li>
          ))}
        </ul>
      </section>

      <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-zinc-900">Exportação inteligente</h2>
          <p className="text-sm text-zinc-600 mt-1">Gerar relatórios executivos para board, financeiro e growth.</p>
        </div>
        <button className="rounded-xl bg-zinc-900 hover:bg-zinc-800 text-white px-4 py-2.5 text-sm font-semibold">
          Exportar relatórios
        </button>
      </section>
    </div>
  );
}
