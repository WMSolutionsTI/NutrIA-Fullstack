"use client";
import React from "react";

const MOCK_RELATORIOS = {
  consultas: 42,
  clientes: 30,
  faturamento: 8200.50,
  engajamento: 87,
  campanhas: 5,
};

export default function Relatorios() {
  return (
    <div className="mx-auto w-full max-w-6xl space-y-6">
      <section className="rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm">
        <h1 className="text-3xl font-black text-zinc-900">Relatórios de Performance</h1>
        <p className="mt-2 text-zinc-600">
          Acompanhe produtividade clínica, crescimento comercial e resultado financeiro em um único painel.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <article className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-zinc-500">Consultas realizadas</p>
          <p className="mt-1 text-3xl font-black text-zinc-900">{MOCK_RELATORIOS.consultas}</p>
        </article>
        <article className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-zinc-500">Clientes ativos</p>
          <p className="mt-1 text-3xl font-black text-zinc-900">{MOCK_RELATORIOS.clientes}</p>
        </article>
        <article className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-zinc-500">Faturamento mensal</p>
          <p className="mt-1 text-3xl font-black text-zinc-900">R$ {MOCK_RELATORIOS.faturamento.toFixed(2)}</p>
        </article>
      </section>

      <section className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <article className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-zinc-900">Indicadores de atendimento</h2>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Engajamento</p>
              <p className="mt-1 text-2xl font-black text-emerald-700">{MOCK_RELATORIOS.engajamento}%</p>
            </div>
            <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Campanhas enviadas</p>
              <p className="mt-1 text-2xl font-black text-cyan-700">{MOCK_RELATORIOS.campanhas}</p>
            </div>
          </div>
        </article>

        <article className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-zinc-900">Ações recomendadas</h2>
          <ul className="mt-4 space-y-2 text-sm text-zinc-700">
            <li className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5">
              Reativar clientes sem retorno há mais de 30 dias.
            </li>
            <li className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5">
              Executar campanha segmentada para plano premium.
            </li>
            <li className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5">
              Publicar slots vagos na agenda automática.
            </li>
          </ul>
        </article>
      </section>
    </div>
  );
}
