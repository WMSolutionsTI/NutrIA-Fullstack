import React, { useState } from "react";

export default function RelatoriosAnalyticsAdmin() {
  // Simulação de métricas
  const [metricas, setMetricas] = useState({ vendas: 120, receita: 15000, clientes: 420, engajamento: 88 });
  const [insights, setInsights] = useState([
    "Maior taxa de conversão: WhatsApp",
    "Clientes ativos aumentaram 12% este mês",
    "Campanha webinar gerou 30 novos assinantes"
  ]);

  // Simulação de exportação
  const exportar = () => {
    alert("Exportação de relatórios simulada!");
  };

  // Simulação de automação IA
  const automacaoIA = "IA ativa: gera insights, sugere ações, monitora métricas e exporta dados automaticamente.";

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-indigo-700 dark:text-indigo-300 mb-8">Relatórios e Analytics Admin</h1>
        {/* Gráficos e métricas */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Métricas de Uso</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
              <p className="font-bold">Vendas:</p>
              <p>{metricas.vendas}</p>
            </div>
            <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
              <p className="font-bold">Receita:</p>
              <p>R$ {metricas.receita}</p>
            </div>
            <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow col-span-2">
              <p className="font-bold">Clientes:</p>
              <p>{metricas.clientes}</p>
            </div>
            <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow col-span-2">
              <p className="font-bold">Engajamento:</p>
              <p>{metricas.engajamento}%</p>
            </div>
          </div>
        </section>
        {/* Insights de negócio */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Insights de Negócio</h2>
          <ul className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
            {insights.map((i, idx) => <li key={idx}>{i}</li>)}
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
          <button onClick={exportar} className="rounded bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 font-semibold shadow">Exportar Relatórios</button>
        </section>
      </div>
    </div>
  );
}

// Estilos básicos para inputs
// Adicione ao seu CSS global:
// .input { border-radius: 0.5rem; border: 1px solid #6366f1; padding: 0.5rem; background: #fff; color: #222; }
// .input:focus { outline: none; border-color: #6366f1; background: #eef2ff; }