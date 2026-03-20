"use client";

import React, { useState } from "react";

export default function RelatoriosMetricas() {
  // Simulação de dados
  const [metricas, setMetricas] = useState({ peso: [70, 69, 68.5], imc: [24, 23.8, 23.5], exames: ["Hemograma OK", "Ferritina baixa"], adesao: 85, engajamento: 90 });
  const [alertas, setAlertas] = useState(["Atenção: ferritina abaixo do ideal", "Meta de peso atingida!"]);
  const [historico, setHistorico] = useState(["Consulta 01/03/2026", "Exame 10/03/2026", "Plano alimentar atualizado 12/03/2026"]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 via-white to-emerald-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-blue-700 dark:text-blue-300 mb-8">Relatórios e Métricas</h1>
        {/* Dashboard geral */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Dashboard</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
              <p className="font-bold">Peso (últimos registros):</p>
              <ul>{metricas.peso.map((p, idx) => <li key={idx}>{p} kg</li>)}</ul>
            </div>
            <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
              <p className="font-bold">IMC (últimos registros):</p>
              <ul>{metricas.imc.map((i, idx) => <li key={idx}>{i}</li>)}</ul>
            </div>
            <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow col-span-2">
              <p className="font-bold">Exames:</p>
              <ul>{metricas.exames.map((e, idx) => <li key={idx}>{e}</li>)}</ul>
            </div>
          </div>
        </section>
        {/* Adesão ao plano alimentar */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Adesão ao Plano Alimentar</h2>
          <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
            <p>Adesão: <span className="font-bold">{metricas.adesao}%</span></p>
          </div>
        </section>
        {/* Engajamento e comunicação */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Engajamento</h2>
          <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
            <p>Engajamento: <span className="font-bold">{metricas.engajamento}%</span></p>
          </div>
        </section>
        {/* Alertas automáticos */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Alertas Automáticos</h2>
          <ul className="bg-blue-100 dark:bg-zinc-800 rounded p-4 shadow">
            {alertas.map((a, idx) => <li key={idx}>{a}</li>)}
          </ul>
        </section>
        {/* Histórico de métricas */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Histórico</h2>
          <ul className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
            {historico.map((h, idx) => <li key={idx}>{h}</li>)}
          </ul>
        </section>
      </div>
    </div>
  );
}

// Estilos básicos para inputs
// Adicione ao seu CSS global:
// .input { border-radius: 0.5rem; border: 1px solid #d1d5db; padding: 0.5rem; background: #fff; color: #222; }
// .input:focus { outline: none; border-color: #3b82f6; background: #f0f6ff; }