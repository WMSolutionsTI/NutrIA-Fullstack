"use client";

import React, { useState } from "react";

export default function RelatoriosMetricas() {
  const [metricas] = useState({
    peso: [70, 69, 68.5],
    imc: [24, 23.8, 23.5],
    exames: ["Hemograma OK", "Ferritina baixa"],
    adesao: 85,
    engajamento: 90,
  });
  const [alertas] = useState(["Atenção: ferritina abaixo do ideal", "Meta de peso atingida!"]);
  const [historico] = useState(["Consulta 01/03/2026", "Exame 10/03/2026", "Plano alimentar atualizado 12/03/2026"]);

  return (
    <div className="mx-auto w-full max-w-6xl space-y-6">
      <section className="rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm">
        <h1 className="text-3xl font-black text-zinc-900">Métricas Clínicas</h1>
        <p className="mt-2 text-zinc-600">
          Monitore evolução dos clientes com leitura rápida de adesão, exames e pontos de atenção.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <article className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-zinc-500">Peso recente</p>
          <ul className="mt-2 space-y-1 text-sm font-semibold text-zinc-700">
            {metricas.peso.map((p, idx) => (
              <li key={idx}>{p} kg</li>
            ))}
          </ul>
        </article>
        <article className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-zinc-500">IMC recente</p>
          <ul className="mt-2 space-y-1 text-sm font-semibold text-zinc-700">
            {metricas.imc.map((i, idx) => (
              <li key={idx}>{i}</li>
            ))}
          </ul>
        </article>
      </section>

      <section className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <article className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-zinc-900">Exames e alertas</h2>
          <div className="mt-4 grid gap-3">
            <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Exames</p>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-zinc-700">
                {metricas.exames.map((e) => (
                  <li key={e}>{e}</li>
                ))}
              </ul>
            </div>
            <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-amber-700">Alertas automáticos</p>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-amber-800">
                {alertas.map((a) => (
                  <li key={a}>{a}</li>
                ))}
              </ul>
            </div>
          </div>
        </article>

        <article className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-zinc-900">Indicadores rápidos</h2>
          <div className="mt-4 space-y-3">
            <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Adesão ao plano</p>
              <p className="mt-1 text-2xl font-black text-emerald-700">{metricas.adesao}%</p>
            </div>
            <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Engajamento</p>
              <p className="mt-1 text-2xl font-black text-cyan-700">{metricas.engajamento}%</p>
            </div>
            <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Histórico recente</p>
              <ul className="mt-2 space-y-1 text-sm text-zinc-700">
                {historico.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          </div>
        </article>
      </section>
    </div>
  );
}
