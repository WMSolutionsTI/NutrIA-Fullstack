"use client";
import React, { useState } from "react";

export default function ContabilidadeAdmin() {
  // Simulação de dados financeiros
  const [financeiro, setFinanceiro] = useState({ receita: 15000, despesas: 5000, saldo: 10000 });
  const [relatorios, setRelatorios] = useState([
    "Receita março: R$ 15.000",
    "Despesas março: R$ 5.000",
    "Saldo atual: R$ 10.000"
  ]);

  // Simulação de exportação
  const exportar = () => {
    alert("Exportação de relatórios financeiros simulada!");
  };

  // Simulação de automação IA
  const automacaoIA = "IA ativa: monitora fluxo de caixa, sugere ajustes, gera relatórios e exporta dados automaticamente.";

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-green-700 dark:text-green-300 mb-8">Contabilidade Admin</h1>
        {/* Fluxo de caixa */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Fluxo de Caixa</h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
              <p className="font-bold">Receita:</p>
              <p>R$ {financeiro.receita}</p>
            </div>
            <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
              <p className="font-bold">Despesas:</p>
              <p>R$ {financeiro.despesas}</p>
            </div>
            <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
              <p className="font-bold">Saldo:</p>
              <p>R$ {financeiro.saldo}</p>
            </div>
          </div>
        </section>
        {/* Relatórios financeiros */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Relatórios Financeiros</h2>
          <ul className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
            {relatorios.map((r, idx) => <li key={idx}>{r}</li>)}
          </ul>
        </section>
        {/* Automação IA */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Automação IA</h2>
          <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
            <p>{automacaoIA}</p>
          </div>
        </section>
        {/* Exportação */}
        <section className="mb-6">
          <button onClick={exportar} className="rounded bg-green-600 hover:bg-green-700 text-white px-6 py-2 font-semibold shadow">Exportar Relatórios</button>
        </section>
      </div>
    </div>
  );
}

// Estilos básicos para inputs
// Adicione ao seu CSS global:
// .input { border-radius: 0.5rem; border: 1px solid #22c55e; padding: 0.5rem; background: #fff; color: #222; }
// .input:focus { outline: none; border-color: #22c55e; background: #f0fdf4; }